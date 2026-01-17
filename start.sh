#!/bin/bash
set -e

echo "========================================"
echo "Container starting..."
echo "Date: $(date)"
echo "Python: $(python --version)"
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "GPU: $(python -c 'import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")')"
echo "========================================"

echo "Starting handler.py..."
exec python -u handler.py
