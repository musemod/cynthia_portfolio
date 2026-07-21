FROM python:3.13.11-slim-bookworm

WORKDIR /myportfolio

# cffi has no prebuilt wheel for py3.13, so it compiles from source —
# build-essential (gcc, libc6-dev, etc.) + libffi-dev cover its build requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]

EXPOSE 5000