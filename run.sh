#!/bin/bash

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
    kill $database_pid $storage_pid $embedding_pid $backend_pid
    wait $database_pid $storage_pid $embedding_pid $backend_pid 2>/dev/null
}

trap cleanup EXIT INT TERM

# Start all services

echo "Starting database service..."
(cd database_service && bash run.sh) &
database_pid=$!

echo "Starting storage service on port 8002..."
(cd storage_service && bash run.sh) &
storage_pid=$!

echo "Starting embedding service on port 8000..."
(cd embedding_service && bash run.sh) &
embedding_pid=$!

echo "Starting graph service..."
(cd graph_service && bash run.sh) &
backend_pid=$!

echo "All services started."

# Keep processes running

wait
