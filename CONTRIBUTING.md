# Contributing to physrisk-api

## Getting started
To get set up, clone and enter the repo.
```
git clone https://github.com/os-climate/physrisk-api.git
cd physrisk-api
```

We recommend using [pdm](https://pdm-project.org/latest/) for a
consistent working environment. Install via, e.g.:
```
pip install pdm
```
For ease of using Jupyter notebooks (e.g. in VS Code) the config can be used:
```
pdm config venv.with_pip True
```

The command:
```
pdm install
```
will create a virtual environment (typically .venv folder in the project folder) and install the dependencies.
We recommend that the IDE workspace uses this virtual environment when developing.

When adding a package for use in new or improved functionality,
`pdm add <package-name>`. Or, when adding something helpful for
testing or development, `pdm add -dG <group> <package-name>`.

## Development
Patches may be contributed via pull requests to
https://github.com/os-climate/physrisk-api.

All changes must pass the automated test suite, along with various static
checks.

Enabling automatic formatting via [pre-commit](https://pre-commit.com/)
is also recommended:
```
pre-commit install
```
or
```
pre-commit run --all-files
```

To ensure compliance with automated checks, developers may wish to run formatting and test steps which can be done via:
```
pdm run lint
pdm run test
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
