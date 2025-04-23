document.addEventListener("DOMContentLoaded", function () {
  const quizMeta = document.getElementById("quiz-meta");
  const isAuthenticated = quizMeta.dataset.userAuthenticated === "True";
  const chainLength = parseInt(quizMeta.dataset.chainLength || "1");
  const timeLimit = parseFloat(quizMeta.dataset.timePerQuestion) * 60;

  const questions = document.querySelectorAll('.quiz-question');
  const nextBtn = document.getElementById('next-btn');
  const progressText = document.getElementById('quiz-progress');
  const timerDisplay = document.getElementById('timer-display');

  let current = 0;
  let timerInterval = null;
  let userAnswers = {};
  let quizStartTime = null;
  let quizEndTime = null;

  function updateProgress(index) {
    progressText.textContent = `Question ${index + 1} of ${questions.length}`;
  }

  function updateButtonState() {
    const selected = document.querySelector(`input[name="question-${current}"]:checked`);
    nextBtn.disabled = !selected;
  }

  function startTimer(seconds) {
    let remaining = seconds;

    function updateDisplay() {
      const mins = Math.floor(remaining / 60);
      const secs = remaining % 60;
      timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

      timerDisplay.classList.toggle('timer-warning', remaining <= 10);
    }

    updateDisplay();
    timerInterval = setInterval(() => {
      remaining--;
      updateDisplay();
      if (remaining <= 0) {
        clearInterval(timerInterval);
        timerInterval = null;
        autoAdvance();
      }
    }, 1000);
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  function autoAdvance() {
    const selected = document.querySelector(`input[name="question-${current}"]:checked`);
    if (selected) {
      userAnswers[current] = selected.value;
    }

    current++;
    if (current < questions.length) {
      showQuestion(current);
    } else {
      quizEndTime = new Date();
      handleQuizCompletion();
    }
  }

  function showQuestion(index) {
    questions.forEach((q, i) => q.style.display = i === index ? 'block' : 'none');
    nextBtn.disabled = true;
    nextBtn.textContent = index === questions.length - 1 ? 'Finish' : 'Next';

    updateProgress(index);
    stopTimer();
    startTimer(timeLimit);
  }

  nextBtn.addEventListener('click', function () {
    const selected = document.querySelector(`input[name="question-${current}"]:checked`);
    if (!selected) return;

    userAnswers[current] = selected.value;

    stopTimer();
    current++;
    if (current < questions.length) {
      showQuestion(current);
    } else {
      quizEndTime = new Date();
      handleQuizCompletion();
    }
  });

  document.addEventListener('change', function (e) {
    if (e.target.classList.contains('answer-option')) {
      const questionIndex = e.target.name.split('-')[1];
      if (parseInt(questionIndex) === current) {
        updateButtonState();
      }
    }
  });

  function handleQuizCompletion() {
    submitResults();  // Always submit
  }
  

  function submitResults() {
    const payload = generateResultsPayload();
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch("/save-quiz/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success && data.attempt_id) {
        window.location.href = `/my-quizzes/${data.attempt_id}`;
      } else {
        alert("Something went wrong saving your quiz. Please try again.");
      }
    })
    .catch(error => {
      console.error("Error submitting quiz:", error);
      alert("Network error. Please try again.");
    });
  }

  function generateResultsPayload() {
    const responses = [];

    questions.forEach((questionEl, index) => {
      const questionId = parseInt(questionEl.dataset.questionId);
      const correctInput = questionEl.querySelector('.form-check-input[data-correct]');
      const correctAnswer = correctInput ? correctInput.value.trim().toUpperCase() : null;

      const userAnswerRaw = userAnswers[index] || '';
      const userAnswer = userAnswerRaw.trim().toUpperCase();
      const isCorrect = userAnswer === correctAnswer;

      responses.push({
        question_id: questionId,
        user_answer: userAnswer,
        correct: isCorrect
      });
    });

    const score = responses.filter(r => r.correct).length;
    const total_questions = questions.length;
    const time_taken = Math.floor((quizEndTime - quizStartTime) / 1000);

    const query = new URLSearchParams(window.location.search);
    const keywordParam = query.get("keywords");
    const keywords = keywordParam ? keywordParam.split(',').map(k => parseInt(k)) : [];

    const points = score * 100 * Math.min(chainLength, 7);

    return {
      score,
      total_questions,
      time_taken,
      keywords,
      responses,
      points
    };
  }

  // Init
  showQuestion(current);
  quizStartTime = new Date();
});

document.getElementById('share-btn').addEventListener('click', async () => {
  const shareUrl = window.location.href;

  if (navigator.share) {
    try {
      await navigator.share({
        title: document.title,
        url: shareUrl
      });
    } catch (err) {
      console.warn('Sharing cancelled or failed:', err);
    }
  } else {
    try {
      await navigator.clipboard.writeText(shareUrl);
      showCopyToast();
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }
});

function showCopyToast() {
  const toast = document.getElementById('copy-toast');
  toast.classList.remove('d-none');
  toast.classList.add('fade', 'show');

  setTimeout(() => {
    toast.classList.remove('show');
    toast.classList.add('d-none');
  }, 2000);
}
