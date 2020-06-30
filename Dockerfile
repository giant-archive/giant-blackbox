# Container image that runs your code
FROM python:3.8.3-slim

# Setup the environment
RUN pip install poetry==1.0.9
COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

# Move the Python code into place
COPY src /src

# Move the Action entrypoint into place.
COPY entrypoint.sh /entrypoint.sh
RUN ["chmod", "+x", "/entrypoint.sh"]

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]

