(function () {
  const root = document.getElementById("docs-picker");
  if (!root) return;

  const state = {
    answers: {},
    history: [],
    selected: [],
    current: null,
  };

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function render() {
    const data = window.DocsPickerEngine.nextStep(state.answers);
    state.history = data.history || [];
    state.answers = data.answers || state.answers;
    root.innerHTML = `
      <div class="docs-picker__layout">
        <aside class="docs-picker__rail">${renderRail(data)}</aside>
        <div class="docs-picker__main">
          <p class="docs-picker__step" id="docs-picker-step"></p>
          <div id="docs-picker-body"></div>
        </div>
      </div>`;
    bindRail();
    if (data.done) {
      renderPackage(data);
      return;
    }
    state.current = data;
    state.selected = Array.isArray(state.answers[data.question.id])
      ? [...state.answers[data.question.id]]
      : [];
    renderQuestion();
  }

  function renderRail(data) {
    const items = (data.history || [])
      .map(
        (item) => `
        <li>
          <button type="button" data-id="${escapeHtml(item.id)}">
            ${escapeHtml(item.title)}
            <small>${escapeHtml(item.labels.join(", "))}</small>
          </button>
        </li>`
      )
      .join("");
    return `
      <h3>Ваши ответы</h3>
      <ul class="docs-picker__history">${items || "<li class='docs-picker__hint'>Ответы появятся здесь</li>"}</ul>
      <div class="docs-picker__actions">
        <button type="button" class="docs-picker__ghost" data-reset>Начать заново</button>
      </div>`;
  }

  function bindRail() {
    root.querySelectorAll("[data-id]").forEach((btn) => {
      btn.addEventListener("click", () => rewind(btn.dataset.id));
    });
    const reset = root.querySelector("[data-reset]");
    if (reset) {
      reset.addEventListener("click", () => {
        state.answers = {};
        render();
      });
    }
  }

  function rewind(qid) {
    const keep = new Set();
    for (const item of state.history) {
      if (item.id === qid) break;
      keep.add(item.id);
    }
    state.answers = Object.fromEntries(
      Object.entries(state.answers).filter(([key]) => keep.has(key))
    );
    render();
  }

  function renderQuestion() {
    const data = state.current;
    const question = data.question;
    root.querySelector("#docs-picker-step").textContent = `Шаг ${data.step} из ${data.total}`;
    const options = question.options
      .map((opt) => {
        const on = state.selected.includes(opt.id) ? " is-on" : "";
        const input =
          question.type === "multi"
            ? `<input type="checkbox" ${state.selected.includes(opt.id) ? "checked" : ""} />`
            : `<input type="radio" name="docs-picker-opt" />`;
        return `<button type="button" class="docs-picker__option${on}" data-opt="${escapeHtml(opt.id)}">${input}<span>${escapeHtml(opt.label)}</span></button>`;
      })
      .join("");
    const links = (question.links || [])
      .map(
        (link) =>
          `<a href="${escapeHtml(link.url)}" target="_blank" rel="noreferrer">${escapeHtml(link.label)}</a>`
      )
      .join("");
    const extra =
      question.type === "multi"
        ? `<div class="docs-picker__actions"><button type="button" class="docs-picker__primary" data-next>Далее</button></div>`
        : "";
    const body = root.querySelector("#docs-picker-body");
    body.innerHTML = `
      <h2>${escapeHtml(question.title)}</h2>
      ${question.hint ? `<p class="docs-picker__hint">${escapeHtml(question.hint)}</p>` : ""}
      ${data.error ? `<p class="docs-picker__error">${escapeHtml(data.error)}</p>` : ""}
      <div class="docs-picker__options">${options}</div>
      ${links ? `<div class="docs-picker__links">${links}</div>` : ""}
      ${extra}`;
    body.querySelectorAll("[data-opt]").forEach((btn) => {
      btn.addEventListener("click", () => choose(question, btn.dataset.opt));
    });
    const next = body.querySelector("[data-next]");
    if (next) {
      next.addEventListener("click", () => {
        state.answers = { ...state.answers, [question.id]: [...state.selected] };
        render();
      });
    }
  }

  function choose(question, id) {
    if (question.type === "multi") {
      if (state.selected.includes(id)) {
        state.selected = state.selected.filter((item) => item !== id);
      } else {
        state.selected.push(id);
      }
      renderQuestion();
      return;
    }
    state.answers = { ...state.answers, [question.id]: id };
    render();
  }

  function renderPackage(data) {
    root.querySelector("#docs-picker-step").textContent = "Пакет документов";
    const groups = data.package.groups
      .map((group) => {
        const items = group.items
          .map((item) => {
            const note = item.note ? `<span>${escapeHtml(item.note)}</span>` : "";
            const url = item.url
              ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">Скачать бланк / открыть</a>`
              : "";
            return `<div class="docs-picker__item"><b>${escapeHtml(item.title)}</b>${note}${url}</div>`;
          })
          .join("");
        return `<section class="docs-picker__section"><h3>${escapeHtml(group.title)}</h3>${items}</section>`;
      })
      .join("");
    const channel = data.package.channel_url
      ? `<a href="${escapeHtml(data.package.channel_url)}" target="_blank" rel="noreferrer">Перейти к подаче документов</a>`
      : "";
    root.querySelector("#docs-picker-body").innerHTML = `
      <div class="docs-picker__package">
        <div class="docs-picker__package-head">
          <div>
            <h2>Итоговый список</h2>
            <p>${escapeHtml(data.package.notice || "")}</p>
            <p>${data.package.count} документ(ов) по выбранным условиям. ${channel}</p>
          </div>
          <button type="button" class="docs-picker__primary" data-print>Печать / PDF</button>
        </div>
        ${groups}
      </div>`;
    root.querySelector("[data-print]").addEventListener("click", () => window.print());
  }

  render();
})();
