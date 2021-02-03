echo "Starting frontend service"
export WORKER_ROLE=FRONTEND
uvicorn sub_services.frontend:app --port "$FRONTEND_PORT" > access_frontend.log &

