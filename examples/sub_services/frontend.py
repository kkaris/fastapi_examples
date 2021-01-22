"""
Serves front-end

Todo: This services provides a frontend to what was previously done in
 python script
 Consider hosting the data directory (from the subservices) here as well
 instead of calling that service (can be good to if you just want to test
 the JS approach without running all the services)
"""
import json
import logging
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from depmap_analysis.util.aws import check_existence_and_date_s3, \
    read_query_json_from_s3
from indra_network_search.net import EMPTY_RESULT
from indra_network_search.util import TEMPLATES as NETSEARCH_TEMPLATES, \
    STATIC as NETSEARCH_STATIC
from .service_util import FASTAPI_DATA_DIR

logger = logging.getLogger(__name__)

app = FastAPI()
app.mount('/static', StaticFiles(directory=NETSEARCH_STATIC), name='static')
app.mount('/data', StaticFiles(directory=FASTAPI_DATA_DIR), name='data')
templates = Jinja2Templates(directory=NETSEARCH_TEMPLATES)

NS_LIST_ = ['NAMESPACE1', 'NAMESPACE2', 'NAMESPACE3']
INDRA_DB_FROMAGENTS = 'https://db.indra.bio/statements/from_agents'


@app.get('/', response_class=HTMLResponse)
async def query_page(request: Request, query: Optional[int] = None):
    """Loads or responds to queries submitted on the query page"""
    logger.info('Got query')
    # logger.info('Incoming Args -----------')
    # logger.info(repr(request.args))

    stmt_types = ['Activation', 'Phosphorylation', '']
    has_signed_graph = False

    # Get query hash from parameters
    qh = query
    if qh:
        # Get query hash
        logger.info('Got query hash %s' % str(qh))
        old_results = check_existence_and_date_s3(qh)

        # Get result json
        res_json_key = old_results.get('result_json_key')
        results_json = read_query_json_from_s3(res_json_key) if res_json_key\
            else {}

        # Get query json
        query_json_key = old_results.get('query_json_key')
        query_json = read_query_json_from_s3(query_json_key) if \
            query_json_key else {}

        source = query_json.get('source', '')
        target = query_json.get('target', '')
    else:
        results_json = {'result': EMPTY_RESULT}
        query_json = {}
        source = ''
        target = ''
    return templates.TemplateResponse(
        'fast_api_query_template.html',
        context={
            'request': request,
            'query_hash': qh,
            'stmt_types': stmt_types,
            'node_name_spaces': list(NS_LIST_),
            'terminal_name_spaces': list(NS_LIST_),
            'has_signed_graph': has_signed_graph,
            'old_result': json.dumps(results_json),
            'old_query': json.dumps(query_json),
            'source': source,
            'target': target,
            'indra_db_url_fromagents': INDRA_DB_FROMAGENTS
        })
