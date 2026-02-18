import asyncio
import json
import logging
import httpx

from collections import Counter
from statistics import mean, median
from typing import Optional

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from llm.llm_client import LLMClient
from model.task import (
    TaskResult,
    TaskEntry,
)
from model.document_summary import DocumentSummary
from model.search_result import SearchResult
from model.semantic_search_query import (
    SemanticSearchQuery,
)
from model.citation import Citation
from model.execution_config import ExecutionConfig
from utils.prompt_loader import load_prompt


logger = logging.getLogger(__name__)


async def _generate_search_query(
    task: str,
    llm_client: LLMClient,
) -> str:
    logger.debug(f"Generating search query for task: {task}")
    search_query_prompt = load_prompt(
        "semantic_search_query.md",
    )
    formatted_search_prompt = (
        search_query_prompt.format(task=task)
    )

    search_query_response = (
        await llm_client.ainvoke(
            input=[
                SystemMessage(
                    content=formatted_search_prompt,
                ),
                HumanMessage(content=task),
            ],
            output_type=SemanticSearchQuery,
        )
    )
    logger.debug(f"Generated search query: {search_query_response.query}")

    return search_query_response.query


async def _search_documents(
    collection_name: str,
    search_query: str,
) -> list[SearchResult]:
    from config import EMBEDDING_SERVICE_URL

    logger.debug(f"Searching documents in collection '{collection_name}' with query: {search_query}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{EMBEDDING_SERVICE_URL}/collections/{collection_name}/search",
                json={
                    "query": search_query,
                    "top_k": 50,
                },
            )
            response.raise_for_status()
            data = response.json()
            results_data = data.get("results", [])
            results = [SearchResult(**result) for result in results_data]
            logger.debug(f"Found {len(results)} documents")
            return results
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during document search: {e}")
        raise
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise


def _format_context(
    search_query: str,
    documents: list[SearchResult],
    chat_history: Optional[list[BaseMessage]] = None,
) -> str:
    logger.debug(f"Formatting context for {len(documents)} documents")
    context_parts = []

    if chat_history:
        context_parts.append("## Chat History Context")
        for msg in chat_history:            
            context_parts.append(f"\t{msg.type}: {msg.content}")
        
    context_parts.append("\n---\n")

    context_parts.append("## Search Query Context")
    context_parts.append(f"Search query used for retrieval: {search_query}")
    
    context_parts.append("\n---\n")

    context_parts.append("## Document Context")    
    if not documents:
        logger.warning(f"No documents found relevant to the search query")
        context_parts.append(f"No documents found for the search query")
    else:                        
        for i, doc in enumerate(documents):            
            context_parts.append(
                f"{i}. {json.dumps(doc.model_dump(), indent=2)}"
            )

    return "\n".join(context_parts)


def _extract_citations(
    collection_name: str,
    documents: list[SearchResult],
) -> list[Citation]:
    logger.debug(f"Extracting citations from {len(documents)} documents")
    citations: list[Citation] = []
    seen: set[tuple[str, str, int]] = set()

    for doc in documents:
        filename = doc.metadata.source_name
        page_number = doc.metadata.page_number or -1
        chunk_index = doc.metadata.chunk_index or -1
        content = doc.metadata.content
        score = doc.score
        content_summary = doc.content_summary

        citation_key = (collection_name, filename, chunk_index)

        if citation_key not in seen:
            citations.append(
                Citation(
                    filename=filename,
                    content_summary=content_summary,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    collection_name=collection_name,
                    score=score,
                    content=content,
                )
            )
            seen.add(citation_key)

    logger.debug(f"Extracted {len(citations)} unique citations")
    return citations


def _filter_documents_by_score(
    documents: list[SearchResult],
    max_docs: Optional[int] = None,
) -> list[SearchResult]:
    if not documents:
        return []

    scores = [doc.score for doc in documents]

    score_mean = mean(scores)
    score_median = median(scores)

    score_counts = Counter(scores)
    score_mode = score_counts.most_common(1)[0][0]

    logger.debug(
        f"Score statistics - Mean: {score_mean:.4f}, "
        f"Median: {score_median:.4f}, Mode: {score_mode:.4f}"
    )

    dynamic_threshold = max(score_mean, score_median, score_mode)
    dampened_threshold = dynamic_threshold * 0.8
    min_threshold = 0.3
    final_threshold = max(dampened_threshold, min_threshold)

    logger.debug(
        f"Filtering with threshold: {final_threshold:.4f} "
        f"(dampened from {dynamic_threshold:.4f})"
    )

    filtered_docs = [
        doc for doc in documents
        if doc.score >= final_threshold
    ]

    filtered_docs.sort(key=lambda d: d.score, reverse=True)

    if max_docs is not None:
        filtered_docs = filtered_docs[:max_docs]

    logger.debug(
        f"Filtered {len(documents)} documents to "
        f"{len(filtered_docs)} documents"
    )

    return filtered_docs


async def _summarize_chunk(
    task: str,
    content: str,
    llm_client: LLMClient,
) -> DocumentSummary:
    summarization_prompt = load_prompt("chunk_summarization.md")

    task_input = json.dumps({
        "task": task,
        "content": content,
    })

    summary_response = await llm_client.ainvoke(
        input=[
            SystemMessage(content=summarization_prompt),
            HumanMessage(content=task_input),
        ],
        output_type=DocumentSummary,
    )

    return summary_response


async def _attach_content_summary_to_doc(
    task: str,
    document: SearchResult,
    llm_client: LLMClient,
) -> SearchResult:
    try:
        logger.debug(f"Summarizing document for task: {task}")

        original_content = document.metadata.content

        summary_response = await _summarize_chunk(
            task,
            original_content,
            llm_client=llm_client,
        )

        document.content_summary = summary_response.summary
    except Exception as e:
        logger.error(f"Error summarizing document: {e}", exc_info=True)

    return document


async def execute_task(
    task: str,
    prompt: str,
    collection_name: str,
    llm_client: LLMClient,
    execution_config: ExecutionConfig = ExecutionConfig.default(),
    chat_history: Optional[list[BaseMessage]] = None,
) -> TaskEntry:
    logger.debug(f"Executing task: {task}")

    allow_general_knowledge = (
        execution_config.allow_general_knowledge
    )

    try:
        search_query = await _generate_search_query(
            task,
            llm_client=llm_client,
        )

        documents = await _search_documents(
            collection_name,
            search_query,
        )

        documents = _filter_documents_by_score(
            documents=documents,
            max_docs=25,
        )

        if documents:
            await asyncio.gather(*[
                _attach_content_summary_to_doc(
                    task,
                    doc,
                    llm_client=llm_client,
                )
                for doc in documents
            ])

            citations = _extract_citations(
                collection_name,
                documents,
            )
        else:
            logger.debug("No documents found after filtering")

            if not allow_general_knowledge:
                return TaskEntry(
                    task=task,
                    success=False,
                    result="No relevant documents found.",
                    reasoning=(
                        "The search query did not return any relevant documents "
                        "and general-knowledge fallback is disabled by config."
                    ),
                    citations=[],
                )

            citations = []

        context = _format_context(
            search_query,
            documents,
            chat_history,
        )

        formatted_prompt = prompt.format(task=task)

        messages: list[BaseMessage] = []

        system_message_str = (
            f"{formatted_prompt}\n\n"
            f"# Context\n\n"
            f"{context}"
        )

        if not documents:
            system_message_str += (
                "\n\n**IMPORTANT**: No documents were found to use as sources in the RAG index. "
                "Answer using your general knowledge and clearly indicate that "
                "no indexed sources were available."
            )

        logger.debug(f"Constructed system message for task execution:\n{system_message_str}")

        if chat_history:
            chat_history_str = "\n".join(
                f"{msg.type}: {msg.content}"
                for msg in chat_history
            )
            system_message_str += (
                "\n\n## Chat History\n\n"
                f"{chat_history_str}"
            )

        messages.append(
            SystemMessage(content=(system_message_str))
        )

        messages.append(HumanMessage(content=task))

        output = await llm_client.ainvoke(
            input=messages,
            output_type=TaskResult,
        )

        logger.debug(f"Task '{task}' completed successfully")
        return TaskEntry(
            task=task,
            success=True,
            result=output.result,
            reasoning=output.reasoning,
            citations=citations,
        )
    except Exception as e:
        logger.error(f"Task '{task}' failed with error: {e}", exc_info=True)
        return TaskEntry(
            task=task,
            success=False,
            result=str(e),
            citations=[],
        )
