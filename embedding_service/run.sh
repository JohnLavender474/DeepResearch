#!/bin/bash

# Set up logging by redirecting stdout and stderr to a log file
# and also displaying it in the console.

LOG_DIR="logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/embedding_service-${TIMESTAMP}.log"

mkdir -p ${LOG_DIR}

exec > >(tee -a "${LOG_FILE}") 2>&1

# Check if configured port is in use and kill the process if it is

PORT=8004
if lsof -i :${PORT} > /dev/null 2>&1; then
    PID=$(lsof -i :${PORT} -t)
    echo "Port ${PORT} is in use by process(es): ${PID}"
    echo "Killing process(es)..."
    kill -9 ${PID} 2>/dev/null
fi

# Check if Qdrant Docker container is running; if not, start it.

CONTAINER_NAME="deepresearch_qdrant_db"

running_containers=$(docker ps --format '{{.Names}}')
all_containers=$(docker ps -a --format '{{.Names}}')

container_is_running=$(echo "$running_containers" | grep -q "^${CONTAINER_NAME}$" && echo true || echo false)

if [ "$container_is_running" = false ]; then
    container_exists=$(echo "$all_containers" | grep -q "^${CONTAINER_NAME}$" && echo true || echo false)

    if [ "$container_exists" = true ]; then
        echo "Restarting existing Qdrant container..."
        docker start ${CONTAINER_NAME}
    else
        echo "Creating and starting Qdrant container..."
        docker run -d --name ${CONTAINER_NAME} -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
    fi

    echo "Qdrant service started on port 6333."
else
    echo "Qdrant is already started and running."
fi

# Start the embedding service using Uvicorn

python -m uvicorn app:app --host 0.0.0.0 --port ${PORT} --reload

echo "Embedding service started on port ${PORT}."