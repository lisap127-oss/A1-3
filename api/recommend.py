from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        # 요청 본문 읽기
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        user_input = data.get('message', '')
        
        # Groq API 호출
        api_key = os.environ.get('GROQ_API_KEY', '')
        
        if not api_key:
            self._send_response(500, {'error': 'API 키가 없습니다'})
            return
        
        try:
            prompt = f"""당신은 친절한 여행 플래너입니다.
사용자 요청: {user_input}

다음 형식으로 여행 일정을 추천해주세요:
- 1일차: 오전/오후/저녁 일정
- 2일차: 오전/오후/저녁 일정
- 맛집 추천
- 여행 팁"""

            payload = json.dumps({
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024
            }).encode('utf-8')
            
            req = urllib.request.Request(
                'https://api.groq.com/openai/v1/chat/completions',
                data=payload,
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read())
                answer = result['choices'][0]['message']['content']
                self._send_response(200, {'result': answer})
                
        except Exception as e:
            self._send_response(500, {'error': str(e)})
    
    def do_OPTIONS(self):
        self._send_response(200, {})
    
    def _send_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))