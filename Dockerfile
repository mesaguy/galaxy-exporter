FROM python:3.8-alpine

ENV PROJECT_DIR /usr/src/app

WORKDIR $PROJECT_DIR

COPY setup.py Pipfile.lock Pipfile ${PROJECT_DIR}/
COPY README.md .
COPY galaxy_exporter/ galaxy_exporter/

# Install compiler, tools, and libraries temporarily while building FastAPI
RUN apk add --no-cache file gcc libffi-dev make musl-dev openssl-dev && \
    # Upgrade pip
    python -m pip install --upgrade pip && \
    # Install pipenv
    pip install pipenv && \
    # Install 3rd party Python modules
    pipenv install --system --deploy && \
    # Remove the unneeded compiler, tools, and libraries
    apk del file gcc libffi-dev make musl-dev openssl-dev

USER nobody

CMD ["uvicorn", "galaxy_exporter.galaxy_exporter:app", "--host=0.0.0.0", "--port=9654"]
