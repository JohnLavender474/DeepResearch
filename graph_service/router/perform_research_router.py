from fastapi import APIRouter

from model.perform_research import (
    PerformResearchInput,
    PerformResearchOutput,
)
from service.perform_research_service import (
    execute_tasks_in_parallel,
    execute_tasks_in_sequence,
)
from llm.llm_factory import get_llm


router = APIRouter(prefix="/api/graph/perform_research", tags=["graph"])


@router.post(
    "/parallel/execute",
    response_model=PerformResearchOutput,
)
async def parallel_tasks_execute(
    input_data: PerformResearchInput,
    llm_model: str = "claude",
) -> PerformResearchOutput:
    llm_client = get_llm(model_selection=llm_model)
    
    return await execute_tasks_in_parallel(
        input_data,
        llm_client=llm_client,
    )


@router.post(
    "/sequential/execute",
    response_model=PerformResearchOutput,
)
async def sequential_tasks_execute(
    input_data: PerformResearchInput,
    llm_model: str = "claude",
) -> PerformResearchOutput:
    llm_client = get_llm(model_selection=llm_model)
    
    return await execute_tasks_in_sequence(
        input_data,
        llm_client=llm_client,
    )

