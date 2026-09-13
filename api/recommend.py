import json
import os
import urllib.request

def handler(request):
    # OPTIONS (CORS 프리플라이트)
    if request.method == 'OPTIONS':
        return Response('', status=200, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        })

    if request.method != 'POST':
        return Response(json.dumps({'error': 'Method not allowed'}), status=405, headers={
            'Content-Type': 'application/json'
        })

    try:
        data = request.json()
        user_input = data.get('message', '')

        api_key = os.environ.get('GROQ_API_KEY', '')
        if not api_key:
            return Response(json.dumps({'error': 'API 키가 없습니다'}), status=500, headers={
                'Content-Type': 'application/json'
            })

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

            return Response(json.dumps({'result': answer}, ensure_ascii=False), status=200, headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            })

    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, headers={
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        })