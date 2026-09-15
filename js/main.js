// ===== TripAI 메인 JavaScript =====

// ===== 1. 공통 API 호출 =====
async function askAI(message, resultBox, resultText, loadingMsg) {
    resultBox.classList.remove('hidden');
    resultText.textContent = loadingMsg;

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok || data.error) {
            const detail = data.detail ? `\n${data.detail}` : '';
            resultText.textContent = `오류: ${data.error || `HTTP ${response.status}`}${detail}`;
            return;
        }

        resultText.innerHTML = formatResult(data.result);
    } catch (error) {
        resultText.textContent = `서버에 연결할 수 없습니다: ${error.message}`;
    }
}

// ===== 2. 여행지 추천 =====
function getRecommendation() {
    const input = document.getElementById('travel-input').value.trim();
    if (!input) {
        alert('여행 정보를 입력해주세요! 예) 제주도 3박4일 가족여행');
        return;
    }
    askAI(
        input,
        document.getElementById('recommend-result'),
        document.getElementById('recommend-text'),
        'AI가 추천 코스를 생성 중입니다...'
    );
}

// ===== 3. 맛집 검색 =====
function searchRestaurant() {
    const input = document.getElementById('restaurant-input').value.trim();
    if (!input) {
        alert('검색할 지역을 입력해주세요! 예) 부산 해운대 맛집');
        return;
    }
    askAI(
        input + ' 맛집 추천해줘',
        document.getElementById('restaurant-result'),
        document.getElementById('restaurant-text'),
        'AI가 맛집을 검색 중입니다...'
    );
}

// ===== 4. 결과 텍스트 포맷 (HTML 이스케이프 후 줄바꿈만 <br>) =====
function formatResult(text) {
    const escaped = String(text ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    return escaped.replace(/\n/g, '<br>');
}

// ===== 5. 스크롤 애니메이션 =====
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.15)';
    } else {
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    }
});

// ===== 6. 엔터키로 검색 =====
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('travel-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') getRecommendation();
    });

    document.getElementById('restaurant-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchRestaurant();
    });
});
