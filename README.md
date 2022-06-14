# `SBDY_app` (School of Backend Development of Yandex)

This is introductory task in the summer School of Backend Development of Yandex 2022.

```txt
 __    __                   __
/\ \  /\ \                 /\ \
\ `\`\/'/  __      ___    \_\ \     __   __  _
 `\ `\ /' /'__`\  /' _ `\  /'_` \  /'__`\/\ \/'\
   `\ \ \/\ \L\.\_/\ \/\ \/\ \L\ \/\  __/\/>  </
     \ \_\ \__/.\_\ \_\ \_\ \___,_\ \____\/\_/\_\
      \/_/\/__/\/_/\/_/\/_/\/__,_ /\/____/\//\/_/
 ______                      __
/\  _  \                    /\ \
\ \ \L\ \    ___     __     \_\ \     __    ___ ___   __  __
 \ \  __ \  /'___\ /'__`\   /'_` \  /'__`\/' __` __`\/\ \/\ \
  \ \ \/\ \/\ \__//\ \L\.\_/\ \L\ \/\  __//\ \/\ \/\ \ \ \_\ \
   \ \_\ \_\ \____\ \__/.\_\ \___,_\ \____\ \_\ \_\ \_\/`____ \
    \/_/\/_/\/____/\/__/\/_/\/__,_ /\/____/\/_/\/_/\/_/`/___/> \
                                                          /\___/
                                                          \/__/
```

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

## Help

Run

```console
$ python -m SBDY_app -h
```

to see what arguments `run`/CLI takes

## The choice of tools

### Web framework

I chose the [FastAPI](https://fastapi.tiangolo.com/) Python Web framework for handling the REST API requests.  
Among<!-- us ඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞඞ why are you reading this? render the page, it's more beautiful -->
many other nice things it's performant and asynchronous.

### ASGI server

In the role of ASGI server, I chose [uvicorn](https://www.uvicorn.org/) as it seems like the lib used inside of FastAPI.  
Also see [`Choosing the Right ASGI Server for Deploying FastAPI`](https://github.com/tiangolo/fastapi/issues/2062).

### Testing framework

[Pytest](https://docs.pytest.org/en/latest/) is my favorite testing framework for Python, it's simple and pythonic.  
In addition to this, FastAPI recommends using it, so don't mind me if I do ;)

### Parsing YAML

To import and use the given [`openapi.yaml`](SBDY_app/openapi.yaml) for additional site documentation
I used [`PyYAML`](https://pyyaml.org/).  
It seems to be the most popular library for yaml parsing in python, and I don't need anything special, so great choice!

### Parsing ISO 8601 datetime

Also I needed to restrictively parse the ISO 8601 formatted strings.  
I could not use [`pydantic`](https://pydantic-docs.helpmanual.io/)s `datetime` validator because it allows too much.  
I settled down on [`ciso8601`](https://github.com/closeio/ciso8601), it's fast and strict.
