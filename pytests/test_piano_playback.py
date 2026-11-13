import unittest

from piano.playback import (
    active_pitches_at,
    clamp_tempo_scale,
    format_time,
    position_from_progress,
    progress_from_position,
)


class PlaybackTimelineTests(unittest.TestCase):
    def test_progress_round_trip(self):
        self.assertEqual(position_from_progress(500, 120), 60)
        self.assertEqual(progress_from_position(60, 120), 500)

    def test_progress_clamps_and_handles_zero_duration(self):
        self.assertEqual(position_from_progress(-10, 30), 0)
        self.assertEqual(position_from_progress(2000, 30), 30)
        self.assertEqual(progress_from_position(10, 0), 0)

    def test_active_notes_include_chords_and_exclude_note_end(self):
        notes = [
            {"pitch": 60, "start": 0.0, "end": 1.0},
            {"pitch": 64, "start": 0.5, "end": 1.5},
            {"pitch": 67, "start": 1.0, "end": 2.0},
        ]
        self.assertEqual(active_pitches_at(notes, 0.75), [60, 64])
        self.assertEqual(active_pitches_at(notes, 1.0), [64, 67])
        self.assertEqual(active_pitches_at(notes, 2.0), [])

    def test_tempo_and_time_formatting(self):
        self.assertEqual(clamp_tempo_scale(2.0), 1.5)
        self.assertEqual(clamp_tempo_scale(0.1), 0.5)
        self.assertEqual(format_time(125.9), "02:05")


if __name__ == "__main__":
    unittest.main()
