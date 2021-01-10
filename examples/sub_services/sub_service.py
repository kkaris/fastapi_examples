"""
Handles some requests from the main api
Requests that could take a long time (like weighted path searches) are done
as background tasks

Run this as a server using uvicorn with:
> uvicorn sub_services.sub_service:app --reload
"""
import asyncio
from time import sleep
from depmap_analysis.util.io_functions import file_opener
from depmap_analysis.network_functions.indra_network import IndraNetwork
from typing import Union, Optional
from numpy.random import exponential as rnd_exp
from networkx import DiGraph, MultiGraph
from logging import getLogger
from fastapi import BackgroundTasks, FastAPI, status as http_status
from . import *

app = FastAPI()
network_search_api: Optional[IndraNetwork] = None

logger = getLogger(__name__)

# Initialize with 'booting' before we're done loading stuff
STATUS: ServiceStatus = ServiceStatus(service_type=WORKER_ROLE,
                                      status='booting',
                                      graph_stats={})

# edge1: Edge = Edge(hashes=[123456789, 987654321],
#                    sources={'reach': 5, 'xdd': 3, 'tas': 2})
# edge2: Edge = Edge(hashes=[-123456789, -987654321],
#                    sources={'sparser': 5, 'tas': 3})
# edge3: Edge = Edge(hashes=[-192837465, 9081726354],
#                    sources={'tas': 1, 'drugbank': 1})


def handle_query(nsq: NetworkSearchQuery, job_status: JobStatus):
    """Respond to search query from client"""
    logger.info(f'Working on query {nsq.get_hash()}')

    # Update job status to 'working'
    logger.info(f'Updating {nsq.get_hash()} to working')
    job_status.status = 'working'
    upload_json(job_status)

    # pr = PathResult(one_edge=[edge1], two_edge=[edge2, edge3])
    # st = [edge1, edge2]
    # qr = QueryResult(forward_paths=pr, shared_targets=st)
    sr: SearchResults = network_search_api.handle_query(**nsq.dict())
    qrm: QueryResult = QueryResult(
        result=sr,
        path_hashes=sr.paths_by_node_count.path_hashes
    )
    qrm.query_hash = nsq.get_hash()
    qrm.fname = f'{nsq.get_hash()}_result.json'

    # Simulate work that often takes a couple of seconds or less,
    # but sometimes takes a lot longer
    # sleep_time = rnd_exp(scale=7)
    # sleep(sleep_time)
    logger.info(f'Finished query {nsq.get_hash()}')

    # Upload results
    upload_json(qrm)

    # Update job status
    logger.info(f'Updating {nsq.get_hash()} to done')
    job_status.status = 'done'
    upload_json(job_status)


@app.get('/health', response_model=ServiceStatus)
async def health():
    """Health endpoint"""
    return STATUS


# This is where to make the decision if we should run network search in the
# background or if we should run a blocking query
# Try background for now
@app.post('/query',
          status_code=http_status.HTTP_202_ACCEPTED,
          response_model=JobStatus)
async def query(search_query: NetworkSearchQuery,
                bgt: BackgroundTasks):
    """Runs a query and uploads status and potential results"""
    logger.info(f'Handling query {search_query.get_hash()}')
    meta_name = f'{search_query.get_hash()}_meta.json'
    meta_loc = f'/data/{meta_name}'
    job_status = JobStatus(id=search_query.get_hash(),
                           status='pending',
                           fname=meta_name,
                           location=meta_loc)
    logger.info(f'Updating {search_query.get_hash()} to pending')
    bgt.add_task(upload_json, job_status)
    bgt.add_task(handle_query, search_query, job_status)
    return job_status


# Change to 'online' after everything is loaded
# asyncio.sleep(5)  # Simulate loading something <- not allowed, can't await
# outside async function
if WORKER_ROLE == 'UNSIGNED':
    logger.info('Assuming role as unsigned worker')
    indra_graph = file_opener(FILES['dir_graph']) if FILES['dir_graph'] else\
        None
    if isinstance(indra_graph, (DiGraph, MultiGraph)):
        STATUS.graph_stats['unsigned_edges'] = len(indra_graph.edges)
        STATUS.graph_stats['unsigned_nodes'] = len(indra_graph.nodes)
        network_search_api = IndraNetwork(indra_dir_graph=indra_graph)
elif WORKER_ROLE == 'SIGNED':
    logger.info('Assuming role as signed worker')
    indra_seg = file_opener(FILES['sign_edge_graph']) if FILES[
        'sign_edge_graph'] else None
    if isinstance(indra_seg, (DiGraph, MultiGraph)):
        STATUS.graph_stats['signed_edge_edges'] = len(indra_seg.edges)
        STATUS.graph_stats['signed_edge_nodes'] = len(indra_seg.nodes)
    indra_sng = file_opener(FILES['sign_node_graph']) if indra_seg and \
        FILES['sign_node_graph'] else None
    if isinstance(indra_sng, (DiGraph, MultiGraph)):
        STATUS.graph_stats['signed_node_edges'] = len(indra_sng.edges)
        STATUS.graph_stats['signed_node_nodes'] = len(indra_sng.nodes)
        network_search_api = IndraNetwork(indra_sign_edge_graph=indra_seg,
                                          indra_sign_node_graph=indra_sng)
else:
    logger.warning('No worker role assigned, not loading graph')
    network_search_api = IndraNetwork()
network_search_api.verbose = 2
logger.info('Finished loading graphs, ready for work')
STATUS.status = 'online'
