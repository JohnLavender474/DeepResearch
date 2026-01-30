#!/bin/bash

# Start Qdrant only if not already running
if ! docker ps --format '{{.Names}}' | grep -q '^qdrant$'; then
    echo "Starting Qdrant..."
    docker run -d --name qdrant -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
else
    echo "Qdrant is already running. (If not running on port 6333, please stop the existing container and restart this script.)"
fi

# Start PostgreSQL
echo "Starting database service..."
(cd database_service && bash run.sh)

# Remove old virtual environment
rm -rf venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up trap to clean up on exit
cleanup() {
    echo "Shutting down services..."
    kill $embedding_pid $backend_pid 2>/dev/null
    wait $embedding_pid $backend_pid 2>/dev/null
}

trap cleanup EXIT

# Start all services
echo "Starting embedding service on port 8000..."
(cd embedding_service && bash run.sh) &
embedding_pid=$!

echo "Starting graph service on port 8001..."
(cd graph_service && bash run.sh) &
backend_pid=$!

# Keep processes running
wait
