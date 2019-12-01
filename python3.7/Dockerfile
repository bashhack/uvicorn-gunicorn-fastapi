FROM bashhack/uvicorn-gunicorn:python3.7

LABEL maintainer="Marc Laughton (bashhack) - <info@marclaughton.com>"

# -- Adding Pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --deploy --system

COPY app /app
