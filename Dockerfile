FROM python:3.11-slim

# OCP (the OpenCascade binding under CadQuery) links against these even headless.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglu1-mesa libxrender1 libxext6 libsm6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY spec/ spec/
COPY solution/ solution/
COPY tests/ tests/

# Build the part, then check the STEP it produced. Exit code is the verdict.
CMD ["sh", "-c", "python solution/bracket.py && pytest -q tests/"]
