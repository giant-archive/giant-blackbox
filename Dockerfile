# Container image that runs your code
FROM python:3.8.3-slim

# Setup the environment
COPY etc/requirements.txt /etc/requirements.txt
RUN pip install -r etc/requirements.txt

# Move the Python code into place
COPY src /src

# Move the Action entrypoint into place.
COPY entrypoint.sh /entrypoint.sh
RUN ["chmod", "+x", "/entrypoint.sh"]

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]

