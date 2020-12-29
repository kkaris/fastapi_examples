import logging
from os import environ
from pathlib import Path

logger = logging.getLogger(__name__)

# Set data directory
if environ.get('DATA_DIR'):
    DATA_DIR = Path(environ['DATA_DIR']).absolute()
else:
    HERE = Path(__file__).parent.absolute()  # This dir
    DATA_DIR = HERE.parent.joinpath('data')  # Directory in parent dir

if not DATA_DIR.is_dir():
    logger.info(f'Data dir {DATA_DIR} does not exist, creating...')
    DATA_DIR.mkdir(parents=True)

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
