import base64
import os
import tempfile
from typing import Any, Dict, List, Optional

import requests
import runpod
from faster_whisper import WhisperModel

MODEL_NAME = os.getenv("WHISPER_MODEL", "large-v3")
DEVICE = os.getenv("WHISPER_DEVICE", "cuda")
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float16")

model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)


def _to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _download_audio(url: str) -> str:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    suffix = ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(response.content)
        return temp_file.name


def _decode_audio_base64(payload: str) -> str:
    data = base64.b64decode(payload)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(data)
        return temp_file.name


def _format_timestamp_srt(seconds: float) -> str:
    ms = int(seconds * 1000)
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    secs = ms // 1000
    ms %= 1000
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def _format_timestamp_vtt(seconds: float) -> str:
    ms = int(seconds * 1000)
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    secs = ms // 1000
    ms %= 1000
    return f"{hours:02}:{minutes:02}:{secs:02}.{ms:03}"


def _format_transcript(segments: List[Dict[str, Any]], fmt: str) -> str:
    if fmt == "formatted_text":
        return "\n".join(seg["text"] for seg in segments).strip()
    if fmt == "srt":
        lines: List[str] = []
        for idx, seg in enumerate(segments, start=1):
            start = _format_timestamp_srt(seg["start"])
            end = _format_timestamp_srt(seg["end"])
            lines.extend([str(idx), f"{start} --> {end}", seg["text"], ""])
        return "\n".join(lines).strip()
    if fmt == "vtt":
        lines = ["WEBVTT", ""]
        for seg in segments:
            start = _format_timestamp_vtt(seg["start"])
            end = _format_timestamp_vtt(seg["end"])
            lines.extend([f"{start} --> {end}", seg["text"], ""])
        return "\n".join(lines).strip()
    return " ".join(seg["text"] for seg in segments).strip()


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = event.get("input", {})
    audio_url = payload.get("audio_url") or payload.get("audio") or payload.get("audioUrl")
    audio_base64 = payload.get("audio_base64")

    if not audio_url and not audio_base64:
        return {"error": "Missing audio input"}

    transcription_format = payload.get("transcription") or "plain_text"
    include_segments = bool(payload.get("include_segments", False))

    language = payload.get("language")
    if language in ("", "auto", "null", None):
        language = None

    vad_filter = bool(payload.get("enable_vad", False) or payload.get("vad_filter", False))
    word_timestamps = bool(payload.get("word_timestamps", False))

    temperature = _to_float(payload.get("temperature"), 0.0)
    best_of = _to_int(payload.get("best_of"))
    beam_size = _to_int(payload.get("beam_size"), 5)
    patience = _to_float(payload.get("patience"))
    length_penalty = _to_float(payload.get("length_penalty"))

    audio_path = ""
    try:
        if audio_base64:
            audio_path = _decode_audio_base64(audio_base64)
        else:
            audio_path = _download_audio(audio_url)

        segments_iter, info = model.transcribe(
            audio_path,
            language=language,
            vad_filter=vad_filter,
            word_timestamps=word_timestamps,
            temperature=temperature,
            best_of=best_of,
            beam_size=beam_size,
            patience=patience,
            length_penalty=length_penalty,
        )

        segments_list: List[Dict[str, Any]] = []
        for seg in segments_iter:
            segments_list.append(
                {
                    "start": float(seg.start),
                    "end": float(seg.end),
                    "text": str(seg.text).strip(),
                }
            )

        text = _format_transcript(segments_list, "plain_text")
        formatted = _format_transcript(segments_list, transcription_format)

        result: Dict[str, Any] = {
            "text": text,
            "transcription": text,
            "language": str(info.language) if info and info.language else "unknown",
            "duration": float(info.duration) if info and info.duration else None,
        }

        if include_segments:
            result["segments"] = segments_list

        if transcription_format != "plain_text":
            result["formatted_transcription"] = formatted

        return result
    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass


runpod.serverless.start({"handler": handler})
