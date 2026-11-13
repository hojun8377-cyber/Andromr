# Andromr 피아노 자동연주 개발 기록

## 현재 반영 단계

- Andromr의 기존 OMR 엔진은 그대로 유지합니다. PDF/사진 인식 결과인 MusicXML을 입력으로 사용합니다.
- `piano/musicxml_to_midi.py`: MusicXML(score-partwise)의 음표, 박자 위치, 길이, 템포를 읽고 표준 MIDI 파일로 변환합니다.
- `piano/piano_keyboard.py`: 88건반(A0-C8)을 표시하고 MIDI 음표 번호에 맞춰 건반을 강조하는 Kivy 위젯입니다.
- 두 모듈은 오프라인 동작을 전제로 하며 외부 서버를 호출하지 않습니다.

## 아직 구현되지 않은 항목

1. Andromr 결과 목록에서 MusicXML을 선택해 플레이어 화면으로 이동
2. MIDI 이벤트를 오디오 엔진으로 전달하는 재생/일시정지/정지 기능
3. 재생 위치와 88건반 하이라이트 동기화
4. 템포 조절 및 구간 반복
5. 고음질 피아노 음원(SoundFont) 포함 및 Android ARM64 빌드 검증

## 오디오 엔진 결정 사항

현재 단계에는 음질을 낮추는 임시 사인파 합성기를 넣지 않았습니다. 실제 피아노 음색을 위해 Android ARM64에서 동작하는 FluidSynth 계열 엔진과 적절한 라이선스의 SoundFont를 검증한 뒤 추가해야 합니다. SoundFont 용량과 라이선스, APK 크기를 확인하기 전에는 고음질 재생이 구현됐다고 간주하지 않습니다.

## MusicXML 파서 범위

현재 지원: 여러 파트, divisions 변경, backup/forward, 쉼표, 화음, 음높이 alteration, sound/per-minute 템포.

현재 미지원: 반복기호 확장, D.C./D.S., pedal, articulation, tie 연결음 병합. 복잡한 악보는 MIDI 변환 결과를 별도로 검증해야 합니다.

## 라이선스

Andromr 원본은 AGPL-3.0입니다. 이 저장소에서 수정본을 배포하거나 네트워크로 제공할 때는 AGPL-3.0 의무와 포함된 제3자 라이선스를 확인해야 합니다.
