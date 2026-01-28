import asyncio
import json
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
)
from model.semantic_search_query import (
    SemanticSearchQuery,
)
from utils.prompt_loader import load_prompt


async def execute_parallel_synthesis(
    input_data: ParallelSynthesisInput,
) -> ParallelSynthesisOutput:
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

    return ParallelSynthesisOutput(
        overall_result=result,
        task_entries=task_entries,
    )


async def _generate_search_query(
    task: str,
) -> str:
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

    return search_query_response.query


async def _search_documents(
    collection_name: str,
    search_query: str,
) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            (
                f"http://localhost:8001/api/embedding/"
                f"collections/{collection_name}/search"
            ),
            json={
                "query": search_query,
                "top_k": 5,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])


def _format_document_context(
    search_query: str,
    documents: list[dict],
) -> str:
    if not documents:
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
        payload = doc.get("payload", {})
        content = payload.get("content", "")
        context_parts.append(f"{i}. {content}")

    return "\n".join(context_parts)


async def _execute_task(
    task: str,
    prompt: str,    
    collection_name: str,
) -> TaskEntry:
    try:
        search_query = await _generate_search_query(task)

        documents = await _search_documents(
            collection_name,
            search_query,
        )

        document_context = _format_document_context(
            search_query,
            documents,
        )

        formatted_prompt = prompt.format(task=task)

        result = await claude_client.ainvoke(
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

        return TaskEntry(
            task=task,
            success=True,
            result=result.result,
            reasoning=result.reasoning,
        )
    except Exception as e:
        return TaskEntry(
            task=task,
            success=False,
            result=str(e),
        )
