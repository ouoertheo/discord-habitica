
# set base image (host OS)
FROM python:3.11-alpine

ENV PROJECT_DIR /app
RUN pip install poetry

# set the working directory in the container
WORKDIR ${PROJECT_DIR}

COPY pyproject.toml ${PROJECT_DIR}/

RUN poetry install

COPY . ${PROJECT_DIR}/

CMD [ "poetry","run","python","discord_habitica.py"]
# RUN python ./discord_habitica.py



