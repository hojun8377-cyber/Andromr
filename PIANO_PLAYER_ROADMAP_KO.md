# Andromr 피아노 자동연주 개발 기록

## 현재 반영 단계

- Andromr의 기존 OMR 엔진은 그대로 유지합니다. PDF/사진 인식 결과인 MusicXML을 입력으로 사용합니다.
- `piano/musicxml_to_midi.py`: MusicXML(score-partwise)의 음표, 박자 위치, 길이, 템포를 읽고 표준 MIDI 파일로 변환합니다.
- `piano/piano_keyboard.py`: 88건반(A0-C8)을 표시하고 MIDI 음표 번호에 맞춰 건반을 강조하는 Kivy 위젯입니다.
- `piano/playback.py`: 재생 위치와 진행률 변환, 현재 울리는 음표 계산, 템포 범위 제한 및 시간 표시를 제공하며 단위 테스트를 포함합니다.
- 플레이어 화면에 진행 위치 슬라이더와 현재/전체 재생 시간 표시를 추가했습니다.
- 템포 슬라이더 입력은 0.45초 동안 변경이 없을 때 한 번만 재렌더링하도록 지연 처리해 불필요한 백그라운드 작업을 줄입니다.
- 오디오 재생이 끝나거나 악보를 바꿀 때 임시 WAV와 오디오 객체를 정리합니다.
- 위 기능은 오프라인 동작을 전제로 하며 외부 서버를 호출하지 않습니다.
- `.github/workflows/piano-player-tests.yml`에서 문법 검사와 MusicXML/재생 타임라인 단위 테스트를 실행합니다.

## 아직 구현되지 않은 항목

1. Andromr 결과 목록에서 플레이어를 여는 실제 진입 버튼/동선의 전체 검증
2. 일시정지 후 이어 재생, 구간 반복
3. 고음질 피아노 음원(SoundFont) 렌더링 엔진의 Android ARM64 패키징
4. APK 빌드 및 Galaxy S23 실기기 검증

## 오디오 엔진 결정 사항

현재 `piano/player.py`는 `libpianosynth.so`의 C ABI(`ps_create`, `ps_note_on`, `ps_note_off`, `ps_render`, `ps_destroy`)를 호출하고 `piano/assets/upright_piano_kw.sf2`를 읽도록 작성되어 있습니다. 그러나 현재 브랜치에는 이 네이티브 라이브러리가 없고, SoundFont 다운로드 스크립트만 있습니다. 따라서 오디오 렌더링은 아직 실행 불가 상태이며, Android ARM64용 엔진 빌드/패키징이 다음 핵심 작업입니다. SoundFont는 FreePats의 Upright Piano KW를 사용하도록 설정되어 있고 해당 페이지는 CC0 라이선스를 명시합니다.

## MusicXML 파서 범위

현재 지원: 여러 파트, divisions 변경, backup/forward, 쉼표, 화음, 음높이 alteration, sound/per-minute 템포.

현재 미지원: 반복기호 확장, D.C./D.S., pedal, articulation, tie 연결음 병합. 복잡한 악보는 MIDI 변환 결과를 별도로 검증해야 합니다.

## 라이선스

Andromr 원본은 AGPL-3.0입니다. 이 저장소에서 수정본을 배포하거나 네트워크로 제공할 때는 AGPL-3.0 의무와 포함된 제3자 라이선스를 확인해야 합니다.
