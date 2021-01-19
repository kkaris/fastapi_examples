# Set env
export DATA_DIR=/home/klas/repos/fastapi_test/examples/data/
export MAIN_PORT=8000
export SIGNED_PORT=8001
export UNSIGNED_PORT=8002
export GRAPH_DIR=/home/klas/repos/depmap_analysis/indra_depmap_service/_cache/

# Start workers (are they running in separate processes??)
./start_unsigned.sh &
./start_signed.sh &
./start_public_api.sh &
