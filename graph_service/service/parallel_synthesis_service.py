import asyncio
import json
import logging
import httpx

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from llm.claude_client import claude_client
from model.parallel_synthesis import (
    ParallelSynthesisInput,
    ParallelSynthesisOutput,
)
from model.task import (
    TaskDecomposition,
    TaskResult,
    TaskEntry,
    TaskCitation,
)
from model.search_result import SearchResult
from model.semantic_search_query import (
    SemanticSearchQuery,
)
from utils.prompt_loader import load_prompt



logger = logging.getLogger(__name__)


async def execute_parallel_synthesis(
    input_data: ParallelSynthesisInput,
) -> ParallelSynthesisOutput:
    logger.debug(f"Starting parallel synthesis for query: {input_data.query}")
    decomposition_prompt = load_prompt(
        "parallel_synthesis_decomposition.md",
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
    logger.debug(f"Task decomposition complete. Number of tasks: {len(decomposition.tasks)}")

    task_execution_prompt = load_prompt(
        "task_execution.md",
    )

    task_coroutines = [
        _execute_task(
            task,
            task_execution_prompt,            
            input_data.collection_name,
        )
        for task in decomposition.tasks
    ]

    task_entries = await asyncio.gather(
        *task_coroutines,
    )
    logger.debug(f"All tasks executed. Successful: {sum(1 for e in task_entries if e.success)}, Failed: {sum(1 for e in task_entries if not e.success)}")

    summary_prompt = load_prompt(
        "parallel_synthesis_summary.md",
    )

    summary_response = await claude_client.ainvoke(
        input=([
            SystemMessage(content=summary_prompt),
            HumanMessage(
                content=json.dumps(
                    [entry.model_dump() for entry in task_entries],
                    indent=2,
                ),
            ),
        ]),
        output_type=TaskResult,
    )

    result = summary_response.result
    logger.debug("Parallel synthesis completed successfully")

    return ParallelSynthesisOutput(
        overall_result=result,
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
                    f"http://localhost:8000/api/embedding/"
                    f"collections/{collection_name}/search"
                ),
                json={
                    "query": search_query,
                    "top_k": 5,
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
) -> str:
    logger.debug(f"Formatting context for {len(documents)} documents")    
    if not documents:
        logger.debug(f"No documents found for search query: {search_query}")
        return (
            f"No documents found for search query: "
            f"{search_query}"
        )

    context_parts = [
        f"Based on search results for: {search_query}",
        "",
        "Retrieved documents:",
    ]

    for i, doc in enumerate(documents, 1):
        content = doc.metadata.content
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

        citation_key = (collection_name, filename, chunk_index)

        if citation_key not in seen:
            citations.append(
                TaskCitation(              
                    content=content,      
                    filename=filename,
                    chunk_index=chunk_index,
                    collection_name=collection_name,
                )
            )
            seen.add(citation_key)

    logger.debug(f"Extracted {len(citations)} unique citations")
    return citations


async def _execute_task(
    task: str,
    prompt: str,    
    collection_name: str,
) -> TaskEntry:
    logger.debug(f"Executing task: {task}")
    try:
        search_query = await _generate_search_query(task)

        documents = await _search_documents(
            collection_name,
            search_query,
        )

        citations = _extract_citations(
            collection_name,
            documents,
        )

        document_context = _format_document_context(
            search_query,
            documents,
        )

        formatted_prompt = prompt.format(task=task)

        output = await claude_client.ainvoke(
            input=([
                SystemMessage(
                    content=(
                        f"{formatted_prompt}\n\n"
                        f"## Relevant Context\n\n"
                        f"{document_context}"
                    ),
                ),
                HumanMessage(content=task),
            ]),
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
