#!/bin/bash

# Navigate to the script's directory

cd "$(dirname "$0")"

# Set up logging by redirecting stdout and stderr to a log file
# and also displaying it in the console.

LOG_DIR="logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/frontend_service-${TIMESTAMP}.log"

mkdir -p ${LOG_DIR}

exec > >(tee -a "${LOG_FILE}") 2>&1

PORT=8004
if lsof -i :${PORT} > /dev/null 2>&1; then
    PID=$(lsof -i :${PORT} -t)
    echo "Port ${PORT} is in use by process(es): ${PID}"
    echo "Killing process(es)..."
    kill -9 ${PID} 2>/dev/null
fi

# Start the frontend service using npm (Vue.js)

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

echo "Starting Vue.js development server on port 8004..."

npm run dev
