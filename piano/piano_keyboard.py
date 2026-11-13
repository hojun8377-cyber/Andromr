"""Small Kivy widget for highlighting notes on an 88-key piano."""
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget

WHITE_PITCH_CLASSES = {0, 2, 4, 5, 7, 9, 11}


class PianoKeyboard(Widget):
    """Draw A0-C8 and highlight MIDI note numbers supplied by the player."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_notes = set()
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def set_active_notes(self, notes):
        self.active_notes = {int(note) for note in notes if 21 <= int(note) <= 108}
        self.redraw()

    def redraw(self, *_):
        self.canvas.clear()
        x0, y0 = self.pos
        width, height = self.size
        if width <= 0 or height <= 0:
            return
        white_notes = [note for note in range(21, 109) if note % 12 in WHITE_PITCH_CLASSES]
        key_width = width / len(white_notes)
        white_index = {note: index for index, note in enumerate(white_notes)}
        with self.canvas:
            for index, note in enumerate(white_notes):
                Color(0.96, 0.96, 0.94, 1)
                Rectangle(pos=(x0 + index * key_width, y0), size=(key_width, height))
                Color(0.12, 0.12, 0.12, 1)
                Line(rectangle=(x0 + index * key_width, y0, key_width, height), width=1)
            for note in range(22, 109):
                if note % 12 in WHITE_PITCH_CLASSES:
                    continue
                preceding = [key for key in white_notes if key < note]
                if preceding:
                    index = white_index[preceding[-1]]
                    x = x0 + (index + 1) * key_width - key_width * 0.31
                    Color(0.07, 0.07, 0.08, 1)
                    Rectangle(pos=(x, y0 + height * 0.42), size=(key_width * 0.62, height * 0.58))
            for note in self.active_notes:
                if note in white_index:
                    index = white_index[note]
                    Color(0.18, 0.62, 0.94, 0.8)
                    Rectangle(pos=(x0 + index * key_width + 1, y0 + 1), size=(key_width - 2, height - 2))
                else:
                    preceding = [key for key in white_notes if key < note]
                    if preceding:
                        index = white_index[preceding[-1]]
                        x = x0 + (index + 1) * key_width - key_width * 0.31
                        Color(0.18, 0.62, 0.94, 0.9)
                        Rectangle(pos=(x, y0 + height * 0.42), size=(key_width * 0.62, height * 0.58))
