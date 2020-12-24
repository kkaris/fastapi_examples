# Sub services example
The minimal working example for how to make the NetworkSearch API more 
efficient

## ToDos
These todos are roughly in order
- [X] BaseModels (see `service_util.py`):
  - [x] NetworkSearchQuery
  - [X] Job
  - [X] JobStatus
  - [X] Result
    - [X] SubModels
    - [ ] 
  - [X] ServiceMetaData (contains info about e.g. graph type, service type 
        e.g. worker or public service)
- [ ] Public service (ps) gets query from Client (C)
- [ ] ps sends job to correct worker (Wi)
- [ ] Wi uploads meta json with `status: pending` status
- [ ] Wi responds with 202 to ps
- [ ] ps responds with 202 to C
- [ ] Wi updates meta json with `status: working`
- [ ] Wi *either* runs job in background *or* runs blocking job
- [ ] Wi finished job, uploads result json
- [ ] Wi updates meta json with `status: done`
- [ ] **If blocking job:** respond to ps with 200
- [ ] **If background job:** no response to ps
- [ ]

## Potential stuff
These ides could be implemented now or later, but are not necessary for the 
minimal working example
- [ ] Provide job status (at least pending/working) with mongodb?
- [ ] Use [aioboto3](https://github.com/terrycain/aioboto3) for async 
      upload of S3 files. See also 
      [aiobotocore](https://github.com/aio-libs/aiobotocore) and this
      [how-to](https://medium.com/tysonworks/concurrency-with-boto3-41cfa300aab4)
