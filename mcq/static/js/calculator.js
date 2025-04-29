let calculatorVisible = false;

function toggleCalculator() {
  const calculator = document.getElementById('calculator-container');
  const currentQuestion = document.querySelector('.quiz-question[style*="block"]');

  if (calculator.style.display === 'block') {
    calculator.style.display = 'none';
    return;
  }

  const existingWrapper = document.getElementById('calculator-wrapper');
  if (existingWrapper) existingWrapper.remove();

  calculator.style.display = 'block';

  const wrapper = document.createElement('div');
  wrapper.id = 'calculator-wrapper';

  if (window.innerWidth >= 768) {
    wrapper.style.display = 'inline-block';
    wrapper.style.marginLeft = '30px';
    currentQuestion.querySelector('.quiz-answers').appendChild(wrapper);
  } else {
    wrapper.style.textAlign = 'center';
    wrapper.style.marginTop = '20px';
    wrapper.style.paddingBottom = '80px';
    currentQuestion.appendChild(wrapper);
  }

  wrapper.appendChild(calculator);
}

function insertToDisplay(value) {
  const display = document.getElementById('calc-display');
  if (display.value === 'Error') {
    display.value = '';
  }

  const constants = {
    e_const: 'Math.E',
    c_const: '3.00e8',
    h_const: '6.626e-34'
  };

  if (constants[value]) {
    display.value += constants[value];
  } else if (value === '×10^') {
    display.value += '×10^';  // Insert display-friendly symbol
  } else {
    const lastChar = display.value.slice(-1);
    const needsMultiplication = /^[a-zπe√(]/i.test(value);
    if (lastChar && !'+-*/^('.includes(lastChar) && needsMultiplication) {
      display.value += '*' + value;
    } else {
      display.value += value;
    }
  }

  setTimeout(() => {
    display.scrollLeft = display.scrollWidth;
  }, 0);
}

function deleteLast() {
  const display = document.getElementById('calc-display');
  display.value = display.value === 'Error' ? '' : display.value.slice(0, -1);
  display.scrollLeft = display.scrollWidth;
}

function clearDisplay() {
  document.getElementById('calc-display').value = '';
}

let previousAnswer = '';

let isDegrees = true;
const modeIndicator = document.getElementById('calc-mode-indicator');
const modeToggleBtn = document.getElementById('toggle-mode-btn');

if (modeToggleBtn) {
  modeToggleBtn.addEventListener('click', () => {
    isDegrees = !isDegrees;
    modeIndicator.textContent = "Mode: " + (isDegrees ? "°" : "π");
  });
}

function toRadiansIfNeeded(expr) {
  return isDegrees ? `(${expr}) * Math.PI / 180` : expr;
}

function calculateResult() {
  const display = document.getElementById('calc-display');
  try {
    let expression = display.value
      .replace(
        /([\d.]+)×10\^([\-+]?\d+)/g,
        (_, coeff, exp) => `(${coeff}*(Math.pow(10,${exp})))`
      )
      // Inverse trig replacements first
      .replace(/sin⁻¹\(/g, 'asin(')
      .replace(/cos⁻¹\(/g, 'acos(')
      .replace(/tan⁻¹\(/g, 'atan(')
      // Clean Unicode
      .replace(/\u207B/g, '-')
      .replace(/\u00B9/g, '')
      // Basic operators
      .replace(/×/g, '*')
      .replace(/÷/g, '/')
      .replace(/Ans/g, previousAnswer || '0')
      .replace(/π/g, 'Math.PI');




    console.log("Pre-eval expression:", expression);

    // Handle normal ^ powers
    const powerRegex = /(\([^()]*\)|[\d.eE+-]+)\^(\([^()]*\)|[\d.eE+-]+)/;
    while (powerRegex.test(expression)) {
      expression = expression.replace(powerRegex, (_, base, exp) => {
        return `(Math.pow(${base}, ${exp}))`;
      });
    }

    // Trigonometric functions
    expression = expression
      .replace(/\bsin\(([^)]+)\)/g, (_, angle) => `Math.sin(${toRadiansIfNeeded(angle)})`)
      .replace(/\bcos\(([^)]+)\)/g, (_, angle) => `Math.cos(${toRadiansIfNeeded(angle)})`)
      .replace(/\btan\(([^)]+)\)/g, (_, angle) => `Math.tan(${toRadiansIfNeeded(angle)})`)
      .replace(/\basin\(([^)]+)\)/g, (_, val) => isDegrees ? `(Math.asin(${val}) * 180/Math.PI)` : `Math.asin(${val})`)
      .replace(/\bacos\(([^)]+)\)/g, (_, val) => isDegrees ? `(Math.acos(${val}) * 180/Math.PI)` : `Math.acos(${val})`)
      .replace(/\batan\(([^)]+)\)/g, (_, val) => isDegrees ? `(Math.atan(${val}) * 180/Math.PI)` : `Math.atan(${val})`)
      .replace(/√\(/g, 'Math.sqrt(')
      .replace(/log\(/g, 'Math.log10(')
      .replace(/ln\(/g, 'Math.log(')
      .replace(/exp\(/g, 'Math.exp(');

    console.log("Evaluating:", expression);

    const result = eval(expression);
    previousAnswer = result;

    display.value = (Math.abs(result) > 1000 || (Math.abs(result) < 0.001 && result !== 0))
      ? result.toExponential(6)
      : parseFloat(result.toFixed(8));
  } catch (err) {
    console.error("Eval error:", err.message);
    display.value = 'Error';
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

document.addEventListener('keydown', function (e) {
  const calculator = document.getElementById('calculator-container');
  const display = document.getElementById('calc-display');

  if (calculator.style.display !== 'block') return;

  const allowedKeys = {
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
    '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
    '.': '.', '+': '+', '-': '-', '*': '*', '/': '/',
    '(': '(', ')': ')'
  };

  if (e.key in allowedKeys) {
    insertToDisplay(allowedKeys[e.key]);
    e.preventDefault();
  } else if (e.key === 'Enter') {
    calculateResult();
    e.preventDefault();
  } else if (e.key === 'Backspace') {
    deleteLast();
    e.preventDefault();
  } else if (e.key === 'Escape') {
    clearDisplay();
    e.preventDefault();
  } else if (e.key === 'q') {
    insertToDisplay("Math.E"); // Electron charge or override
    e.preventDefault();
  } else if (e.key === 'c') {
    insertToDisplay("3.00e8");
    e.preventDefault();
  } else if (e.key === 'h') {
    insertToDisplay("6.626e-34");
    e.preventDefault();
  } else if (e.key === 'p') {
    insertToDisplay("π");
    e.preventDefault();
  } else if (e.key === 'k') {
    insertToDisplay("1.381e-23");
    e.preventDefault();
  } else if (e.key === 'G') {
    insertToDisplay("6.674e-11");
    e.preventDefault();
  } else if (e.key === 'R') {
    insertToDisplay("8.314");
    e.preventDefault();
  } else if (e.key === 'm') {
    insertToDisplay("9.109e-31");
    e.preventDefault();
  } else if (e.key === 'e') {
    insertToDisplay("×10^");
    e.preventDefault();
  }
});
