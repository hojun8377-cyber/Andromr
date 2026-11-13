from pathlib import Path

common = Path(".buildozer/android/platform/python-for-android/pythonforandroid/bootstraps/common/build/templates/build.tmpl.gradle")
sdl = Path(".buildozer/android/platform/python-for-android/pythonforandroid/bootstraps/sdl_common/build/templates/build.tmpl.gradle")

if common.exists():
    text = common.read_text()
    line = "        ndk { abiFilters 'arm64-v8a' }"
    if line not in text and "defaultConfig {" in text:
        text = text.replace("defaultConfig {", "defaultConfig {\n" + line, 1)
        common.write_text(text)

if sdl.exists():
    text = sdl.read_text()
    attribute = 'android:enableOnBackInvokedCallback="false"'
    if attribute not in text and "<application" in text:
        text = text.replace("<application", "<application " + attribute, 1)
        sdl.write_text(text)
