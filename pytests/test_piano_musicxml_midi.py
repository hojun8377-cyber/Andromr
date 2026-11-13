import tempfile
import unittest
from pathlib import Path

from piano.musicxml_to_midi import convert_file, parse_musicxml


SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
  <part-list><score-part id="P1"><part-name>Piano</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>1</divisions></attributes>
      <direction><sound tempo="120"/></direction>
      <note><pitch><step>C</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
      <note><pitch><step>E</step><octave>4</octave></pitch><duration>1</duration><type>quarter</type></note>
      <note><pitch><step>G</step><octave>4</octave></pitch><duration>2</duration><type>half</type></note>
    </measure>
  </part>
</score-partwise>
"""


class MusicXmlMidiTests(unittest.TestCase):
    def test_parse_notes_and_tempo(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "sample.musicxml"
            source.write_text(SAMPLE, encoding="utf-8")
            score = parse_musicxml(source)
        self.assertEqual(score["tempo"], 120.0)
        self.assertEqual([n["pitch"] for n in score["notes"]], [60, 64, 67])
        self.assertEqual([n["start"] for n in score["notes"]], [0.0, 1.0, 2.0])

    def test_write_midi_header(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "sample.musicxml"
            target = Path(folder) / "sample.mid"
            source.write_text(SAMPLE, encoding="utf-8")
            convert_file(source, target)
            payload = target.read_bytes()
        self.assertTrue(payload.startswith(b"MThd"))
        self.assertEqual(payload[8:10], b"\x00\x00")


if __name__ == "__main__":
    unittest.main()
