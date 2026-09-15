# TripAI — AI 여행 플래너

취향·일정을 입력하면 Groq LLM 이 여행 코스와 맛집을 추천하는 정적 웹 + Vercel Python 서버리스 함수 프로젝트.

```
index.html / css/ / js/    정적 프론트엔드
api/recommend.py           POST /api/recommend  → Groq chat completions (표준 라이브러리만 사용)
vercel.json                Vercel 설정 — 명시적 builds/routes (대시보드 빌드 설정과 무관하게 배포되도록)
.env.example               필요한 환경변수 목록
```

## 로컬 실행

```bash
cp .env.example .env            # GROQ_API_KEY 입력
npm i -g vercel && vercel dev   # http://localhost:3000  (정적 + /api 함수 동시 실행)
```

## Vercel 배포 — 필수 조치

1. **환경변수**: Vercel 프로젝트 → Settings → Environment Variables → `GROQ_API_KEY` 추가 (Production·Preview 모두).
   없으면 `/api/recommend` 가 `500 {"error":"GROQ_API_KEY 환경변수가 설정되지 않았습니다"}` 를 돌려준다.
2. **공개 접근**: Settings → Deployment Protection → *Vercel Authentication* 을 끄지 않으면
   `*.vercel.app` 주소가 Vercel 로그인 화면(302)으로 리다이렉트된다.
3. **배포 트리거**: GitHub `main` 에 push 하면 Vercel 이 자동 배포한다 (Git 연동).
   `vercel.json` 의 `builds` 가 있는 동안 대시보드의 Build & Development Settings 는 무시된다 —
   이 저장소에서 `builds` 를 제거한 커밋(cc18132 이후)은 전부 배포 실패했으므로 유지한다.
   legacy `builds` 모드에서는 함수 경로에 확장자가 붙으므로(`/api/recommend.py`) routes 로 `/api/recommend` 를 매핑한다.
4. **모델**: 기본 `openai/gpt-oss-120b` (2026-09 기준 이 Groq 계정에 Llama 계열 없음). 바꾸려면 환경변수 `GROQ_MODEL` 설정.

## API

```
POST /api/recommend
Content-Type: application/json
{"message": "제주도 3박4일 가족여행"}

200 {"result": "..."}          성공
400 {"error": "..."}           입력 누락·JSON 오류
500 {"error": "..."}           GROQ_API_KEY 미설정
502 {"error": "...", "detail": "..."}   Groq 측 오류(키 무효·한도 초과 등) 원문 전달
```
