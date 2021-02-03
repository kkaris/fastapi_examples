# FastAPI examples
Assembles multiple FastAPI examples in one place

## Examples ToDo

- [x] When to do async endpoints and functions and when not to (see 
      `examples/to_async_or_not_to_async/async_vs_sync.py`)
- [x] Background tasks (see `examples/http_accepted/main.py`, 
      `examples/background_tasks/background.py`, )
- [x] Static file hosting (e.g. json files) (see 
      `examples/static_files/static_file_hosting.py`,
      `examples/http_accepted/main.py`)
- [x] How to separate out parameters in endpoint vs query vs json (see 
      `examples/request_mixing/mix_path_query_body.py`)
- [x] Dependency injection (see `examples/background_tasks/background.py`, 
      `examples/dependency_injection/dependency_injection.py`)
- [x] Separate service into sub-services (see `examples/sub_services`)
- [ ] 202-redirect + work in background (see `examples/http_accepted/main.py`)
- [x] async file io using [aiofiles](https://github.com/Tinche/aiofiles) 
      (used in `examples/to_async_or_not_to_async/async_vs_sync.py`)
- [ ] async requests using [aiohttp](https://github.com/aio-libs/aiohttp)
- [ ] Proper use of Pydantic BaseModel (see `examples/pydantic_basemodel`)
- [ ]
