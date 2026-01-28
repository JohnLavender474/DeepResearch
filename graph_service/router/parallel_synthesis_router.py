from fastapi import APIRouter

from model.parallel_synthesis import (
    ParallelSynthesisInput,
    ParallelSynthesisOutput,
)
from service.parallel_synthesis_service import (
    execute_parallel_synthesis,
)


router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.post(
    "/parallel-synthesis/execute",
    response_model=ParallelSynthesisOutput,
)
async def parallel_synthesis_execute(
    input_data: ParallelSynthesisInput,
) -> ParallelSynthesisOutput:
    return await execute_parallel_synthesis(input_data)
