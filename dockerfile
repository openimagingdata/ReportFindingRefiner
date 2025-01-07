# First stage - Python with UV
FROM python:3.11-slim as python-base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Second stage - Final image
FROM python:3.11-slim
COPY --from=python-base /bin/uv /bin/uv
COPY --from=python-base /bin/uvx /bin/uvx

# Install curl and Ollama
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -L https://ollama.ai/install.sh | sh

# Copy the project into the image
ADD . /app
WORKDIR /app
RUN uv sync --frozen

# Make the startup script executable
RUN chmod +x pull-llama3.sh

# Start Ollama service and run test script
CMD ["/bin/sh", "-c", "./pull-llama3.sh"]