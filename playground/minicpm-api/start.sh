#!/bin/bash
# NOTE: This file must have LF line endings to run in Linux containers.
set -e

MODEL_DIR="/app/models"
MODEL_FILE="$MODEL_DIR/MiniCPM5-2B-Q4_K_M.gguf"
THREADS=${MINICPM_THREADS:-8}
CTX_SIZE=${MINICPM_CTX_SIZE:-8192}

# Download model if not present
if [ ! -f "$MODEL_FILE" ]; then
    echo "[minicpm] Downloading MiniCPM5-2B-Q4_K_M.gguf..."
    mkdir -p "$MODEL_DIR"
    curl -L -o "$MODEL_FILE" \
        "https://huggingface.co/openbmb/MiniCPM5-2B-GGUF/resolve/main/MiniCPM5-2B-Q4_K_M.gguf"
    echo "[minicpm] Download complete."
fi

echo "[minicpm] Starting llama-server (threads=$THREADS, ctx=$CTX_SIZE)..."
exec llama-server \
    -m "$MODEL_FILE" \
    --host 0.0.0.0 \
    --port 8001 \
    -ngl 0 \
    -c "$CTX_SIZE" \
    -t "$THREADS" \
    --jinja
