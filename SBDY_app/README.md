# Application overview

In general, the application follows the standard path Fastapi + SQLalchemy.  
Thus, we have the main paths/routes, their data scheme, web docs, database and its models.  
The application is launched on the ASGI server, the data correctness is ensured by Pydantic.  
This application is annotated and written with in the async paradigm.  
Upon the initialization app grabs docs from the `openapi.yaml` and uses them to construct the web docs  

In short, the application receives a request, validates its data, computes the result, likely using the database and sends it back.  
For more details on how Fastapi works you can read its docs.  

## Files

- [`app.py`](app.py) - App initialization and path/route handlers
- [`crud.py`](crud.py) - Database interface for our models (CreateReadUpdateDelete)
- [`database.py`](database.py) - Database initialization and other things that help db work
- [`docs.py`](docs.py) - Pulls out the documentation from YAML and saves it in a useful way
- [`exceptions.py`](exceptions.py) - Custom exceptions and exception handlers
- [`logfile.log`](logfile.log) - Gitignored, but if the app gets run, used for the logging
- [`logger.py`](logger.py) - Setup and things needed for logging
- [`models.py`](models.py) - Database models
- [`openapi.yaml`](openapi.yaml) - YAML documentation used to generate web docs
- [`options.py`](options.py) - Changeable application-wide settings and options
- [`patches.py`](patches.py) - Monkey-patching of the libs, the first thing done in initialization
- [`py.typed`](py.typed) - Marker file for PEP 561
- [`README.md`](README.md) - This file, nice recursion `;>`
- [`run.py`](run.py) - Run the app programmatically (+debug)
- [`schemas.py`](schemas.py) - Pydantic definitions for in/out data structures
- [`sqlite.db`](sqlite.db) - Gitignored, but if the app gets run, the database is created here
- [`typedefs.py`](typedefs.py) - Type/annotation definitions for typechecking
- [`__init__.py`](__init__.py) - Package initialization
- [`__main__.py`](__main__.py) - Main command-line interface for the application
