from fastapi import APIRouter

from model.process_selection import (
    ProcessSelectionInput,
    ProcessSelectionOutput,
)
from service.process_selection_service import (
    select_process,
)


process_selection_router = APIRouter(
    prefix="/api/graph/process-selection",
    tags=["process-selection"],
)


@process_selection_router.post(
    "/execute",
    response_model=ProcessSelectionOutput,
)
async def classify_query_endpoint(
    input_data: ProcessSelectionInput,
) -> ProcessSelectionOutput:
    output = await select_process(input_data)
    return output
