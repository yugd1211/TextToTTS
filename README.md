# TextToTTS (Edge TTS 전용)

이 프로젝트는 **OpenAI 결제 없이**, **Edge TTS만 사용**해서 텍스트를 오디오(mp3)로 만듭니다.

## 사용 방법 (폰 기준)

### 방법 A: GitHub Issue (추천)
1. Issues → New issue → `TTS Capture`
2. 제목 `[tts] ...`, 본문에 텍스트 입력
3. 이슈 생성
4. 자동으로 `content/*.md` + `audio/<문서명>/` 폴더에 mp3 생성

### 방법 B: `content/`에 md 업로드
1. `web/index.html`에서 markdown 다운로드
2. `content/`에 업로드
3. GitHub Action이 mp3 생성

## 핵심 변경
- TTS 엔진: **edge-tts 고정**
- 텍스트 정리: 외부 유료 API 없이 로컬 규칙 기반 요약/정리
- OpenAI API 키 불필요

## 설정값 (선택)
워크플로 env 또는 로컬 환경변수로 조정 가능:
- `EDGE_TTS_VOICE` (기본 `ko-KR-SunHiNeural`)
- `EDGE_TTS_RATE` (기본 `+0%`)
- `EDGE_TTS_PITCH` (기본 `+0Hz`)

## 로컬 테스트
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/refine_and_save.py --title "테스트" --text "안녕하세요"
python scripts/generate_tts.py content/<생성된파일>.md
```


## 참고
- 워크플로는 빈 커밋 방지 로직이 포함되어 있습니다.
- 이슈 제목 `[tts]` 뒤 텍스트가 비어 있으면 `untitled`로 저장됩니다.


## TTS 분할 정책
- 기본 분할 길이: 약 6000자
- `## 오디오북용 스크립트` 섹션이 있으면 해당 섹션만 음성 변환
