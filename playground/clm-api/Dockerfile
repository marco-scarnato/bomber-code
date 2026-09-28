FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn numpy

COPY CLM/src /app/src
COPY CLM/tools /app/tools

ENV PYTHONPATH=/app/src

EXPOSE 8700

CMD ["python", "tools/playground_mock.py", "--host", "0.0.0.0", "--port", "8700", "--cors"]