FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl libgomp1 ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy rizzo-flow source from parent context
COPY rizzo-flow/pyproject.toml rizzo-flow/uv.lock ./
RUN uv sync --locked --no-install-project

COPY rizzo-flow/ .
RUN uv sync --locked

EXPOSE 8017

# Entrypoint downloads model+runtime if not cached, then serves
COPY playground/rizzo-flow-api/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]