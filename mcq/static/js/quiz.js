
document.addEventListener("DOMContentLoaded", function () {
    const questions = document.querySelectorAll('.quiz-question');
    const nextBtn = document.getElementById('next-btn');
    const progressText = document.getElementById('quiz-progress');
    const timerDisplay = document.getElementById('timer-display');
    let current = 0;
  
    const timeLimit = parseFloat(document.getElementById('quiz-meta').dataset.timePerQuestion) * 60;
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
  
        if (remaining <= 10) {
          timerDisplay.classList.add('timer-warning');
        } else {
          timerDisplay.classList.remove('timer-warning');
        }
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
        showResults();
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
        showResults();
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
  
    function showResults() {
        document.getElementById('quiz-container').innerHTML = '';
        document.querySelector('.bottom-bar').remove();
        document.getElementById('quiz-progress').remove();
      
        let correctCount = 0;
        const totalQuestions = questions.length;
          
      
        const reviewHTML = Array.from(questions).map((questionEl, index) => {
          const difficulty = questionEl.dataset.difficulty || 'unknown';
          const questionId = questionEl.dataset.questionId;
        
          const correctInputEl = questionEl.querySelector('.form-check-input[data-correct]');
          const correctValue = correctInputEl ? correctInputEl.value.trim().toUpperCase() : null;
          const correctLabelEl = correctInputEl ? questionEl.querySelector(`label[for="${correctInputEl.id}"]`) : null;
          const correctText = correctLabelEl ? correctLabelEl.textContent.trim() : 'N/A';
        
          const userValueRaw = userAnswers[index] || '';
          const userValue = userValueRaw.trim().toUpperCase();
          const userInputEl = questionEl.querySelector(`.form-check-input[value="${userValue}"]`);
          const userLabelEl = userInputEl ? questionEl.querySelector(`label[for="${userInputEl.id}"]`) : null;
          const userText = userLabelEl ? userLabelEl.textContent.trim() : 'N/A';
        
          const isCorrect = userValue === correctValue;
          if (isCorrect) correctCount++;
        
          const questionText = questionEl.querySelector('h4').textContent;
          const explanationEl = questionEl.querySelector('.question-explanation');
          const explanation = explanationEl ? explanationEl.dataset.explanation : null;
        
          const topic = questionEl.querySelector('.badge + small')?.textContent || '';
          const alreadyFlagged = questionEl.getAttribute("data-flagged") === "true";


        
          let flagMarkup = "";
          if (document.body.dataset.superuser === "true") {
            if (alreadyFlagged) {
              flagMarkup = `<span class="badge bg-warning text-dark mt-2 d-inline-block">🚩 Already flagged</span>`;
            } else {
              flagMarkup = `<button class="btn btn-sm btn-outline-danger flag-btn mt-2" data-question-id="${questionId}">
                              🚩 Flag for review
                            </button>`;
            }
          }
        
          return `
            <div class="card mb-4 shadow-sm ${isCorrect ? 'correct' : 'incorrect'}">
              <div class="card-body">
                <p class="mb-1">
                  <span class="badge ${
                    difficulty === 'easy' ? 'bg-success' :
                    difficulty === 'medium' ? 'bg-primary' :
                    difficulty === 'hard' ? 'bg-warning text-dark' :
                    difficulty === 'hardcore' ? 'bg-danger' : 'bg-secondary'
                  }">${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}</span>
                  <small class="text-muted ms-2">${topic}</small>
                </p>
                <h5 class="card-title">${questionText}</h5>
                <p class="mb-1">
                  <strong>Your answer:</strong> ${userText}
                  ${isCorrect ? '✅' : '<span style="color:red;">✖️</span>'}
                </p>
                <p class="mb-1"><strong>Correct answer:</strong> ${correctText}</p>
                ${explanation ? `<div class="alert alert-info mt-3"><strong>Explanation:</strong> ${explanation}</div>` : ''}
                ${flagMarkup}
              </div>
            </div>
          `;
        }).join('');

              
        const percentage = Math.round((correctCount / totalQuestions) * 100);
        const timeTakenSeconds = Math.floor((quizEndTime - quizStartTime) / 1000);
        const mins = Math.floor(timeTakenSeconds / 60);
        const secs = timeTakenSeconds % 60;

        const chainLength = parseInt(document.getElementById("quiz-meta").dataset.chainLength || "1");
        const points = correctCount * 100 * Math.min(chainLength, 7);


        
      
        const resultsHeader = `
          <h3 class="mb-4">Quiz Results</h3>
          <p><strong>Score:</strong> ${correctCount} / ${totalQuestions} (${percentage}%)</p>
          <p><strong>Points Earned:</strong> ${points}</p>
          <p><strong>Total Time:</strong> ${mins}m ${secs}s</p>
          <hr class="my-4">
        `;
      
        const container = document.createElement('div');
        container.className = 'results';
        container.innerHTML = resultsHeader + reviewHTML;

        // Replace all content inside <main> with the results
        const main = document.querySelector('main');
        main.innerHTML = '';
        main.appendChild(container);


        if (document.body.dataset.superuser === "true") {
          document.querySelectorAll('.flag-btn').forEach(btn => {
            btn.addEventListener('click', () => {
              const questionId = btn.dataset.questionId;
              const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
              fetch("/flag-question/", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ question_id: questionId })
              })
              .then(res => res.json())
              .then(data => {
                if (data.success) {
                  const badge = document.createElement("span");
                  badge.className = "badge bg-warning text-dark mt-2 d-inline-block";
                  badge.textContent = "🚩 Already flagged";
                  btn.replaceWith(badge);
                } else {
                  alert("Couldn't flag question.");
                }
              });
            });
          });
        }

        // Scroll to the top of the main content
        // container.scrollIntoView({ behavior: 'auto', block: 'start' });

        const payload = generateResultsPayload();
        sendResultsToBackend(payload);
          

        
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
    
        // Get keywords from query string
        const query = new URLSearchParams(window.location.search);
        const keywordParam = query.get("keywords"); // e.g. "1,2,3"
        const keywords = keywordParam ? keywordParam.split(',').map(k => parseInt(k)) : [];
        
        const chainLength = parseInt(document.getElementById("quiz-meta").dataset.chainLength || "1");
        const points = score * 100 * Math.min(chainLength, 7);
        // Get points from the score

        return {
            score,
            total_questions,
            time_taken,
            keywords,
            responses,
            points,
        };
    }
    function sendResultsToBackend(results) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        fetch("/save-quiz/", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(results)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
            console.log("Quiz saved. Attempt ID:", data.attempt_id);

            const attemptCount = data.attempt_count || 0;
            if (attemptCount > 0 && attemptCount % 5 === 0) {
              const coffeeModal = new bootstrap.Modal(document.getElementById('coffeeModal'));
              coffeeModal.show();
            }

            } else {
              console.error("Error saving quiz:", data.error);
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
        });
    }
      
      
  
    // Init
    showQuestion(current);
    quizStartTime = new Date();

  });

