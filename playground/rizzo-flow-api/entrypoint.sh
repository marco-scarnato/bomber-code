#!/bin/bash
# NOTE: This file must have LF line endings to run in Linux containers.
set -e

SIZE=${RIZZO_SIZE:-1.7b}
QUANT=${RIZZO_QUANT:-q4_k_m}
DEVICE=${RIZZO_DEVICE:-cpu}

echo "[rizzo-flow] Checking model (size=$SIZE, quant=$QUANT)..."
uv run rizzo download --size "$SIZE" --quant "$QUANT"

echo "[rizzo-flow] Starting server on :8017 (device=$DEVICE)..."
exec uv run rizzo serve --host 0.0.0.0 --port 8017 --device "$DEVICE" --size "$SIZE" --quant "$QUANT"
