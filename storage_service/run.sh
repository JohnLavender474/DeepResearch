#!/bin/bash

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

python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload

echo "Storage service started on port 8002."
