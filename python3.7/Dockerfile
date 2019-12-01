FROM bashhack/uvicorn-gunicorn

LABEL maintainer="Marc Laughton (bashhack) - <info@marclaughton.com>"

# -- Adding Pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --deploy --system

COPY app /app
