let currentIndex = 0;
let userAnswers = [];
// 簡易的なセッションIDの生成（本来はより強固なUUIDライブラリを推奨）
const sessionId = 'sess_' + Math.random().toString(36).substr(2, 9); 

document.addEventListener('DOMContentLoaded', () => {
    renderQuestion();
});

function renderQuestion() {
    const currentQ = quizQuestions[currentIndex];
    
    // UIの更新
    document.getElementById('question-text').innerText = currentQ.text;
    document.getElementById('progress-text').innerText = `${currentIndex + 1} / ${quizQuestions.length}`;
    
    // プログレスバーの更新
    const progressPercent = ((currentIndex) / quizQuestions.length) * 100;
    document.getElementById('progress-bar-fill').style.width = `${progressPercent}%`;

    // 選択肢ボタンの生成
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = ''; // 一旦クリア
    
    scaleLabels.forEach(scale => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerText = scale.label;
        btn.onclick = () => handleAnswer(currentQ.id, scale.value);
        optionsContainer.appendChild(btn);
    });
}

function handleAnswer(questionId, answerValue) {
    // 回答を記録
    userAnswers.push({
        q_id: questionId,
        value: answerValue
    });

    // 次の問題へ、または結果送信へ
    if (currentIndex < quizQuestions.length - 1) {
        currentIndex++;
        renderQuestion();
    } else {
        submitAnswers();
    }
}

async function submitAnswers() {
    // 送信中はUIをローディング状態にする
    document.getElementById('quiz-container').innerHTML = '<h2>解析中...</h2><p>あなたのOSを特定しています</p>';

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
            // 診断完了！結果ページへリダイレクト（assessment_idを渡す）
            window.location.href = `/result?id=${result.assessment_id}`;
        } else {
            alert('通信エラーが発生しました。');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('エラーが発生しました。時間を置いて再度お試しください。');
    }
}