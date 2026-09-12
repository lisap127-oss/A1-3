// ===== TripAI 메인 JavaScript =====

// ===== 1. 여행지 추천 함수 =====
function getRecommendation() {
    const input = document.getElementById('travel-input').value.trim();
    const resultBox = document.getElementById('recommend-result');
    const resultText = document.getElementById('recommend-text');

    // 입력값 없을 때
    if (!input) {
        alert('여행 정보를 입력해주세요! 예) 제주도 3박4일 가족여행');
        return;
    }

    // 로딩 표시
    resultBox.classList.remove('hidden');
    resultText.innerHTML = '⏳ AI가 추천 코스를 생성 중입니다...';

    // API 호출
    fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
    })
    .then(response => response.json())
    .then(data => {
        resultText.innerHTML = formatResult(data.result);
    })
    .catch(error => {
        // API 연결 전 임시 더미 데이터
        resultText.innerHTML = getDummyRecommendation(input);
    });
}

// ===== 2. 맛집 검색 함수 =====
function searchRestaurant() {
    const input = document.getElementById('restaurant-input').value.trim();
    const resultBox = document.getElementById('restaurant-result');
    const resultText = document.getElementById('restaurant-text');

    // 입력값 없을 때
    if (!input) {
        alert('검색할 지역을 입력해주세요! 예) 부산 해운대 맛집');
        return;
    }

    // 로딩 표시
    resultBox.classList.remove('hidden');
    resultText.innerHTML = '⏳ AI가 맛집을 검색 중입니다...';

    // API 호출
    fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input + ' 맛집 추천해줘' })
    })
    .then(response => response.json())
    .then(data => {
        resultText.innerHTML = formatResult(data.result);
    })
    .catch(error => {
        // API 연결 전 임시 더미 데이터
        resultText.innerHTML = getDummyRestaurant(input);
    });
}

// ===== 3. 결과 텍스트 포맷 함수 =====
function formatResult(text) {
    // 줄바꿈을 <br>로 변환
    return text.replace(/\n/g, '<br>');
}

// ===== 4. 더미 데이터 (API 연결 전 테스트용) =====
function getDummyRecommendation(input) {
    return `
        🗺️ <strong>"${input}"</strong> 추천 코스<br><br>
        📍 <strong>1일차</strong> - 주요 관광지 탐방<br>
        &nbsp;&nbsp;오전: 대표 명소 방문 및 사진 촬영<br>
        &nbsp;&nbsp;오후: 전통 시장 구경 & 현지 음식 체험<br>
        &nbsp;&nbsp;저녁: 야경 명소 방문<br><br>
        📍 <strong>2일차</strong> - 자연 & 액티비티<br>
        &nbsp;&nbsp;오전: 자연 경관 트레킹<br>
        &nbsp;&nbsp;오후: 체험 활동 & 기념품 쇼핑<br>
        &nbsp;&nbsp;저녁: 현지 맛집 디너<br><br>
        💡 <strong>TIP</strong>: AI API 연결 시 더 정확한 추천을 받을 수 있어요!
    `;
}

function getDummyRestaurant(input) {
    return `
        🍽️ <strong>"${input}"</strong> 맛집 추천<br><br>
        ⭐ <strong>1위 - 현지 대표 맛집</strong><br>
        &nbsp;&nbsp;📍 위치: 시내 중심가<br>
        &nbsp;&nbsp;🍜 메뉴: 지역 특산 요리<br>
        &nbsp;&nbsp;💰 가격대: 1인 15,000~25,000원<br><br>
        ⭐ <strong>2위 - 전통 향토 음식점</strong><br>
        &nbsp;&nbsp;📍 위치: 전통 시장 근처<br>
        &nbsp;&nbsp;🍱 메뉴: 향토 정식<br>
        &nbsp;&nbsp;💰 가격대: 1인 10,000~18,000원<br><br>
        💡 <strong>TIP</strong>: AI API 연결 시 실시간 맛집 정보를 받을 수 있어요!
    `;
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