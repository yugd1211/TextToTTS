# TextToTTS (개인 지식 오디오북 자동화)

걷거나 뛸 때 읽기 어려운 AI 답변/메모를 **텍스트 → 오디오(mp3)** 로 자동 변환하는 개인용 프로젝트입니다.

## 1) 가장 간단한 사용법 (폰 중심)

### 방법 A: GitHub Issue로 바로 전송 (추천)
1. 폰에서 저장소 → **Issues** → **New issue**
2. 템플릿 `TTS Capture` 선택
3. 제목은 `[tts] ...` 유지, 본문에 텍스트 붙여넣기
4. 이슈 생성하면 액션이 자동으로:
   - 텍스트를 오디오북용으로 정리해 `content/*.md` 저장
   - TTS 생성해 `audio/*.mp3` 저장
   - 완료 댓글 작성

워크플로: `.github/workflows/capture-from-issue.yml`

### 방법 B: 웹 페이지로 md 만들어 업로드
1. `web/index.html` 열기
2. 제목/내용 입력 후 Markdown 다운로드
3. 파일을 `content/`에 업로드
4. 액션이 `audio/*.mp3` 자동 생성

워크플로: `.github/workflows/tts-on-content.yml`

## 2) 구성 요소

- `scripts/refine_and_save.py`
  - 원문을 정리해서 오디오북용 markdown 생성
  - 기본 정리 모델: `gpt-4.1-mini`
- `scripts/generate_tts.py`
  - markdown/text를 TTS로 변환
  - 기본 모델: `gpt-4o-mini-tts`, voice: `coral`
  - 긴 텍스트는 자동 분할해서 `part01`, `part02`로 저장

## 3) 설정

필수 Secret:
- `OPENAI_API_KEY`

위치: GitHub 저장소 **Settings → Secrets and variables → Actions**

## 4) 로컬 테스트

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/refine_and_save.py --title "테스트" --text "안녕하세요" --no-refine
python scripts/generate_tts.py content/<생성된파일>.md
```

## 5) 확장 아이디어

- 텔레그램/슬랙 봇 입력 연동
- Whisper로 음성 메모 입력 → 텍스트 정리 → TTS
- 생성된 mp3를 GitHub Release Asset에도 업로드
