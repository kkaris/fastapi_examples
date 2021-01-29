# Sub services example
The minimal working example for how to make the NetworkSearch API more 
efficient

## ToDos
### Bugs/fixes
- [x] No results in result json (check what comes out of the search vs the 
  model used to store the results)
- [ ] EdgeModel currently has all the statement types hard-coded

### Requirements
- [x] BaseModels (see `service_util.py`):
  - [x] NetworkSearchQuery
  - [x] Job
  - [x] JobStatus
  - [x] Result
    - [x] SubModels
    - [ ] 
  - [x] ServiceMetaData (contains info about e.g. graph type, service type 
        e.g. worker or public service)
- [x] Decide how a worker knows its identity (unsigned or signed)
- [x] Models for NetworkSearch results (try putting a result in the model)
- [ ]

### Request cycle
These todos are roughly in order
- [x] Public service (ps) gets query from Client (C)
- [x] ps sends job to correct worker (Wi)
- [x] Wi uploads meta json with `status: pending` status
- [x] Wi *either* runs job in background (*or* runs blocking job)
- [x] Wi responds with 202 to ps
- [x] ps responds with 202 to C
- [x] Wi updates meta json with `status: working`
- [x] Wi finished job, uploads result json
- [x] Wi updates meta json with `status: done`
- [ ] (**If blocking job:** respond to ps with 200)
- [x] **If background job:** no response to ps
- [ ]

### Frontend cycle
- [X] Submit request
- [ ] Disable search button
- [X] On 202 returned, get the hash, try to get results
- [ ] While 404 for results json, sleep n sec and try again
- [ ] Upon 200 for results json, fill results
- [ ] Activate search button again
- [ ]

### Stress Testing
These things need/should to be tested:
- [X] LvL1: Ping server with health requests while a query comes in
- [x] LvL2: Ping server health, do weighted search that takes long time, 
      submit second request as weighted search is ongoing
- [X] LvL3: Multiple "write" queries (i.e. mesh context queries) at the same 
      time. The expectation is that queries that change edge attributes of 
      the same edges with different weights will cause the results to 
      differ from standalone queries if they interfere. _Note: This has 
      been tested on a limited scale only and corner cases might still be 
      possible where results are affected._
- [ ]

### Frontend Testing
- [ ] Search cycle pass 
- [ ] Subsequent search after first search has finished
- [ ] User messaging works ('pending' -> 'working' -> 'done')
- [ ] Button deactivation and activation
- [ ] Download stmts
- [ ] 

## Potential stuff
These ides could be implemented now or later, but are not necessary for the 
minimal working example
- [ ] Provide job status (at least pending/working) with mongodb in order 
      to avoid excessive pinging to S3
- [ ] Use [aioboto3](https://github.com/terrycain/aioboto3) for async 
      upload of S3 files. See also 
      [aiobotocore](https://github.com/aio-libs/aiobotocore) and this
      [how-to](https://medium.com/tysonworks/concurrency-with-boto3-41cfa300aab4)
