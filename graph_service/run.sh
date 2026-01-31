# !/bin/bash

# Set up logging by redirecting stdout and stderr to a log file
# and also displaying it in the console.

LOG_DIR="logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/graph_service-${TIMESTAMP}.log"

mkdir -p ${LOG_DIR}

exec > >(tee -a "${LOG_FILE}") 2>&1

PORT=8001
if lsof -i :${PORT} > /dev/null 2>&1; then
    PID=$(lsof -i :${PORT} -t)
    echo "Port ${PORT} is in use by process(es): ${PID}"
    echo "Killing process(es)..."
    kill -9 ${PID} 2>/dev/null
fi

# Start the graph service using Uvicorn

python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload

echo "Graph service started on port 8001."