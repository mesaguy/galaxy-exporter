ARG PYTHON_VERSION
FROM $PYTHON_VERSION

# For building FastAPI
RUN apk add --no-cache gcc libffi-dev make musl-dev

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Set the default ANSIBLE_ROLE_ID to mesaguy.prometheus. This environmental
# variable can be overridden at runtime
ENV ANSIBLE_ROLE_ID=29232

# Use "--reload" for development only
#CMD ["uvicorn", "main:app", "--reload", "--host=0.0.0.0"]
CMD ["uvicorn", "main:app", "--host=0.0.0.0"]
