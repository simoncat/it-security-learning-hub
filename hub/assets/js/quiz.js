(function () {
  var dataNode = document.getElementById("quiz-data");
  var root = document.getElementById("quiz-root");
  if (!dataNode || !root) return;

  var pageId = String(document.body.getAttribute("data-page-id") || "").slice(0, 80);
  if (!/^[A-Za-z0-9._:-]{1,80}$/.test(pageId)) pageId = "";
  var QUIZ_PREFIX = "hksarg-hub:quiz:";
  var quizKey = pageId ? QUIZ_PREFIX + pageId : "";

  var data = {};
  try {
    data = JSON.parse(dataNode.textContent) || {};
  } catch (err) {
    root.textContent = "This self-check could not load.";
    return;
  }
  var questions = Array.isArray(data.questions) ? data.questions : [];
  var selections = {};
  var allowedMod = { shall: true, should: true, may: true, appc: true };

  function quizTitle() {
    var heading = document.querySelector("main h1");
    if (heading && heading.textContent) return String(heading.textContent).trim().slice(0, 160);
    return String(document.title || pageId || "Quiz").replace(/\s*·.*$/, "").trim().slice(0, 160);
  }

  function readStored() {
    if (!quizKey) return null;
    try {
      var raw = localStorage.getItem(quizKey);
      if (!raw || raw.length > 200000) return null;
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
      return parsed;
    } catch (err) {
      return null;
    }
  }

  function writeStored(record) {
    if (!quizKey) return;
    try {
      localStorage.setItem(quizKey, JSON.stringify(record));
    } catch (err) {}
  }

  function clearStored() {
    if (!quizKey) return;
    try {
      localStorage.removeItem(quizKey);
    } catch (err) {}
  }

  questions.forEach(function (question) {
    if (!question || typeof question !== "object") return;
    var fieldset = document.createElement("fieldset");
    fieldset.className = "q";
    var qid = String(question.id || "").replace(/[^\w.-]/g, "").slice(0, 64);
    if (!qid) return;
    fieldset.dataset.qid = qid;

    var legend = document.createElement("legend");
    if (question.modalityTag && allowedMod[question.modalityTag]) {
      var badge = document.createElement("span");
      badge.className = "badge badge-" + question.modalityTag;
      badge.textContent = question.modalityTag === "appc" ? "App C" : question.modalityTag.charAt(0).toUpperCase() + question.modalityTag.slice(1);
      legend.appendChild(badge);
      legend.appendChild(document.createTextNode(" "));
    }
    legend.appendChild(document.createTextNode(String(question.prompt || "")));
    fieldset.appendChild(legend);

    (Array.isArray(question.choices) ? question.choices : []).forEach(function (choice, index) {
      var label = document.createElement("label");
      var input = document.createElement("input");
      input.type = "radio";
      input.name = qid;
      input.value = String(index);
      input.addEventListener("change", function () { selections[qid] = index; });
      label.appendChild(input);
      label.appendChild(document.createTextNode(" " + String(choice || "")));
      fieldset.appendChild(label);
    });

    var rationale = document.createElement("p");
    rationale.className = "rationale";
    rationale.hidden = true;
    rationale.textContent = String(question.rationale || "");
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

  function applyScore(persist) {
    var correct = 0;
    var answered = 0;
    questions.forEach(function (question) {
      if (!question || typeof question !== "object") return;
      var qid = String(question.id || "").replace(/[^\w.-]/g, "").slice(0, 64);
      if (!qid) return;
      var fieldset = root.querySelector('[data-qid="' + qid + '"]');
      if (!fieldset) return;
      var chosen = Object.prototype.hasOwnProperty.call(selections, qid) ? selections[qid] : null;
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

    if (persist && quizKey) {
      var cleanSelections = {};
      Object.keys(selections).forEach(function (qid) {
        var value = selections[qid];
        if (typeof value !== "number" || !isFinite(value)) return;
        cleanSelections[qid] = value;
      });
      writeStored({
        quizId: pageId,
        title: quizTitle(),
        scoredAt: new Date().toISOString(),
        correct: correct,
        answered: answered,
        total: questions.length,
        selections: cleanSelections
      });
    }
  }

  function restoreFromStorage() {
    var stored = readStored();
    if (!stored) return;
    var saved = stored.selections;
    if (!saved || typeof saved !== "object" || Array.isArray(saved)) return;
    Object.keys(saved).forEach(function (qid) {
      var index = saved[qid];
      if (typeof index !== "number" || !isFinite(index)) return;
      var input = root.querySelector('input[name="' + qid + '"][value="' + String(index) + '"]');
      if (!input) return;
      input.checked = true;
      selections[qid] = index;
    });
    if (Object.keys(selections).length || typeof stored.correct === "number") {
      applyScore(false);
    }
  }

  scoreBtn.addEventListener("click", function () {
    applyScore(true);
  });

  resetBtn.addEventListener("click", function () {
    selections = {};
    root.querySelectorAll("input[type='radio']").forEach(function (input) { input.checked = false; });
    clearMarks();
    clearStored();
  });

  restoreFromStorage();
})();
