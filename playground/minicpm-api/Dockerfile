FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git libopenblas-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY llama.cpp /app/llama.cpp

WORKDIR /app/llama.cpp
RUN cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS
RUN cmake --build build --config Release -j$(nproc) --target llama-server

FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas0 curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/llama.cpp/build/bin/llama-server /usr/local/bin/llama-server

WORKDIR /app
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8001

ENTRYPOINT ["/app/start.sh"]