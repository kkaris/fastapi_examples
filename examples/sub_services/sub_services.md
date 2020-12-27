# Sub services example
The minimal working example for how to make the NetworkSearch API more 
efficient

## ToDos
These todos are roughly in order
- [x] BaseModels (see `service_util.py`):
  - [x] NetworkSearchQuery
  - [x] Job
  - [x] JobStatus
  - [x] Result
    - [x] SubModels
    - [ ] 
  - [x] ServiceMetaData (contains info about e.g. graph type, service type 
        e.g. worker or public service)
- [ ] Public service finds the other services running
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

## Potential stuff
These ides could be implemented now or later, but are not necessary for the 
minimal working example
- [ ] Provide job status (at least pending/working) with mongodb in order 
      to avoid excessive pinging to S3
- [ ] Use [aioboto3](https://github.com/terrycain/aioboto3) for async 
      upload of S3 files. See also 
      [aiobotocore](https://github.com/aio-libs/aiobotocore) and this
      [how-to](https://medium.com/tysonworks/concurrency-with-boto3-41cfa300aab4)
