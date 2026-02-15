import asyncio
import json
import logging
from datetime import datetime

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from llm.llm_client import LLMClient
from model.perform_research import (
    PerformResearchInput,
    PerformResearchOutput,
)
from model.task import (
    TaskDecomposition,
    TaskEntry,
)
from model.execution_config import ExecutionConfig
from service.rag_task_service import execute_task
from utils.prompt_loader import load_prompt
from utils.copy_messages import copy_messages


logger = logging.getLogger(__name__)


async def _decompose_tasks(
    input_data: PerformResearchInput,
    execution_type: str,
    llm_client: LLMClient,
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

    decomposition = await llm_client.ainvoke(
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
    llm_client: LLMClient,
    execution_config: ExecutionConfig = ExecutionConfig.default(),
) -> PerformResearchOutput:
    logger.debug(
        f"Starting parallel task execution for query: " 
        f"{input_data.query}"
    )

    decomposition = await _decompose_tasks(
        input_data, 
        execution_type="parallel",
        llm_client=llm_client,
    )

    current_date = datetime.now().strftime("%Y-%m-%d")

    task_execution_prompt = load_prompt(
        "task_execution.md",
        args={
            "current_date": current_date,      
        },
    )

    async def _execute_task_with_message_history(
        task: str,
    ) -> TaskEntry:
        return await execute_task(
            task=task,
            prompt=task_execution_prompt,
            collection_name=input_data.collection_name,
            chat_history=copy_messages(
                input_data.chat_history
            ) if input_data.chat_history else None,
            execution_config=execution_config,
            llm_client=llm_client,
        )

    task_coroutines = [
        _execute_task_with_message_history(
            task=task,
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
    llm_client: LLMClient,
    execution_config: ExecutionConfig = ExecutionConfig.default(),
) -> PerformResearchOutput:
    logger.debug(
        f"Starting sequential task execution for query: " 
        f"{input_data.query}"
    )

    decomposition = await _decompose_tasks(
        input_data, 
        execution_type="sequential",
        llm_client=llm_client,
    )

    current_date = datetime.now().strftime("%Y-%m-%d")

    task_execution_prompt = load_prompt(
        "task_execution.md",
        args={
            "current_date": current_date,      
        },
    )

    task_entries: list[TaskEntry] = []

    chat_history: list[BaseMessage] = copy_messages(
        input_data.chat_history
    ) if input_data.chat_history else []

    for task in decomposition.tasks:
        logger.debug(
            f"Executing task sequentially with " 
            f"{len(chat_history)} messages in chat history"
        )
        task_entry = await execute_task(
            task=task,
            chat_history=chat_history,
            prompt=task_execution_prompt,
            collection_name=input_data.collection_name,
            execution_config=execution_config,
            llm_client=llm_client,
        )
        task_entries.append(task_entry)

        if task_entry.success:
            chat_history.append(
                HumanMessage(content=(task_entry.task))
            )
            chat_history.append(
                AIMessage(content=(task_entry.result))
            )
        else:
            logger.debug(
                f"Task failed: {task_entry.task}. " 
                f"Result: {task_entry.result}"
            )
            # Depending on requirements, could choose to break here or continue with next tasks
            # For now, we will continue executing remaining tasks

    logger.debug(
        f"All tasks executed sequentially. " 
        f"Successful: {sum(1 for e in task_entries if e.success)}, " 
        f"Failed: {sum(1 for e in task_entries if not e.success)}"
    )

    return PerformResearchOutput(
        task_entries=task_entries,
    )
