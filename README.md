# TripAI — AI 여행 플래너

취향·일정을 입력하면 Groq LLM 이 여행 코스와 맛집을 추천하는 정적 웹 + Vercel Python 서버리스 함수 프로젝트.
- 배포 URL: https://a1-3-ten.vercel.app/  
- 서비스 기획서: [서비스기획서.md](서비스기획서.md)  
- 증빙 자료(스크린샷): screenshots 폴더

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
## 학습 정리 (과제 목표)

이 프로젝트를 진행하며 아래 6가지를 이 저장소의 실제 코드를 근거로 설명할 수 있다.

### 1. HTML / CSS / JavaScript의 역할

- **HTML(`index.html`)**: 페이지의 구조와 콘텐츠(입력 폼, 결과가 표시될 영역, 섹션 간 이동 메뉴)를 정의한다. "무엇이 화면에 있는가"를 담당한다.
- **CSS(`css/`)**: HTML 요소의 레이아웃과 스타일(색상, 여백, 반응형 breakpoint)을 담당한다. 같은 HTML이라도 화면 크기(모바일/태블릿/데스크톱)에 따라 다르게 보이도록 만드는 부분이다.
- **JavaScript(`js/`)**: 사용자 동작(버튼 클릭, 입력)에 반응해 화면을 동적으로 바꾸고, 서버(API)와 데이터를 주고받는 "동작/로직"을 담당한다. HTML·CSS는 정적인 화면을, JS는 상호작용을 만든다.

### 2. 사용자 입력 → fetch 요청 → 화면 반영 흐름

1. 사용자가 입력 폼에 여행 조건(예: "제주도 3박4일 가족여행")을 입력하고 버튼을 클릭한다.
2. JS가 `input`/`click` 이벤트를 감지해 입력값을 읽어온다.
3. JS가 `fetch('/api/recommend', { method: 'POST', body: JSON.stringify({ message: ... }) })` 형태로 백엔드에 요청을 보낸다.
4. 백엔드(`api/recommend.py`)가 Groq API를 호출하고 결과를 JSON(`{ "result": "..." }`)으로 응답한다.
5. JS가 `fetch`의 응답(`response.json()`)을 받아 DOM(결과 표시 영역)에 렌더링한다.

즉 **"입력 → fetch 요청 → 서버 처리 → 응답 → 화면 갱신"** 이 한 사이클이며, 이 프로젝트에서는 `js/`의 이벤트 핸들러와 `api/recommend.py`의 `POST /api/recommend` 엔드포인트가 이 흐름을 구현한다.

### 3. Vercel Serverless Functions와 프론트-백엔드 호출 구조

- Vercel Serverless Functions는 `api/` 폴더 안의 파일(예: `recommend.py`)을 **각각 독립된 HTTP 엔드포인트**로 자동 변환해주는 기능이다. 별도의 서버를 띄우지 않아도 `api/recommend.py` 하나가 `POST /api/recommend` 라는 API가 된다.
- 프론트엔드는 순수 정적 파일(HTML/CSS/JS)로만 배포되고, AI(Groq) 호출처럼 **API 키가 필요한 로직은 전부 백엔드(Python 함수)에서만 실행**된다.
- 프론트는 그 백엔드 함수를 `fetch('/api/recommend')`로 호출할 뿐, Groq API를 직접 호출하지 않는다. 이렇게 분리해야 API 키가 브라우저(클라이언트) 코드에 노출되지 않는다.
- 이 프로젝트의 `vercel.json`은 `builds`/`routes`를 명시해 `/api/recommend` 경로가 `api/recommend.py`로 정확히 매핑되도록 강제한 설정이다(대시보드 자동 감지 방식이 아닌 명시적 라우팅).

### 4. 환경 변수로 API 키를 관리해야 하는 이유

- API 키가 코드에 그대로 적혀 있으면 GitHub에 커밋되는 순간 **공개 저장소를 통해 누구나 볼 수 있게 되고**, 유출된 키로 제3자가 과금을 유발하거나 서비스를 오남용할 수 있다.
- 환경 변수(`GROQ_API_KEY`)로 분리하면 키 값은 Vercel 프로젝트 설정(Settings → Environment Variables)에만 저장되고, 코드 저장소에는 `.env.example`처럼 **키 이름만** 남는다.
- 이 프로젝트는 `.env.example`에 필요한 환경 변수 목록만 두고, 실제 값이 담긴 `.env`는 `.gitignore`로 커밋 대상에서 제외했다. 로컬에서는 `.env`, 배포 환경에서는 Vercel 대시보드의 환경 변수가 각각 이 값을 채워준다.
- 만약 `GROQ_API_KEY`가 설정되지 않으면 `api/recommend.py`는 `500 {"error":"GROQ_API_KEY 환경변수가 설정되지 않았습니다"}`를 반환하도록 만들어, 키 누락을 코드가 아닌 설정 문제로 바로 식별할 수 있게 했다.

### 5. 로컬 환경과 배포 환경의 차이, 수정·재배포 흐름

- **로컬**: `vercel dev`로 정적 파일과 `api/` 함수를 동시에 실행하며, `.env` 파일의 값을 읽어 테스트한다. `http://localhost:3000`에서 동작을 즉시 확인할 수 있다.
- **배포(Vercel)**: GitHub `main` 브랜치에 push하면 Vercel이 자동으로 빌드·배포한다. 이때 코드에 저장된 값이 아니라 **Vercel 대시보드에 등록된 환경 변수**를 사용하므로, 로컬 `.env`와 배포 환경 변수를 각각 따로 설정해야 한다.
- 두 환경의 차이로 인해 로컬에서는 되는데 배포에서는 안 되는 문제(예: 환경 변수 미설정, `vercel.json`의 라우팅 설정 차이)가 발생할 수 있다. 실제로 이 프로젝트도 `vercel.json`의 `builds` 설정을 제거했을 때 배포가 실패한 이력이 있어, 원인을 파악한 뒤 설정을 원복하고 재배포하는 과정을 거쳤다.
- 수정 후 재배포 흐름은 **"문제 재현 → 원인 확인(코드 or 환경 변수 or 설정) → 로컬에서 수정 → 커밋/push → Vercel 자동 재배포 → 배포 URL에서 재확인"** 순서로 반복한다.

### 6. AI 코딩 도구로 생성한 코드의 오류 원인 파악

AI 코딩 도구로 코드를 생성하더라도 아래처럼 원인을 구조적으로 나눠 파악했다.

- **400 에러**: 요청 본문에 `message` 값이 비어 있거나 JSON 형식이 잘못된 경우 → 프론트의 입력 검증(빈 값 체크) 또는 `fetch`로 보내는 데이터 형식 문제.
- **500 에러**: `GROQ_API_KEY` 환경 변수가 서버(Vercel)에 설정되지 않은 경우 → 코드 문제가 아니라 배포 환경 설정 문제.
- **502 에러**: Groq API 자체가 키 무효·요청 한도 초과 등으로 오류를 반환한 경우 → 백엔드가 Groq의 원문 오류(`detail`)를 그대로 전달하도록 만들어, 외부 API 문제인지 우리 코드 문제인지 구분할 수 있게 했다.
- 배포가 실패했을 때는 Vercel의 빌드 로그와 `vercel.json`의 `routes`/`builds` 설정을 비교해, AI가 생성한 설정이 실제 배포 환경(레거시 `builds` 모드에서는 함수 경로에 확장자가 붙는 등)과 맞는지 확인하며 수정했다.

이처럼 AI가 작성한 코드를 그대로 쓰는 것이 아니라, **에러 메시지 → 원인 후보(프론트/백엔드/환경 변수/설정) → 재현 → 수정** 순서로 검증하며 진행했다.
