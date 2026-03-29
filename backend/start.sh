#!/bin/bash

echo "Starting VeritasAI..."
echo ""

if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with your API keys."
    echo "See .env.example for reference."
    exit 1
fi

echo "Starting backend server..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 3

echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "VeritasAI is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

wait $BACKEND_PID $FRONTEND_PID
