// app/static/js/main.js
let currentIndex = 0;
let userAnswers = [];
// 簡易セッションID
const sessionId = 'sess_' + Math.random().toString(36).substr(2, 9); 

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('quiz-container')) {
        renderQuestion();
    }
});

function renderQuestion() {
    const currentQ = quizQuestions[currentIndex];
    
    document.getElementById('question-text').innerText = currentQ.text;
    document.getElementById('progress-text').innerText = `${currentIndex + 1} / ${quizQuestions.length}`;
    
    const progressPercent = ((currentIndex) / quizQuestions.length) * 100;
    document.getElementById('progress-bar-fill').style.width = `${progressPercent}%`;

    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = ''; 
    
    scaleLabels.forEach(scale => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerText = scale.label;
        btn.onclick = () => handleAnswer(currentQ.id, scale.value);
        optionsContainer.appendChild(btn);
    });
}

function handleAnswer(questionId, answerValue) {
    userAnswers.push({
        q_id: questionId,
        value: answerValue
    });

    if (currentIndex < quizQuestions.length - 1) {
        currentIndex++;
        renderQuestion();
    } else {
        submitAnswers();
    }
}

async function submitAnswers() {
    const container = document.getElementById('quiz-container');
    container.innerHTML = '<h2 style="color:var(--accent-color);">解析中...</h2><p>OSコア・ベクトルを計算しています。</p>';

    const payload = {
        session_id: sessionId,
        answers: userAnswers
    };

    try {
        const response = await fetch('/api/diagnose', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            // 診断完了！結果ページへリダイレクト
            window.location.href = `/result?id=${result.assessment_id}`;
        } else {
            container.innerHTML = '<h2>エラーが発生しました</h2><p>サーバー側の処理に失敗しました。</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<h2>通信エラー</h2><p>ネットワークを確認してください。</p>';
    }
}