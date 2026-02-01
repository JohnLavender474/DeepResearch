import asyncio
import json
import logging
import httpx

from collections import Counter
from statistics import mean, median
from typing import Optional

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from llm.claude_client import claude_client
from model.perform_research import (
    PerformResearchInput,
    PerformResearchOutput,
)
from model.task import (
    TaskDecomposition,
    TaskResult,
    TaskEntry,
    TaskCitation,
)
from model.document_summary import DocumentSummary
from model.search_result import SearchResult
from model.semantic_search_query import (
    SemanticSearchQuery,
)
from utils.prompt_loader import load_prompt


logger = logging.getLogger(__name__)


async def _decompose_tasks(
    input_data: PerformResearchInput,
    execution_type: str
) -> TaskDecomposition:
    logger.debug(
        f"Starting task decomposition for query: " 
        f"{input_data.query}"
    )

    decomposition_prompt = load_prompt(
        f"{execution_type}_task_decomposition.md",
    )        
    
    formatted_decomposition_prompt = (
        decomposition_prompt.format(
            input_data=json.dumps(
                input_data.model_dump(),
                indent=2,
            ),
        )
    )

    decomposition = await claude_client.ainvoke(
        input=([
            SystemMessage(
                content=formatted_decomposition_prompt,
            ),
            HumanMessage(content=input_data.query),
        ]),
        output_type=TaskDecomposition,
    )
    logger.debug(
        f"Task decomposition complete. Number of tasks: " 
        f"{len(decomposition.tasks)}"
    )

    return decomposition


async def execute_tasks_in_parallel(
    input_data: PerformResearchInput,
) -> PerformResearchOutput:
    logger.debug(
        f"Starting parallel task execution for query: " 
        f"{input_data.query}"
    )

    decomposition = await _decompose_tasks(
        input_data, 
        execution_type="parallel"
    )

    task_execution_prompt = load_prompt(
        "task_execution.md",
    )

    task_coroutines = [
        _execute_task(
            task=task,
            prompt=task_execution_prompt,
            collection_name=input_data.collection_name,            
        )
        for task in decomposition.tasks
    ]

    task_entries = await asyncio.gather(
        *task_coroutines,
    )
    logger.debug(
        f"All tasks executed. Successful: " 
        f"{sum(1 for e in task_entries if e.success)}, " 
        f"Failed: {sum(1 for e in task_entries if not e.success)}"
    )

    return PerformResearchOutput(
        task_entries=task_entries,
    )


async def execute_tasks_in_sequence(
    input_data: PerformResearchInput,
) -> PerformResearchOutput:
    logger.debug(
        f"Starting sequential task execution for query: " 
        f"{input_data.query}"
    )

    decomposition = await _decompose_tasks(
        input_data, 
        execution_type="sequential"
    )

    task_execution_prompt = load_prompt(
        "task_execution.md",
    )

    task_entries: list[TaskEntry] = []
    chat_history: list[BaseMessage] = []

    for task in decomposition.tasks:
        logger.debug(
            f"Executing task sequentially with " 
            f"{len(chat_history)} messages in chat history"
        )
        task_entry = await _execute_task(
            task=task,
            chat_history=chat_history,
            prompt=task_execution_prompt,
            collection_name=input_data.collection_name,            
        )
        task_entries.append(task_entry)

        if task_entry.success:
            chat_history.append(
                HumanMessage(content=(task_entry.task))
            )
            chat_history.append(
                AIMessage(content=(task_entry.result))
            )

    logger.debug(
        f"All tasks executed sequentially. " 
        f"Successful: {sum(1 for e in task_entries if e.success)}, " 
        f"Failed: {sum(1 for e in task_entries if not e.success)}"
    )

    return PerformResearchOutput(
        task_entries=task_entries,
    )


async def _generate_search_query(
    task: str,
) -> str:
    logger.debug(f"Generating search query for task: {task}")
    search_query_prompt = load_prompt(
        "semantic_search_query.md",
    )
    formatted_search_prompt = (
        search_query_prompt.format(task=task)
    )

    search_query_response = (
        await claude_client.ainvoke(
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
    logger.debug(f"Searching documents in collection '{collection_name}' with query: {search_query}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                (
                    f"http://localhost:8000/api/embeddings/"
                    f"collections/{collection_name}/search"
                ),
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


def _format_document_context(
    search_query: str,
    documents: list[SearchResult],
    chat_history: Optional[list[BaseMessage]] = None,
) -> str:
    logger.debug(f"Formatting context for {len(documents)} documents")
    context_parts = []

    if chat_history:
        context_parts.append("## Prior Context")
        for msg in chat_history:
            if isinstance(msg, HumanMessage):
                context_parts.append(msg.content)
        context_parts.append("")

    if not documents:
        logger.debug(f"No documents found for search query: {search_query}")
        context_parts.append(
            f"No documents found for search query: {search_query}"
        )
    else:
        context_parts.append(f"Based on search results for: {search_query}")
        context_parts.append("")
        context_parts.append("Retrieved documents:")

        for i, doc in enumerate(documents, 1):
            content = doc.content_summary or doc.metadata.content
            context_parts.append(f"{i}. {content}")

    return "\n".join(context_parts)


def _extract_citations(
    collection_name: str,
    documents: list[SearchResult],
) -> list[TaskCitation]:
    logger.debug(f"Extracting citations from {len(documents)} documents")
    citations: list[TaskCitation] = []
    seen: set[tuple[str, str, int]] = set()

    for doc in documents:
        filename = doc.metadata.source_name
        chunk_index = doc.metadata.chunk_index
        content = doc.metadata.content
        score = doc.score
        content_summary = doc.content_summary

        citation_key = (collection_name, filename, chunk_index)

        if citation_key not in seen:
            citations.append(
                TaskCitation(
                    filename=filename,
                    content_summary=content_summary,
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
    # Return early if no documents to filter
    if not documents:
        return []

    # Extract all scores for statistical analysis
    scores = [doc.score for doc in documents]

    # Calculate central tendency metrics:
    # - Mean: average score, sensitive to outliers
    # - Median: middle value, robust to outliers
    # - Mode: most frequent score, indicates clustering
    score_mean = mean(scores)
    score_median = median(scores)

    # Counter finds the most common score values
    # Mode represents the "typical" score in the distribution
    score_counts = Counter(scores)
    score_mode = score_counts.most_common(1)[0][0]

    logger.debug(
        f"Score statistics - Mean: {score_mean:.4f}, "
        f"Median: {score_median:.4f}, Mode: {score_mode:.4f}"
    )

    # Dynamic threshold calculation:
    # Use the maximum of mean, median, and mode to ensure we keep
    # only the most relevant documents. This approach adapts to
    # different score distributions:
    # - If scores are normally distributed, mean ≈ median ≈ mode
    # - If scores are skewed high, mode catches the cluster of good matches
    # - If there are outlier low scores, median provides robustness
    dynamic_threshold = max(score_mean, score_median, score_mode)

    # Apply a dampening factor to avoid being too aggressive
    # This keeps documents that are within 80% of the threshold
    dampened_threshold = dynamic_threshold * 0.8

    # Ensure minimum threshold to filter out clearly irrelevant results
    min_threshold = 0.3

    final_threshold = max(dampened_threshold, min_threshold)

    logger.debug(
        f"Filtering with threshold: {final_threshold:.4f} "
        f"(dampened from {dynamic_threshold:.4f})"
    )

    # Filter documents that meet the threshold
    filtered_docs = [
        doc for doc in documents
        if doc.score >= final_threshold
    ]

    # Sort by score descending to prioritize most relevant
    filtered_docs.sort(key=lambda d: d.score, reverse=True)

    # Apply hard cap to prevent context overflow
    # even if many documents meet the threshold
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
) -> DocumentSummary:
    summarization_prompt = load_prompt("chunk_summarization.md")   

    task_input = json.dumps({
        "task": task,
        "content": content,
    })

    summary_response = await claude_client.ainvoke(
        input=[
            SystemMessage(content=summarization_prompt),
            HumanMessage(content=task_input),
        ],
        output_type=DocumentSummary,
    )

    return summary_response


async def _summarization_and_relevancy_filtering(
    task: str,
    documents: list[SearchResult],
) -> list[SearchResult]:
    logger.debug(f"Summarizing {len(documents)} documents for task: {task}")

    async def summarize_single(doc: SearchResult) -> tuple[SearchResult, bool]:
        original_content = doc.metadata.content
        summary_response = await _summarize_chunk(task, original_content)
        doc.content_summary = summary_response.summary
        return doc, summary_response.relevant

    results = await asyncio.gather(
        *[summarize_single(doc) for doc in documents]
    )

    relevant_docs = [doc for doc, is_relevant in results if is_relevant]

    logger.debug(
        f"Completed summarization. "
        f"Relevant docs: {len(relevant_docs)}"
    )
    return relevant_docs


async def _execute_task(
    task: str,
    prompt: str,
    collection_name: str,
    chat_history: Optional[list[BaseMessage]] = None,
) -> TaskEntry:
    logger.debug(f"Executing task: {task}")
    try:
        search_query = await _generate_search_query(task)
       
        documents = await _search_documents(
            collection_name,
            search_query,
        )

        filtered_documents = _filter_documents_by_score(
            documents=documents,
            max_docs=25
        )
        
        relevant_documents = await _summarization_and_relevancy_filtering(
            task,
            filtered_documents,
        )

        logger.debug(
            f"Using {len(relevant_documents)} relevant documents out of "
            f"{len(filtered_documents)} filtered documents"
        )

        citations = _extract_citations(
            collection_name,
            relevant_documents,
        )

        document_context = _format_document_context(
            search_query,
            relevant_documents,
            chat_history,
        )

        formatted_prompt = prompt.format(task=task)

        messages: list[BaseMessage] = []

        system_message_str = (
            f"{formatted_prompt}\n\n"
            f"## Document Context\n\n"
            f"{document_context}"
        )

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

        output = await claude_client.ainvoke(
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
