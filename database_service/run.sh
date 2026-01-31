#!/bin/bash

# Set up logging by redirecting stdout and stderr to a log file
# and also displaying it in the console.

LOG_DIR="logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/database_service-${TIMESTAMP}.log"

mkdir -p ${LOG_DIR}

exec > >(tee -a "${LOG_FILE}") 2>&1

PORT=8003
if lsof -i :${PORT} > /dev/null 2>&1; then
    PID=$(lsof -i :${PORT} -t)
    echo "Port ${PORT} is in use by process(es): ${PID}"
    echo "Killing process(es)..."
    kill -9 ${PID} 2>/dev/null
fi

# Check if PostgreSQL Docker container is running; if not, start it.

CONTAINER_NAME="deepresearch_postgres_db"
POSTGRES_USER="${POSTGRES_USER:-root}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-password}"
POSTGRES_DB="${POSTGRES_DB:-deepresearch}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "Starting existing PostgreSQL container..."
        docker start ${CONTAINER_NAME}
    else
        echo "Creating and starting PostgreSQL container..."
        docker run -d --name ${CONTAINER_NAME} \
            -p ${POSTGRES_PORT}:5432 \
            -e POSTGRES_USER=${POSTGRES_USER} \
            -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -e POSTGRES_DB=${POSTGRES_DB} \
            -v postgres_data:/var/lib/postgresql/data \
            postgres:16
    fi
else
    echo "PostgreSQL is already running."
fi

echo "Waiting for PostgreSQL to be ready..."

until docker exec ${CONTAINER_NAME} pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1; do
    sleep 1
done

echo "PostgreSQL started on port ${POSTGRES_PORT}."

# Start the database service using Uvicorn

echo "Starting database service on port 8003..."

cd "$(dirname "$0")"

python -m uvicorn app:app --host 0.0.0.0 --port 8003 --reload
