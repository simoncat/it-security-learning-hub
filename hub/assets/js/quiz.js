(function () {
  var dataNode = document.getElementById("quiz-data");
  var root = document.getElementById("quiz-root");
  if (!dataNode || !root) return;

  var data = JSON.parse(dataNode.textContent);
  var questions = data.questions || [];
  var selections = {};

  questions.forEach(function (question) {
    var fieldset = document.createElement("fieldset");
    fieldset.className = "q";
    fieldset.dataset.qid = question.id;

    var legend = document.createElement("legend");
    if (question.modalityTag) {
      var badge = document.createElement("span");
      badge.className = "badge badge-" + question.modalityTag;
      badge.textContent = question.modalityTag === "appc" ? "App C" : question.modalityTag.charAt(0).toUpperCase() + question.modalityTag.slice(1);
      legend.appendChild(badge);
      legend.appendChild(document.createTextNode(" "));
    }
    legend.appendChild(document.createTextNode(question.prompt));
    fieldset.appendChild(legend);

    question.choices.forEach(function (choice, index) {
      var label = document.createElement("label");
      var input = document.createElement("input");
      input.type = "radio";
      input.name = question.id;
      input.value = String(index);
      input.addEventListener("change", function () { selections[question.id] = index; });
      label.appendChild(input);
      label.appendChild(document.createTextNode(" " + choice));
      fieldset.appendChild(label);
    });

    var rationale = document.createElement("p");
    rationale.className = "rationale";
    rationale.hidden = true;
    rationale.textContent = question.rationale;
    fieldset.appendChild(rationale);
    root.appendChild(fieldset);
  });

  var scoreBox = document.createElement("div");
  scoreBox.className = "score-box";
  scoreBox.hidden = true;
  scoreBox.setAttribute("aria-live", "polite");
  var actions = document.createElement("div");
  actions.className = "toolbar no-print";
  var scoreBtn = document.createElement("button");
  scoreBtn.type = "button";
  scoreBtn.className = "btn btn-primary";
  scoreBtn.textContent = "Check score";
  var resetBtn = document.createElement("button");
  resetBtn.type = "button";
  resetBtn.className = "btn btn-ghost";
  resetBtn.textContent = "Reset";
  actions.appendChild(scoreBtn);
  actions.appendChild(resetBtn);
  root.before(actions);
  root.after(scoreBox);

  function clearMarks() {
    root.querySelectorAll(".q").forEach(function (fieldset) {
      fieldset.classList.remove("is-scored");
      fieldset.querySelectorAll("label").forEach(function (label) {
        label.classList.remove("is-correct", "is-wrong");
      });
      var rationale = fieldset.querySelector(".rationale");
      if (rationale) rationale.hidden = true;
    });
    scoreBox.hidden = true;
    scoreBox.textContent = "";
  }

  scoreBtn.addEventListener("click", function () {
    var correct = 0;
    var answered = 0;
    questions.forEach(function (question) {
      var fieldset = root.querySelector('[data-qid="' + question.id + '"]');
      var chosen = Object.prototype.hasOwnProperty.call(selections, question.id) ? selections[question.id] : null;
      if (chosen !== null) answered += 1;
      if (chosen === question.answerIndex) correct += 1;
      fieldset.classList.add("is-scored");
      fieldset.querySelectorAll("label").forEach(function (label, index) {
        label.classList.toggle("is-correct", index === question.answerIndex);
        label.classList.toggle("is-wrong", chosen === index && index !== question.answerIndex);
      });
      fieldset.querySelector(".rationale").hidden = false;
    });
    scoreBox.hidden = false;
    scoreBox.textContent = "";
    var title = document.createElement("p");
    title.textContent = "Score: " + correct + " of " + questions.length + ".";
    var detail = document.createElement("p");
    detail.textContent = "Answered " + answered + " of " + questions.length + ". Unanswered questions count as not correct. Nothing is submitted.";
    scoreBox.appendChild(title);
    scoreBox.appendChild(detail);
  });

  resetBtn.addEventListener("click", function () {
    selections = {};
    root.querySelectorAll("input[type='radio']").forEach(function (input) { input.checked = false; });
    clearMarks();
  });
})();
