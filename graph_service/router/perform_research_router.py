from fastapi import APIRouter

from model.perform_research import (
    PerformResearchInput,
    PerformResearchOutput,
)
from service.perform_research_service import (
    execute_tasks_in_parallel,
    execute_tasks_in_sequence,
)


router = APIRouter(prefix="/api/graph/perform_research", tags=["graph"])


@router.post(
    "/parallel/execute",
    response_model=PerformResearchOutput,
)
async def parallel_tasks_execute(
    input_data: PerformResearchInput,
) -> PerformResearchOutput:
    return await execute_tasks_in_parallel(input_data)


@router.post(
    "/sequential/execute",
    response_model=PerformResearchOutput,
)
async def sequential_tasks_execute(
    input_data: PerformResearchInput,
) -> PerformResearchOutput:
    return await execute_tasks_in_sequence(input_data)

