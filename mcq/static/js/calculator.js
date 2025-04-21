let calculatorVisible = false;

function toggleCalculator() {
    const calculator = document.getElementById('calculator-container');
    const currentQuestion = document.querySelector('.quiz-question[style*="block"]');
  
    // Clear previous insertions
    const existingWrapper = document.getElementById('calculator-wrapper');
    if (existingWrapper) existingWrapper.remove();
  
    calculator.style.display = 'block'; // Always show while relocating
  
    const wrapper = document.createElement('div');
    wrapper.id = 'calculator-wrapper';
  
    if (window.innerWidth >= 768) {
      // Desktop: Insert to the right of answers
      wrapper.style.display = 'inline-block';
      wrapper.style.marginLeft = '30px';
      currentQuestion.querySelector('.quiz-answers').appendChild(wrapper);
    } else {
      // Mobile: Insert below, center, and scroll
      wrapper.style.textAlign = 'center';
      wrapper.style.marginTop = '20px';
      wrapper.style.paddingBottom = '80px'; // for fixed bottom bar
  
      currentQuestion.appendChild(wrapper);
      
    }
  
    wrapper.appendChild(calculator);
  }

  function insertToDisplay(value) {
    const display = document.getElementById('calc-display');
    if (display.value === 'Error') {
      display.value = '';
    }
  
    if (value === '×10^') {
      display.value += '*10^';
      return;
    }
  
    const lastChar = display.value.slice(-1);
    const needsMultiplication = /^[a-zπe√(]/i.test(value);
  
    if (lastChar && !'+-*/^('.includes(lastChar) && needsMultiplication) {
      display.value += '*' + value;
    } else {
      display.value += value;
    }
  }
  

function clearDisplay() {
  document.getElementById('calc-display').value = '';
}

function deleteLast() {
  const display = document.getElementById('calc-display');
  display.value = display.value === 'Error' ? '' : display.value.slice(0, -1);
}

function calculateResult() {
    const display = document.getElementById('calc-display');
    try {
      let expression = display.value;
  
      // STEP 0: Normalize any accidental Unicode symbols
      expression = expression.replace(/×/g, '*');
  
      // STEP 1: Replace functions
      expression = expression
        .replace(/×/g, '*')  // normalize × symbol
        .replace(/log\(/g, 'Math.log10(')
        .replace(/ln\(/g, 'Math.log(')
        .replace(/sin\(/g, 'Math.sin(')
        .replace(/cos\(/g, 'Math.cos(')
        .replace(/tan\(/g, 'Math.tan(')
        .replace(/exp\(/g, 'Math.exp(')
        .replace(/√\(/g, 'Math.sqrt(')
        .replace(/π/g, 'Math.PI')
        .replace(/(?<![\w.])e(?![\w.])/g, 'Math.E')
        .replace(/(\d+)\^2/g, 'Math.pow($1, 2)')
        .replace(/([0-9.]+|\([^()]+\))\^(-?[0-9.]+)/g, 'Math.pow($1, $2)');

  
      // STEP 2: Replace constants
      expression = expression
        .replace(/π/g, 'Math.PI')
        .replace(/(?<![\w.])e(?![\w.])/g, 'Math.E');
  
    //   // STEP 3: Replace powers
    //   expression = expression
    //     .replace(/(\d+)\^2/g, 'Math.pow($1, 2)')
    //     .replace(/([0-9.]+|\(.+?\))\^([0-9.]+)/g, 'Math.pow($1, $2)');
  
      console.log("Evaluating:", expression);
      display.value = eval(expression);
    } catch (err) {
      console.error("Eval error:", err.message);
      display.value = 'Error';
    }
  }
  
  
  
  

  function insertToDisplay(value) {
    const display = document.getElementById('calc-display');
    if (display.value === 'Error') {
      display.value = '';
    }
  
    const lastChar = display.value.slice(-1);
    const needsMultiplication = /^[a-zπe√]/i.test(value);
  
    if (lastChar && !'+-*/^('.includes(lastChar) && needsMultiplication) {
      display.value += '*' + value;
    } else {
      display.value += value;
    }
  }
  
  

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.calc-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const val = btn.dataset.val;
      if (val === 'AC') clearDisplay();
      else if (val === 'DEL') deleteLast();
      else if (val === '=') calculateResult();
      else insertToDisplay(val);
    });
  });
});

document.addEventListener('click', function (e) {
    const calculator = document.getElementById('calculator-container');
    const toggleBtn = document.getElementById('toggle-calculator-btn');
    if (!calculator.contains(e.target) && !toggleBtn.contains(e.target)) {
      calculator.style.display = 'none';
      calculatorVisible = false;
    }
  });
  
