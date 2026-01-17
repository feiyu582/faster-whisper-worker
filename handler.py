"""
Simplified test handler - no model loading, just test if logs work
"""
import os
import sys

print("=" * 50, flush=True)
print("HELLO FROM CONTAINER!", flush=True)
print(f"Python version: {sys.version}", flush=True)
print("=" * 50, flush=True)

# Test imports one by one
print("Testing imports...", flush=True)

try:
    import runpod
    print(f"✓ runpod imported: {runpod.__version__}", flush=True)
except Exception as e:
    print(f"✗ runpod import failed: {e}", flush=True)

try:
    import torch
    print(f"✓ torch imported: {torch.__version__}", flush=True)
    print(f"  CUDA available: {torch.cuda.is_available()}", flush=True)
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}", flush=True)
except Exception as e:
    print(f"✗ torch import failed: {e}", flush=True)

try:
    from faster_whisper import WhisperModel
    print("✓ faster_whisper imported", flush=True)
except Exception as e:
    print(f"✗ faster_whisper import failed: {e}", flush=True)

print("=" * 50, flush=True)
print("All imports done, starting handler...", flush=True)


def handler(event):
    """Simple test handler - just echo back"""
    print(f"Handler called with: {event}", flush=True)
    return {
        "status": "ok",
        "message": "Test handler working!",
        "received": event.get("input", {})
    }


print("Starting RunPod serverless...", flush=True)
runpod.serverless.start({"handler": handler})
