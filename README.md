# Custom Faster Whisper RunPod Worker

This worker returns JSON-serializable results to avoid RunPod `job-done` 400 errors.

## Build and Push

```bash
docker build -t <your-registry>/faster-whisper-worker:latest .
docker push <your-registry>/faster-whisper-worker:latest
```

## RunPod Serverless Endpoint

1. Create a new Serverless endpoint.
2. Use your custom image: `<your-registry>/faster-whisper-worker:latest`.
3. Set environment variables (optional):
   - `WHISPER_MODEL=large-v3`
   - `WHISPER_DEVICE=cuda`
   - `WHISPER_COMPUTE_TYPE=float16`
   - `WHISPER_MODEL_ALLOWLIST=tiny,base,small,medium,large-v3`
   - `WHISPER_MODEL_CACHE_LIMIT=1`

## Input Example

```json
{
  "input": {
    "audio_url": "https://example.com/audio.mp3",
    "model": "large-v3",
    "language": null,
    "enable_vad": false,
    "word_timestamps": false,
    "transcription": "plain_text",
    "include_segments": false
  }
}
```

## Output Example

```json
{
  "text": "Hello world",
  "transcription": "Hello world",
  "language": "en",
  "duration": 12.34,
  "model": "large-v3",
  "segments": [
    { "start": 0.1, "end": 1.2, "text": "Hello world" }
  ]
}
```
