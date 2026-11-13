#include <stdlib.h>
#define TSF_IMPLEMENTATION
#include "tsf.h"

typedef struct {
    tsf *font;
    int preset;
} PianoSynth;

void *ps_create(const char *sf2_path, int sample_rate) {
    PianoSynth *s = (PianoSynth *)calloc(1, sizeof(PianoSynth));
    if (!s) return NULL;
    s->font = tsf_load_filename(sf2_path);
    if (!s->font) { free(s); return NULL; }
    s->preset = tsf_get_presetindex(s->font, 0, 0);
    if (s->preset < 0) s->preset = 0;
    tsf_set_output(s->font, TSF_STEREO_INTERLEAVED, sample_rate, -3.0f);
    tsf_set_max_voices(s->font, 256);
    return s;
}

void ps_destroy(void *handle) {
    PianoSynth *s = (PianoSynth *)handle;
    if (!s) return;
    if (s->font) tsf_close(s->font);
    free(s);
}

void ps_note_on(void *handle, int key, int velocity) {
    PianoSynth *s = (PianoSynth *)handle;
    if (!s || key < 0 || key > 127) return;
    if (velocity < 1) velocity = 1;
    if (velocity > 127) velocity = 127;
    tsf_note_on(s->font, s->preset, key, (float)velocity / 127.0f);
}

void ps_note_off(void *handle, int key) {
    PianoSynth *s = (PianoSynth *)handle;
    if (s && key >= 0 && key <= 127) tsf_note_off(s->font, s->preset, key);
}

void ps_render(void *handle, short *buffer, int frames) {
    PianoSynth *s = (PianoSynth *)handle;
    if (!s || !buffer || frames <= 0) return;
    tsf_render_short(s->font, buffer, frames, 0);
}

int ps_active_voices(void *handle) {
    PianoSynth *s = (PianoSynth *)handle;
    return s ? tsf_active_voice_count(s->font) : 0;
}
