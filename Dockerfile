FROM python:3.8-alpine

WORKDIR /usr/src/app

COPY setup.py .
COPY README.md .
COPY galaxy_exporter/ galaxy_exporter/

# Install compiler, tools, and libraries temporarily while building FastAPI
RUN apk add --no-cache file gcc libffi-dev make musl-dev openssl-dev && \
    # Install 3rd party Python modules
    ./setup.py install && \
    # Remove the unneeded compiler, tools, and libraries
    apk del file gcc libffi-dev make musl-dev openssl-dev

USER nobody

CMD ["uvicorn", "galaxy_exporter.galaxy_exporter:app", "--host=0.0.0.0", "--port=9654"]
