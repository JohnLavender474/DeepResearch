from fastapi import APIRouter

from model.perform_research import (
    PerformResearchInput,
    PerformResearchOutput,
)
from service.perform_research_service import (
    execute_tasks_in_parallel,
)


router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.post(
    "/parallel-synthesis/execute",
    response_model=PerformResearchOutput,
)
async def parallel_synthesis_execute(
    input_data: PerformResearchInput,
) -> PerformResearchOutput:
    return await execute_tasks_in_parallel(input_data)
