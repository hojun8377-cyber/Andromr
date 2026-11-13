"""Pure playback timeline helpers shared by the Kivy player and unit tests."""

from __future__ import annotations

PROGRESS_MAX = 1000


def clamp_tempo_scale(value: float) -> float:
    return max(0.5, min(1.5, float(value)))


def position_from_progress(value: float, duration: float) -> float:
    if duration <= 0:
        return 0.0
    ratio = max(0.0, min(float(PROGRESS_MAX), float(value))) / PROGRESS_MAX
    return ratio * duration


def progress_from_position(position: float, duration: float) -> int:
    if duration <= 0:
        return 0
    ratio = max(0.0, min(float(duration), float(position))) / duration
    return round(ratio * PROGRESS_MAX)


def active_pitches_at(notes: list[dict], position: float) -> list[int]:
    """Return every pitch sounding at the given playback position."""
    return sorted({
        int(note["pitch"])
        for note in notes
        if float(note["start"]) <= position < float(note["end"])
    })


def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"
