---
title: TripAI(A1-3) 코드 오류 해소 및 Vercel 배포 복구 보고서
date: 2026-09-15
project: A1-3 (TripAI)
repo: https://github.com/lisap127-oss/A1-3
vercel_scope: pys2
status: 완료 — 프로덕션 공개 접근·API 실호출 200 검증
tags: [vercel, python-runtime, groq, deployment]
---

# TripAI(A1-3) 코드 오류 해소 및 Vercel 배포 복구 보고서

## 1. 접근 주소 (정본)

| 구분 | 주소 | 현재 상태 |
|---|---|---|
| Production (a1-3 프로젝트) | https://a1-3-pys2.vercel.app | 배포 성공 · Vercel 로그인 필요(302 → sso-api) |
| Production (trip-ai 프로젝트, 중복) | https://trip-ai-pys2.vercel.app | 배포 성공 · Vercel 로그인 필요 |
| API 엔드포인트 | https://a1-3-pys2.vercel.app/api/recommend | POST JSON `{"message": "..."}` |
| 이번 배포 고유 URL (a1-3) | https://a1-3-i0b4wj3mm-pys2.vercel.app | 커밋 f10970f |
| 이번 배포 고유 URL (trip-ai) | https://trip-57o6s4bzk-pys2.vercel.app | 커밋 f10970f |
| Vercel 대시보드 | https://vercel.com/pys2/a1-3 · https://vercel.com/pys2/trip-ai | 계정 pys2 로그인 |

- `https://trip-ai.vercel.app` 은 **타인의 사이트**(제목 "Page title")이므로 사용하지 않는다.
- 두 주소 모두 현재 `Deployment Protection → Vercel Authentication` 이 켜져 있어
  `pys2` 계정으로 로그인한 브라우저에서만 열린다. API 호출도 `401 {"protection":{"vercel_auth_enabled":true}}` 로 차단된다.
  → 공개 서비스로 쓰려면 §5-1 조치가 필요하다.

## 2. 해소한 코드 오류

| # | 파일 | 오류 | 조치 |
|---|---|---|---|
| 1 | api/recommend.py | 함수형 `handler(request)` 에서 정의되지 않은 `Response` 사용 → 모든 요청 `NameError` | Vercel 규약대로 `BaseHTTPRequestHandler` 서브클래스 `handler` 로 재작성 (`do_POST`/`do_OPTIONS`/`do_GET`) |
| 2 | api/recommend.py | 모델 `llama3-8b-8192` — Groq 2025-08-30 퇴역 | 공식 대체 `llama-3.1-8b-instant` (환경변수 `GROQ_MODEL` 로 변경 가능) |
| 3 | api/recommend.py | 기본 UA `Python-urllib/3.x` → Cloudflare `403 error 1010` 차단 (로컬 실측) | `User-Agent: TripAI/1.0` 명시 |
| 4 | api/recommend.py | 예외 시 원인 소실 | Groq 오류는 502 + `detail` 원문, 입력 오류 400, 키 미설정 500 으로 분리 |
| 5 | js/main.js | fetch 실패 시 **더미 데이터로 덮어** 장애가 보이지 않음 | 더미 제거, 서버 오류 메시지 그대로 표시 |
| 6 | js/main.js | LLM 출력을 `innerHTML` 에 원문 삽입 (XSS) | HTML 이스케이프 후 줄바꿈만 `<br>` |
| 7 | vercel.json | `builds` 제거 후 전 배포 실패 (§3) | 검증된 `builds` + `routes` 구성 복원 |
| 8 | requirements.txt | 미사용 `groq`·`requests`·`python-dotenv` | 비움 (표준 라이브러리만 사용) |

## 3. 배포 실패 원인 규명 (GitHub Deployments API 21건 전수 분석)

```
09-12 16:08  4a4012c  success   ← vercel.json 에 builds 블록 존재
09-12 16:25  fff7ac0  success
09-12 16:42  b30d75c  success   ← 마지막 성공 (단, routes dest 가 /api/$1 이라 API 는 404)
09-13 15:45  cc18132  failure   ← "remove builds from vercel.json" — 이후 전부 실패
09-13 ~      7691178 · 2f592dc · c9d21d9 · f057df2   failure
09-15 16:07  0e137e4  failure   ← 본 세션 1차 (zero-config)
09-15 16:10  f10970f  SUCCESS   ← 본 세션 2차 (builds 복원)
```

- `builds` 가 있으면 Vercel 은 대시보드 *Build & Development Settings* 를 무시한다.
  즉 대시보드에 잘못된 빌드 설정이 남아 있어 zero-config 배포가 즉시 실패했고, `builds` 가 이를 우회한다.
- legacy `builds` 모드에서는 Python 함수가 `/api/recommend.py` 경로(확장자 포함)로 노출된다.
  b30d75c 는 `dest: /api/$1` 이라 배포는 됐어도 API 가 404 → 프론트가 더미 데이터로 덮어 "동작하는 척" 했다.
  cc18132 가 `dest` 를 `/api/$1.py` 로 바로잡았으나 같은 커밋에서 `builds` 를 제거해 빌드가 깨졌다.

## 4. 검증 결과

### 4-1. 로컬 (HTTPServer + 실제 핸들러 클래스)

| 케이스 | 기대 | 결과 |
|---|---|---|
| OPTIONS | 204 + CORS | 204 |
| GET | 405 | 405 `POST 요청만 지원합니다` |
| 잘못된 JSON | 400 | 400 |
| 빈 message | 400 | 400 |
| GROQ_API_KEY 미설정 | 500 | 500 `GROQ_API_KEY 환경변수가 설정되지 않았습니다` |
| 무효 키 | 502 + Groq 원문 | 502 `Invalid API Key` (Groq 인증 계층까지 도달 확인) |
| 정적 `/`·`/css/style.css`·`/js/main.js` | 200 | 200 (title `TripAI - AI 여행 플래너`) |

### 4-2. Vercel (GitHub Deployments API)

- Vercel GitHub App(`vercel[bot]`) 이 저장소에 설치·활성 상태 — push 마다 Production 배포 생성.
- 커밋 `f10970f`: **a1-3 success · trip-ai success** (각각 약 20초 내 완료).
- 프로덕션 도메인은 Vercel Authentication 으로 가려져 있어 **200 응답·Groq 실호출은 본 세션에서 미검증**.

## 5. 계정 보유자(pys2) 가 해야 할 조치

### 5-1. 공개 접근 허용 (필수)
Vercel → 프로젝트 `a1-3` → Settings → **Deployment Protection** → *Vercel Authentication* → **Disabled** → Save.
(이후 https://a1-3-pys2.vercel.app 이 로그인 없이 200 으로 열린다.)

### 5-2. Groq 키 등록 (필수)
Settings → **Environment Variables** → `GROQ_API_KEY` = `gsk_...` (Production 체크) → Save → **Redeploy**.
키 발급: https://console.groq.com/keys
미설정 시 화면에 `오류: GROQ_API_KEY 환경변수가 설정되지 않았습니다` 가 그대로 표시된다(더 이상 더미로 가려지지 않음).

### 5-3. 중복 프로젝트 정리 (권장)
같은 저장소가 `a1-3` 과 `trip-ai` 두 프로젝트에 연결되어 push 마다 2회 배포된다.
`trip-ai` → Settings → General → 맨 아래 **Delete Project**. (`a1-3` 만 남긴다.)

### 5-4. 확인 명령 (조치 후)
```bash
curl -I https://a1-3-pys2.vercel.app                       # 200 기대
curl -X POST https://a1-3-pys2.vercel.app/api/recommend \
     -H 'Content-Type: application/json' -d '{"message":"제주도 2박3일"}'   # {"result": ...} 기대
```

## 6. 보안 메모

- 대화에 입력된 GitHub PAT(`ghp_otuz…`, classic, `repo`·`admin:*` 등 광범위 권한)는 유효하며 push 에 사용했다.
  저장소 `.git/config` 나 파일에는 남기지 않았다. **GitHub → Settings → Developer settings 에서 폐기 후 재발급 권장.**
- `.env` 는 `.gitignore` 로 제외되어 있고, `.env.example` 만 커밋했다.

## 7. 변경 커밋

- `0e137e4` fix: Vercel Python 핸들러 규약 준수 및 퇴역 모델 교체
- `f10970f` fix: vercel.json 을 검증된 builds/routes 구성으로 복원

## 8. 관련 파일

- /Users/woo/cody/api/recommend.py
- /Users/woo/cody/js/main.js
- /Users/woo/cody/vercel.json
- /Users/woo/cody/README.md
- /Users/woo/cody/.env.example
- /Users/woo/cody/docs/reports/260915-vercel-deploy-fix-report.md


## 9. 2차 작업 (Vercel 토큰으로 직접 처리 · 2026-09-15 오후)

| 항목 | 이전 | 조치 후 |
|---|---|---|
| Framework Preset (a1-3) | `python` — zero-config 즉시 실패의 근본 원인 | `Other`(null) |
| 환경변수 | `groqkey` (코드가 읽지 않는 이름, 실수 버전) | `GROQ_API_KEY` (production·preview·development) · `groqkey` 삭제 |
| 모델 | `llama-3.1-8b-instant` → Groq `404 model_not_found` | `openai/gpt-oss-120b` (계정 사용 가능 모델 실측 후 한국어 품질·1.3s 기준 선택) |
| 중복 프로젝트 `trip-ai` | push 마다 2회 배포 | 삭제 (HTTP 204) |
| Deployment Protection | (계정 보유자가 해제) | 3 alias 모두 200 |

### 최종 실측 (커밋 1b54d49 이후)
- `GET https://a1-3-pys2.vercel.app/` → 200, `<title>TripAI - AI 여행 플래너</title>`
- `POST /api/recommend {"message":"제주도 3박4일 가족여행"}` → **200**, 1,214자 한국어 일정
- `POST /api/recommend {"message":"부산 해운대 맛집 추천해줘"}` → **200**, 맛집 5곳 목록

### 정본 접근 주소
- https://a1-3-pys2.vercel.app  (동일 배포: https://a1-3-ten.vercel.app · https://a1-3-git-main-pys2.vercel.app)
