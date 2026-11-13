"""Offline MusicXML-to-WAV piano rendering using the bundled Android synth."""
from __future__ import annotations

import ctypes
import os
import tempfile
import wave
from pathlib import Path

from piano.musicxml_to_midi import parse_musicxml

SAMPLE_RATE = 44100
BLOCK_FRAMES = 4096


def _load_library():
    candidates = ["libpianosynth.so", "pianosynth"]
    last_error = None
    for candidate in candidates:
        try:
            return ctypes.CDLL(candidate)
        except OSError as exc:
            last_error = exc
    raise RuntimeError(
        "피아노 오디오 엔진(libpianosynth.so)을 찾을 수 없습니다. Android ARM64 빌드가 필요합니다."
    ) from last_error


def _configure_library(lib):
    lib.ps_create.argtypes = [ctypes.c_char_p, ctypes.c_int]
    lib.ps_create.restype = ctypes.c_void_p
    lib.ps_destroy.argtypes = [ctypes.c_void_p]
    lib.ps_note_on.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.ps_note_off.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.ps_render.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int16), ctypes.c_int]
    lib.ps_active_voices.argtypes = [ctypes.c_void_p]
    lib.ps_active_voices.restype = ctypes.c_int


def bundled_soundfont() -> Path:
    path = Path(__file__).resolve().parent / "assets" / "upright_piano_kw.sf2"
    if not path.is_file():
        raise FileNotFoundError(
            "피아노 음원 파일이 없습니다. scripts/fetch_piano_soundfont.sh를 실행한 뒤 앱을 빌드하세요."
        )
    return path


def render_musicxml_to_wav(musicxml_path, output_path=None, tempo_scale=1.0):
    """Render a score to stereo 16-bit PCM WAV entirely on the device."""
    tempo_scale = max(0.5, min(1.5, float(tempo_scale)))
    score = parse_musicxml(musicxml_path)
    tempo = score["tempo"] * tempo_scale
    beat_seconds = 60.0 / tempo
    events = []
    display_notes = []
    for note in score["notes"]:
        start = max(0.0, note["start"] * beat_seconds)
        end = max(start + 0.02, (note["start"] + note["duration"]) * beat_seconds)
        events.append((round(start * SAMPLE_RATE), 1, note["pitch"], note["velocity"]))
        events.append((round(end * SAMPLE_RATE), 0, note["pitch"], 0))
        display_notes.append({"pitch": note["pitch"], "start": start, "end": end})
    events.sort(key=lambda event: (event[0], event[1]))

    sf2 = bundled_soundfont()
    lib = _load_library()
    _configure_library(lib)
    handle = lib.ps_create(os.fsencode(sf2), SAMPLE_RATE)
    if not handle:
        raise RuntimeError("SoundFont를 열 수 없습니다. 음원 파일이 손상됐는지 확인하세요.")

    if output_path is None:
        fd, output_path = tempfile.mkstemp(prefix="andromr-piano-", suffix=".wav")
        os.close(fd)
    output_path = str(output_path)
    cursor = 0
    total_frames = max(event[0] for event in events) + int(SAMPLE_RATE * 2.2)
    pcm_type = ctypes.c_int16 * (BLOCK_FRAMES * 2)
    buffer = pcm_type()

    try:
        with wave.open(output_path, "wb") as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            for frame, action, pitch, velocity in events:
                while cursor < frame:
                    count = min(BLOCK_FRAMES, frame - cursor)
                    lib.ps_render(handle, buffer, count)
                    wav.writeframesraw(ctypes.string_at(buffer, count * 4))
                    cursor += count
                if action == 0:
                    lib.ps_note_off(handle, pitch)
                else:
                    lib.ps_note_on(handle, pitch, velocity)
            while cursor < total_frames:
                count = min(BLOCK_FRAMES, total_frames - cursor)
                lib.ps_render(handle, buffer, count)
                wav.writeframesraw(bytes(memoryview(buffer).cast("B")[:count * 4]))
                cursor += count
    finally:
        lib.ps_destroy(handle)
    return output_path, display_notes, total_frames / SAMPLE_RATE
