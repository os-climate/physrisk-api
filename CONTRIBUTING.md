# Contributing to physrisk-api

## Getting started
To get set up, clone and enter the repo.
```bash
git clone https://github.com/os-climate/physrisk-api.git
cd physrisk-api
```

We recommend using [uv](https://docs.astral.sh/uv/) for maintaining a consistent working environment.
There are a number of [installation options](https://docs.astral.sh/uv/getting-started/installation/).
Note that an advantage of uv is that it can also be used to maintain python installations
(via ```uv python install```) and select the Python installation be be used for the creation of the
project's virtual environment, e.g. ```uv python pin 3.11```.

The command

```bash
uv sync
```

will create a virtual environment (.venv folder in the project
folder) and install the dependencies.
We recommend that the IDE workspace use this virtual environment when
developing.

When adding a package for use in new or improved functionality,
`uv add <package-name>`. Or, when adding something for
development, `uv add --dev <package-name>`.

## Development

Patches may be contributed via pull requests to
<https://github.com/os-climate/physrisk-api>.

All changes must pass the automated test suite, along with various static
checks. Tests and static checks can be run via the commands:

```bash
uv run pytest
```

```bash
uv run pre-commit run --all-files
```

Other checks are then run with Actions within GitHub.

Enabling automatic formatting via [pre-commit](https://pre-commit.com/)
is also recommended:
```
pre-commit install
```

## IDE set-up
For those using VS Code, configure tests ('Python: Configure Tests') to use 'pytest'
to allow running of tests within the IDE.


## Forking workflow
This is a useful clarification of the forking workflow:  
https://gist.github.com/Chaser324/ce0505fbed06b947d962  
https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow


## Running API in a Container
An image can be built and run via:
```
docker build . -t physrisk-api-image
docker run -d --name physrisk-api -p 8081:8081 physrisk-api-image
```
The API should then be accessible via:  
http://localhost:8081  
and docs via:  
http://localhost:8081/docs


An example is also given of using Docker Compose to use nginx as a reverse proxy. To run the application locally, run either of the following commands;

    docker-compose up
    # or
    podman-compose up

This is just an example and details of how the image are used in an Application are mostly beyond the scope of this repo. There is a useful introduction here:
https://fastapi.tiangolo.com/deployment/docker/.
The example 'physrisk' project is hosted on the [OpenShift](https://www.redhat.com/en/technologies/cloud-computing/openshift) Container platform. This is the 'One Load Balancer - Multiple Worker Containers' case where replication is done at the cluster level, which explains why the Dockerfile configures a single worker process.  
https://physrisk-ui-physrisk.apps.odh-cl2.apps.os-climate.org/  
https://physrisk-api-physrisk.apps.odh-cl2.apps.os-climate.org/docs


## Releasing
Currently, this image is built and released automatically to quay.io and manually (/automatically for a test instance) deployed onto OpenShift.


## Debugging (without Docker)
We recommend the approach of https://fastapi.tiangolo.com/tutorial/debugging/. That is, the ```"Python Debugger: Current File"``` option can be selected, running file ```.\src\physrisk_api\app\main.py```.

It may be desirable to debug or otherwise develop physrisk-api using a local, modified version of physrisk. In this case, the command ```uv pip install``` is useful. physrisk-api can use a cloned version of physrisk API (here in location "/Users/username/Code/physrisk") via:

```
uv pip install -e "/Users/username/Code/physrisk"
```