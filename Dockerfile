ARG PYTHON_VERSION
FROM $PYTHON_VERSION

WORKDIR /usr/src/app
COPY requirements.txt .

# Install compiler, tools, and libraries temporarily while building FastAPI
RUN apk add --no-cache gcc libffi-dev make musl-dev && \
    # Install 3rd party Python modules
    pip install --no-cache-dir -r requirements.txt && \
    # Remove the unneeded compiler, tools, and libraries
    apk del gcc libffi-dev make musl-dev

COPY main.py .

# Set the default ANSIBLE_ROLE_ID to mesaguy.prometheus. This environmental
# variable can be overridden at runtime
ENV ANSIBLE_ROLE_ID=29232
ENV ANSIBLE_ROLE_NAME=mesaguy.prometheus
ENV CACHE_SECONDS=900

USER nobody

CMD ["uvicorn", "main:app", "--host=0.0.0.0"]
