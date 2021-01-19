echo "Starting unsigned service"
export WORKER_ROLE=UNSIGNED
uvicorn sub_services.sub_service:app --port "$UNSIGNED_PORT" > access_unsigned.log &

