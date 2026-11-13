# Andromr 피아노 자동연주 미리보기

## 앱 사용 흐름
1. Andromr에서 악보 PDF 또는 이미지를 불러옵니다.
2. 기존 OMR 변환을 완료해 MusicXML을 저장합니다.
3. 홈 화면의 악보 목록에서 해당 악보 오른쪽의 재생 아이콘을 누릅니다.
4. 피아노 재생 화면에서 재생/정지, 재생 위치 이동 및 속도(50~150%)를 조절합니다.
5. 현재/전체 재생 시간이 표시되고, 재생 중 현재 연주되는 음이 88건반에 표시됩니다.

## 오프라인 구성
- OMR은 기존 Andromr/HOMR 엔진을 사용합니다.
- MusicXML 파싱과 오디오 렌더링은 기기 내부에서 수행합니다.
- TinySoundFont 기반 네이티브 합성 엔진과 CC0 Upright Piano KW SF2를 사용합니다.
- 앱 실행 중 악보나 오디오를 외부 서버로 전송하지 않습니다. 최초 앱 설치/OMR 모델 준비 과정의 기존 다운로드는 Andromr 원본 동작을 따릅니다.

## 빌드 전 준비
SoundFont 파일은 라이선스가 명확한 FreePats CC0 음원을 빌드 시 내려받습니다.

Ubuntu:
```bash
sudo apt-get update
sudo apt-get install -y p7zip-full
bash scripts/fetch_piano_soundfont.sh
```

그 다음 Andromr의 기존 BUILDING.md에 따라 Buildozer Docker 환경에서 빌드합니다. 이 브랜치에는 TinySoundFont ARM64 로컬 recipe와 Gradle 템플릿 패치 스크립트가 추가되어 있습니다. GitHub Actions의 **Android piano player build** 워크플로도 사용할 수 있습니다.

## 알려진 제한
- 현재 MusicXML 파서는 score-partwise 형식과 일반적인 음표/쉼표/화음/박자 정보를 대상으로 합니다.
- 반복기호, D.C./D.S., 페달, 꾸밈음 및 tie 연결음 병합은 아직 처리하지 않습니다.
- 속도 변경 시 WAV를 다시 생성하므로 곡이 길면 준비 시간이 발생합니다. 슬라이더 조작을 마친 뒤 0.45초 후 한 번만 다시 렌더링합니다.
- 실제 Android 기기에서 오디오 지연, 메모리 사용량, SoundLoader 호환성을 검증해야 합니다.
- 88건반 표시는 재생 위치에 맞춰 갱신하지만, 악보 화면과의 동시 스크롤/음표 강조는 아직 없습니다.

## 라이선스
- TinySoundFont: MIT
- Upright Piano KW: CC0 1.0
- Andromr: AGPL-3.0
