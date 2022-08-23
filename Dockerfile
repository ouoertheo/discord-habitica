
# set base image (host OS)
FROM python:3.9

ENV PROJECT_DIR /app
RUN pip install pipenv

# set the working directory in the container
WORKDIR ${PROJECT_DIR}


COPY Pipfile Pipfile.lock ${PROJECT_DIR}/
RUN pipenv install --system --deploy

COPY . ${PROJECT_DIR}/
EXPOSE 8952

CMD [ "python", "discord_habitica.py"]
# RUN python ./discord_habitica.py



