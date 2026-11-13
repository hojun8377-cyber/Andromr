"""Convert MusicXML score-partwise documents into Standard MIDI files.

This first offline implementation intentionally supports common notation
constructs and keeps unsupported score directions explicit in the module docs.
"""
from __future__ import annotations

import struct
import xml.etree.ElementTree as ET
from pathlib import Path

STEP_TO_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _tag(element):
    return element.tag.rsplit("}", 1)[-1]


def _child(element, name):
    return next((item for item in list(element) if _tag(item) == name), None)


def _text(element, name, default=None):
    child = _child(element, name)
    return child.text.strip() if child is not None and child.text else default


def _first_tempo(root):
    for element in root.iter():
        if _tag(element) == "sound" and element.get("tempo"):
            try:
                return max(20.0, min(300.0, float(element.get("tempo"))))
            except ValueError:
                continue
    for element in root.iter():
        if _tag(element) == "per-minute" and element.text:
            try:
                return max(20.0, min(300.0, float(element.text)))
            except ValueError:
                continue
    return 120.0


def parse_musicxml(path: str | Path):
    """Return {'tempo': BPM, 'notes': [...]} from a score-partwise file.

    Note start/duration values are measured in quarter-note beats.
    Supports multiple parts, changing divisions, backup/forward, rests,
    chords and pitch alterations. Repeat navigation, D.C./D.S., pedal,
    articulations and tie consolidation are not expanded in this MVP.
    """
    root = ET.parse(str(path)).getroot()
    if _tag(root) != "score-partwise":
        raise ValueError("Only score-partwise MusicXML is currently supported.")

    notes = []
    for part_index, part in enumerate(item for item in root if _tag(item) == "part"):
        cursor = 0.0
        divisions = 1.0
        previous_onset = 0.0
        for measure in (item for item in part if _tag(item) == "measure"):
            for item in list(measure):
                tag = _tag(item)
                if tag == "attributes":
                    value = _text(item, "divisions")
                    if value:
                        divisions = max(1.0, float(value))
                elif tag in ("backup", "forward"):
                    duration = float(_text(item, "duration", "0")) / divisions
                    cursor = max(0.0, cursor - duration) if tag == "backup" else cursor + duration
                elif tag == "note":
                    duration = float(_text(item, "duration", "0")) / divisions
                    is_chord = _child(item, "chord") is not None
                    onset = previous_onset if is_chord else cursor
                    if _child(item, "rest") is None and duration > 0:
                        pitch = _child(item, "pitch")
                        if pitch is not None:
                            step = _text(pitch, "step", "C")
                            octave = int(_text(pitch, "octave", "4"))
                            alter = float(_text(pitch, "alter", "0"))
                            midi_note = round((octave + 1) * 12 + STEP_TO_SEMITONE[step] + alter)
                            notes.append({
                                "part": part_index,
                                "pitch": max(0, min(127, midi_note)),
                                "start": onset,
                                "duration": duration,
                                "velocity": 88,
                            })
                    if not is_chord:
                        previous_onset = cursor
                        cursor += duration

    if not notes:
        raise ValueError("No playable notes were found in this MusicXML file.")
    return {"tempo": _first_tempo(root), "notes": sorted(notes, key=lambda n: (n["start"], n["pitch"]))}


def _variable_length(value: int) -> bytes:
    value = max(0, int(value))
    buffer = value & 0x7F
    output = bytearray()
    while True:
        value >>= 7
        if value:
            buffer <<= 8
            buffer |= (value & 0x7F) | 0x80
        else:
            break
    while True:
        output.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            break
    return bytes(output)


def write_midi(score, output_path: str | Path, ticks_per_quarter: int = 480):
    """Write a type-0 Standard MIDI file and return its path."""
    tempo_microseconds = int(60_000_000 / score["tempo"])
    events = [(0, 0, b"\xff\x51\x03" + tempo_microseconds.to_bytes(3, "big"))]
    for note in score["notes"]:
        start = round(note["start"] * ticks_per_quarter)
        end = round((note["start"] + note["duration"]) * ticks_per_quarter)
        channel = note["part"] % 9  # avoid MIDI percussion channel 10
        events.append((start, 2, bytes((0x90 | channel, note["pitch"], note["velocity"]))))
        events.append((end, 1, bytes((0x80 | channel, note["pitch"], 0))))
    events.sort(key=lambda event: (event[0], event[1]))

    track = bytearray()
    last_tick = 0
    for tick, _, message in events:
        track.extend(_variable_length(tick - last_tick))
        track.extend(message)
        last_tick = tick
    track.extend(b"\x00\xff\x2f\x00")

    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, ticks_per_quarter)
    chunk = b"MTrk" + struct.pack(">I", len(track)) + bytes(track)
    Path(output_path).write_bytes(header + chunk)
    return str(output_path)


def convert_file(input_path: str | Path, output_path: str | Path):
    return write_midi(parse_musicxml(input_path), output_path)
