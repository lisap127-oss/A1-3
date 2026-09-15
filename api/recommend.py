import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
# llama3-8b-8192(2025-08-30 퇴역)·llama-3.1-8b-instant(이 계정에서 model_not_found) 모두 불가.
# 2026-09-15 /v1/models 실측: 한국어 품질·속도 최상은 openai/gpt-oss-120b (환경변수 GROQ_MODEL 로 변경 가능)
DEFAULT_MODEL = 'openai/gpt-oss-120b'

SYSTEM_PROMPT = """당신은 친절한 한국어 여행 플래너입니다. 반드시 한국어로 답합니다.
마크다운 표·헤딩(#)·굵게(**) 를 쓰지 말고, 줄바꿈과 '-' 목록만으로 답하세요 (화면이 일반 텍스트로 표시됩니다).

- 여행 일정 요청이면 다음 형식으로 답하세요:
  - 1일차: 오전/오후/저녁 일정
  - 2일차: 오전/오후/저녁 일정 (요청한 일수만큼)
  - 맛집 추천
  - 여행 팁
- 맛집 검색 요청이면 지역 대표 맛집 3~5곳을 이름·위치·대표 메뉴·가격대와 함께 목록으로 답하세요."""


def ask_groq(api_key, user_input):
    payload = json.dumps({
        'model': os.environ.get('GROQ_MODEL', DEFAULT_MODEL),
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_input},
        ],
        'max_tokens': 1500,
    }).encode('utf-8')

    req = urllib.request.Request(
        GROQ_URL,
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            # 기본 UA(Python-urllib/x.y)는 Cloudflare 가 403(error 1010)으로 차단한다
            'User-Agent': 'TripAI/1.0',
        },
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        result = json.loads(response.read())
    return result['choices'][0]['message']['content']


# Vercel Python 런타임 규약: /api/*.py 는 BaseHTTPRequestHandler 를 상속한
# 최상위 클래스 `handler` 를 정의해야 한다. api/recommend.py → /api/recommend
class handler(BaseHTTPRequestHandler):

    def _send_json(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self._send_json(405, {'error': 'POST 요청만 지원합니다'})

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        try:
            data = json.loads(self.rfile.read(length) or b'{}')
        except json.JSONDecodeError:
            return self._send_json(400, {'error': '잘못된 JSON 요청입니다'})

        user_input = (data.get('message') or '').strip()
        if not user_input:
            return self._send_json(400, {'error': '여행 정보를 입력해주세요'})

        api_key = os.environ.get('GROQ_API_KEY', '').strip()
        if not api_key:
            return self._send_json(500, {'error': 'GROQ_API_KEY 환경변수가 설정되지 않았습니다'})

        try:
            answer = ask_groq(api_key, user_input)
        except urllib.error.HTTPError as e:
            detail = e.read().decode('utf-8', 'replace')[:500]
            return self._send_json(502, {'error': f'Groq API 오류 ({e.code})', 'detail': detail})
        except Exception as e:
            return self._send_json(500, {'error': str(e)})

        self._send_json(200, {'result': answer})
