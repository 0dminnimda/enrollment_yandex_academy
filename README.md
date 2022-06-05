# `SBDY_app` (School of Backend Development of Yandex)

This is introductory task in the summer School of Backend Development of Yandex 2022.

This is the second task in the process of selection to the School of Backend Development.
And this is my take on it.

The description of the task is in the [Task.md](Task.md).

## Installation

Open console in the root folder and run

```console
$ pip install .
```

## Launch

After installation just run in the console

```console
$ python -m SBDY_app
```

or run the python code

```python
from SBDY_app import run
run()
```

<!-- Command line / `run()` arguments: -->

## The choice of tools

I chose the [FastAPI](https://fastapi.tiangolo.com/) Python Web framework for handling the REST API requests.  
Among<!-- us ඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞ why are you reading this? render the page, it's more beautiful -->
many other nice things it's performant and asynchronous.

In the role of ASGI server, I chose [Uvicorn](https://www.uvicorn.org/) as it seems like the lib used inside of FastAPI.  
Also see [`Choosing the Right ASGI Server for Deploying FastAPI`](https://github.com/tiangolo/fastapi/issues/2062).

[PyTest](https://docs.pytest.org/en/latest/) is my favorite testing framework for Python, it's simple and pythonic.  
In addition to this, FastAPI recommends using it, so don't mind me if I do ;)
