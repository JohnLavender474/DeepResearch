#!/bin/bash

# Set up logging by redirecting stdout and stderr to a log file
# and also displaying it in the console.

LOG_DIR="logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/storage_service-${TIMESTAMP}.log"

mkdir -p ${LOG_DIR}

exec > >(tee -a "${LOG_FILE}") 2>&1

PORT=8002
if lsof -i :${PORT} > /dev/null 2>&1; then
    PID=$(lsof -i :${PORT} -t)
    echo "Port ${PORT} is in use by process(es): ${PID}"
    echo "Killing process(es)..."
    kill -9 ${PID} 2>/dev/null
fi

# Check if MinIO Docker container is running; if not, start it.

CONTAINER_NAME="deepresearch_minio_db"

running_containers=$(docker ps --format '{{.Names}}')
all_containers=$(docker ps -a --format '{{.Names}}')

container_is_running=$(echo "$running_containers" | grep -q "^${CONTAINER_NAME}$" && echo true || echo false)

if [ "$container_is_running" = false ]; then
    container_exists=$(echo "$all_containers" | grep -q "^${CONTAINER_NAME}$" && echo true || echo false)

    if [ "$container_exists" = true ]; then
        echo "Starting existing MinIO container..."
        docker start ${CONTAINER_NAME}
    else
        echo "Creating and starting MinIO container..."
        docker run -d --name ${CONTAINER_NAME} \
            -p 9000:9000 \
            -p 9001:9001 \
            -e MINIO_ROOT_USER=minioadmin \
            -e MINIO_ROOT_PASSWORD=minioadmin \
            -v minio_data:/data \
            minio/minio:latest server /data --console-address ":9001"
    fi

    echo "MinIO service started on port 9000 (API) and 9001 (Console)."
else
    echo "MinIO is already started and running."
fi

# Start the storage service using Uvicorn

python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload

echo "Storage service started on port 8002."
