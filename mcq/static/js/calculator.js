let calculatorVisible = false;

function toggleCalculator() {
  const calculator = document.getElementById('calculator-container');
  const currentQuestion = document.querySelector('.quiz-question[style*="block"]');

  if (calculator.style.display === 'block') {
    calculator.style.display = 'none';
    return; // exit early if it was already shown
  }

  // Otherwise show and position it
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

  const constants = {
    e_const: '1.602e-19',
    c_const: '3.00e8',
    h_const: '6.626e-34'
  };

  const inverseTrig = {
    'asin(': 'Math.asin(',
    'acos(': 'Math.acos(',
    'atan(': 'Math.atan('
  };

  if (constants[value]) {
    display.value += constants[value];
  } else if (inverseTrig[value]) {
    display.value += inverseTrig[value];
  } else if (value === '×10^') {
    display.value += '*10^';
  } else {
    const lastChar = display.value.slice(-1);
    const needsMultiplication = /^[a-zπe√(]/i.test(value);
    if (lastChar && !'+-*/^('.includes(lastChar) && needsMultiplication) {
      display.value += '*' + value;
    } else {
      display.value += value;
    }
  }

  // ✅ Ensure the input scrolls to the right
  setTimeout(() => {
    display.scrollLeft = display.scrollWidth;
  }, 0);
}



function deleteLast() {
  const display = document.getElementById('calc-display');
  display.value = display.value === 'Error' ? '' : display.value.slice(0, -1);
  display.scrollLeft = display.scrollWidth; // ✨ Also scroll after deleting
}


  

function clearDisplay() {
  document.getElementById('calc-display').value = '';
}

function deleteLast() {
  const display = document.getElementById('calc-display');
  display.value = display.value === 'Error' ? '' : display.value.slice(0, -1);
}

let previousAnswer = '';  // to store result for Ans

let isDegrees = true;  // default mode
const modeIndicator = document.getElementById('calc-mode-indicator');
const modeToggleBtn = document.getElementById('toggle-mode-btn');

if (modeToggleBtn) {
  modeToggleBtn.addEventListener('click', () => {
    isDegrees = !isDegrees;
    modeIndicator.textContent = "Mode: " + (isDegrees ? "°" : "π");
  });
}

// Helper function to wrap angles in radians if needed
function toRadiansIfNeeded(expr) {
  return isDegrees ? `(${expr}) * Math.PI / 180` : expr;
}

// Override trig replacements in your calculateResult()
function calculateResult() {
  const display = document.getElementById('calc-display');
  try {
    let expression = display.value
      .replace(/×/g, '*')
      .replace(/÷/g, '/')
      .replace(/Ans/g, previousAnswer || '0');

    // Handle ×10^X as scientific notation
    expression = expression.replace(/(\d+(?:\.\d+)?)\*10\^(-?\d+)/g, (_, base, exp) => {
      return `(${base} * Math.pow(10, ${exp}))`;
    });

    // Trig conversions
    expression = expression
    .replace(/×/g, '*')
    .replace(/÷/g, '/')
    .replace(/Ans/g, previousAnswer || '0')
    .replace(/sin\(([^)]+)\)/g, (_, angle) => `Math.sin(${toRadiansIfNeeded(angle)})`)
    .replace(/cos\(([^)]+)\)/g, (_, angle) => `Math.cos(${toRadiansIfNeeded(angle)})`)
    .replace(/tan\(([^)]+)\)/g, (_, angle) => `Math.tan(${toRadiansIfNeeded(angle)})`)
    .replace(/asin\(([^)]+)\)/g, (_, val) => isDegrees ? `(Math.asin(${val}) * 180 / Math.PI)` : `Math.asin(${val})`)
    .replace(/acos\(([^)]+)\)/g, (_, val) => isDegrees ? `(Math.acos(${val}) * 180 / Math.PI)` : `Math.acos(${val})`)
    .replace(/atan\(([^)]+)\)/g, (_, val) => isDegrees ? `(Math.atan(${val}) * 180 / Math.PI)` : `Math.atan(${val})`)
    .replace(/log\(/g, 'Math.log10(')
    .replace(/ln\(/g, 'Math.log(')
    .replace(/exp\(/g, 'Math.exp(')
    .replace(/√\(/g, 'Math.sqrt(')
    .replace(/π/g, 'Math.PI')
    .replace(/(?<![\w.])e(?![\w.])/g, 'Math.E') // Euler's number only, not part of scientific notation
    .replace(/(\d+)\^2/g, 'Math.pow($1, 2)')
    .replace(/([0-9.]+|\([^()]+\))\^(-?[0-9.]+)/g, 'Math.pow($1, $2)')
    // .replace(/(?<![eE])10\^(-?\d+)/g, 'Math.pow(10, $1)');


    console.log("Evaluating:", expression);
    const result = eval(expression);
    previousAnswer = result;

    display.value = (Math.abs(result) > 1000 || (Math.abs(result) < 0.01 && result !== 0))
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
      insertToDisplay("1.602e-19");  // electron charge
      e.preventDefault();
    } else if (e.key === 'c') {
      insertToDisplay("3.00e8");  // speed of light
      e.preventDefault();
    } else if (e.key === 'h') {
      insertToDisplay("6.626e-34");  // Planck's constant
      e.preventDefault();
    } else if (e.key === 'p') {
      insertToDisplay("π");
      e.preventDefault();
    } else if (e.key === 'k') {
      insertToDisplay("1.381e-23");  // Boltzmann constant
      e.preventDefault();
    } else if (e.key === 'G') {
      insertToDisplay("6.674e-11");  // Gravitational constant
      e.preventDefault();
    } else if (e.key === 'R') {
      insertToDisplay("8.314");  // Ideal gas constant
      e.preventDefault();
    } else if (e.key === 'm') {
      insertToDisplay("9.109e-31");  // Electron mass
      e.preventDefault();
    } else if (e.key === 'e') {
      insertToDisplay("×10^");  // Scientific notation
      e.preventDefault();
    }
  });
  