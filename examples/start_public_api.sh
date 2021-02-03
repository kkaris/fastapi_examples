echo "Starting public api"
export WORKER_ROLE=PUBLIC_API
uvicorn sub_services.main_api:app --port "$MAIN_PORT" > access_public_api.log &

