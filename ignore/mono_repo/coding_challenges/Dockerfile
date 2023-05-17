# build
FROM python:3.8.3-alpine as base

# Setup environment
ENV PYTHONUNBUFFERED=1
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PIPENV_VENV_IN_PROJECT 1

WORKDIR /
COPY ./ ./app

WORKDIR /app


FROM base as dependencies

# upgrde pip and install pipenv
RUN ["sh", "-c", "/usr/local/bin/python -m pip install --upgrade pip"]
RUN ["sh", "-c", "pip install pipenv"]
# install dependancies
RUN ["sh", "-c", "pipenv lock"]
RUN ["sh", "-c", "pipenv install --system"]


FROM dependencies as development
RUN ["sh", "-c", "pipenv install --dev"]
CMD ["sh", "-c", "pipenv run flake8"]

# production
# expose image port
EXPOSE 80

# run server
# CMD ["sh", "-c", "pipenv run python app.py"]
#CMD ["sh", "-c", "ls app -a;"]
