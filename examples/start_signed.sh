echo "Starting signed service"
export WORKER_ROLE=SIGNED
uvicorn sub_services.sub_service:app --port $SIGNED_PORT > access_signed.log &

