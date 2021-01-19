import logging
from os import environ
from pathlib import Path
from .service_util import *

__all__ = ['WORKER_ROLE', 'FILES', 'upload_json', 'upload_json_async',
           'async_pickle_open', 'NetworkSearchQuery', 'Job', 'JobStatus',
           'ServiceStatus', 'Edge', 'PathResult', 'QueryResult',
           'HealthStatus', 'EMPTY_JOB_STATUS', 'StmtInfo', 'SearchResults',
           'CommonParents', 'KShortest', 'FASTAPI_DATA_DIR', 'SERVICE_URLS']

logger = logging.getLogger(__name__)

# Set service configs
try:
    WORKER_ROLE = environ['WORKER_ROLE']  # Sets the identity of the service
    assert WORKER_ROLE in {'UNSIGNED', 'SIGNED', 'PUBLIC_API'}
    public_port = environ['MAIN_PORT']
    signed_port = environ['SIGNED_PORT']
    unsigned_port = environ['UNSIGNED_PORT']
    SERVICE_URLS = {'public': f'http://127.0.0.1:{public_port}',
                    'signed': f'http://127.0.0.1:{signed_port}',
                    'unsigned': f'http://127.0.0.1:{unsigned_port}'}
    graph_dir = Path(environ['GRAPH_DIR']).absolute()
    INDRA_MDG = graph_dir.joinpath('indranet_multi_digraph_latest.pkl')
    INDRA_DG = graph_dir.joinpath('indranet_dir_graph_latest.pkl')
    INDRA_SNG = graph_dir.joinpath('indranet_sign_node_graph_latest.pkl')
    INDRA_SEG = graph_dir.joinpath('indranet_sign_edge_graph_latest.pkl')
    FILES = {
        'dir_graph': INDRA_DG.as_posix() if INDRA_DG.is_file() else None,
        # 'multi_digraph_path': INDRA_MDG_CACHE if path.isfile(INDRA_MDG_CACHE)
        # else None,
        'multi_digraph': None,
        'sign_edge_graph': INDRA_SEG.as_posix() if \
        INDRA_SEG.is_file() else None,
        'sign_node_graph': INDRA_SNG.as_posix() if \
        INDRA_SNG.is_file() else None
    }
except KeyError as err:
    raise KeyError(
        'Mandatory environment variable not set in config file'
    ) from err
