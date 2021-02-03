# Kills the services
echo 'Killing uvicorn service on port 5000'
pkill -f "sub_services.frontend:app --port 5000"
sleep 1
echo 'Killing uvicorn service on port 8002'
pkill -f "sub_services.sub_service:app --port 8002"
sleep 1
echo 'Killing uvicorn service on port 8001'
pkill -f "sub_services.sub_service:app --port 8001"
sleep 1
echo 'Killing uvicorn service on port 8000'
pkill -f "sub_services.main_api:app --port 8000"
