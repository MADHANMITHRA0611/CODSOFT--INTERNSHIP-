let expression = "";

function press(val) {
  expression += val;
  document.getElementById("display").value = expression;
}

function clearDisplay() {
  expression = "";
  document.getElementById("display").value = "";
}

function calculate() {
  fetch('/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ expression: expression })
  })
  .then(response => response.json())
  .then(data => {
    if (data.result !== undefined) {
      expression = data.result.toString();
      document.getElementById("display").value = expression;
    } else {
      document.getElementById("display").value = "Error";
      expression = "";
    }
  });
}

function toggleTheme() {
  document.body.classList.toggle("light");
}
