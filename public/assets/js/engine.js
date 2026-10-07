(function (global) {
  function scheme() {
    return global.DOCS_PICKER_SCHEME;
  }

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function question(id, title, extra) {
    return Object.assign(
      { id, title, type: "single", hint: "", options: [], links: [] },
      extra || {}
    );
  }

  function questionVisible(qid, answers) {
    if (qid === "family") return answers.form === "ip";
    if (qid === "spouse_tax") return answers.form === "ip" && answers.family === "spouse_ip";
    if (qid === "owner") return Boolean(answers.collateral && answers.collateral.length);
    return true;
  }

  function buildQuestion(qid, answers) {
    const data = scheme();
    if (qid === "amount") {
      return question(qid, "Сумма займа", {
        hint: data.collateralRequired,
        options: [
          { id: "lt1m", label: "до 1 000 000" },
          { id: "gt1m", label: "от 1 000 000 до 5 000 000" },
        ],
      });
    }
    if (qid === "channel") {
      return question(qid, "Способ подачи документов", {
        hint: "Ссылку можно открыть в новой вкладке. После подачи вернитесь сюда и продолжите подбор пакета.",
        options: [
          { id: "msp", label: "Цифровая платформа МСП" },
          { id: "office", label: "Офис Фонда" },
        ],
        links: [
          { label: "Платформа МСП", url: data.urls.msp },
          { label: "Способы подачи в Фонд", url: data.urls.office },
        ],
      });
    }
    if (qid === "form") {
      return question(qid, "Организационно-правовая форма", {
        options: [
          { id: "ip", label: "Индивидуальный предприниматель или Глава КФХ" },
          { id: "ul", label: "Юридическое лицо" },
        ],
      });
    }
    if (qid === "tax") {
      const mspIp = answers.channel === "msp" && answers.form === "ip";
      return question(qid, mspIp ? "Система налогообложения (за последние два года)" : "Система налогообложения", {
        type: "multi",
        hint: "Можно выбрать несколько вариантов, если режимы применялись в разные периоды.",
        options: clone(answers.form === "ip" ? data.taxIp : data.taxUl),
      });
    }
    if (qid === "term") {
      return question(qid, "Срок ведения деятельности", {
        options: [
          { id: "lt3", label: "Менее 3 месяцев" },
          { id: "ge3", label: "3 месяца и более" },
        ],
      });
    }
    if (qid === "family") {
      return question(qid, "Семейное положение", {
        hint: "От этого зависит пакет поручительства супруга.",
        options: [
          { id: "spouse_ip", label: "Супруг(а) является ИП" },
          { id: "spouse_no", label: "Супруг(а) не являются ИП" },
          { id: "single", label: "Не состою в браке" },
        ],
      });
    }
    if (qid === "spouse_tax") {
      return question(qid, "Система налогообложения супруга(-ги)", {
        type: "multi",
        hint: "Можно выбрать несколько вариантов.",
        options: clone(data.taxIp),
      });
    }
    if (qid === "refinance") {
      return question(
        qid,
        "Цель использования займа: рефинансирование кредита на осуществление предпринимательской деятельности",
        {
          hint: "Если да, в пакет войдут кредитный договор, банковская справка и документы о целевом использовании.",
          options: [
            { id: "yes", label: "Да" },
            { id: "no", label: "Нет" },
          ],
        }
      );
    }
    if (qid === "collateral") {
      return question(qid, "Предлагаемое обеспечение", {
        type: "multi",
        hint:
          answers.amount === "gt1m"
            ? data.collateralRequired
            : "Можно выбрать несколько видов обеспечения или пропустить, если залога нет.",
        options: [
          { id: "realty", label: "Нежилое недвижимое имущество, находящееся на территории ХМАО-Югры" },
          { id: "vehicle", label: "Транспортное средство, спецтехника, находящееся на территории ХМАО-Югры" },
        ],
      });
    }
    if (qid === "owner") {
      return question(qid, "Залог принадлежит", {
        options: [
          { id: "borrower", label: "Заемщику" },
          { id: "citizen", label: "Третьему лицу – гражданину" },
          { id: "legal", label: "Третьему лицу – юридическому лицу" },
        ],
      });
    }
    throw new Error("Unknown question: " + qid);
  }

  function optionLabel(qid, value, answers) {
    const found = buildQuestion(qid, answers).options.find((opt) => opt.id === value);
    return found ? found.label : value;
  }

  function sanitizeAnswers(raw) {
    const answers = Object.assign({}, raw || {});
    if (answers.form !== "ip") {
      delete answers.family;
      delete answers.spouse_tax;
    }
    if (answers.family !== "spouse_ip") delete answers.spouse_tax;
    if (!answers.collateral || !answers.collateral.length) delete answers.owner;
    return answers;
  }

  function remainingAfter(current, answers) {
    let started = false;
    let count = 0;
    scheme().questionOrder.forEach((qid) => {
      if (qid === current) {
        started = true;
        return;
      }
      if (!started) return;
      if (questionVisible(qid, answers)) count += 1;
    });
    return count;
  }

  function matches(when, answers) {
    return Object.keys(when).every((key) => {
      const expected = when[key];
      const value = answers[key];
      if (Array.isArray(expected)) {
        const selected = Array.isArray(value) ? value : value ? [value] : [];
        return expected.some((item) => selected.includes(item));
      }
      return value === expected;
    });
  }

  function buildPackage(answers) {
    const data = scheme();
    const groups = {};
    data.sectionOrder.forEach((name) => {
      groups[name] = [];
    });
    const seen = new Set();
    data.documents.forEach((item) => {
      if (!matches(item.when, answers)) return;
      const key = [item.section, item.title, item.note || "", item.url || ""].join("\t");
      if (seen.has(key)) return;
      seen.add(key);
      groups[item.section].push({
        title: item.title,
        note: item.note || "",
        url: item.url || "",
      });
    });
    return {
      count: Object.values(groups).reduce((sum, items) => sum + items.length, 0),
      notice: data.packageNotice,
      channel: answers.channel,
      channel_url: data.urls[answers.channel] || "",
      groups: data.sectionOrder
        .filter((name) => groups[name].length)
        .map((name) => ({ title: name, items: groups[name] })),
    };
  }

  function nextStep(rawAnswers) {
    const data = scheme();
    let answers = sanitizeAnswers(rawAnswers);
    let error = null;
    if (answers.amount === "gt1m" && Object.prototype.hasOwnProperty.call(rawAnswers || {}, "collateral")) {
      if (!answers.collateral || !answers.collateral.length) {
        error = data.collateralRequired;
        delete answers.collateral;
      }
    }

    const history = [];
    let current = null;
    for (const qid of data.questionOrder) {
      if (!questionVisible(qid, answers)) continue;
      if (!(qid in answers) || (error && qid === "collateral")) {
        current = qid;
        break;
      }
      const value = answers[qid];
      const labels = Array.isArray(value)
        ? value.map((item) => optionLabel(qid, item, answers))
        : [optionLabel(qid, value, answers)];
      history.push({
        id: qid,
        title: buildQuestion(qid, answers).title,
        labels,
      });
    }

    if (current) {
      return {
        done: false,
        question: buildQuestion(current, answers),
        error,
        answers,
        history,
        step: history.length + 1,
        total: history.length + 1 + remainingAfter(current, answers),
      };
    }

    return {
      done: true,
      question: null,
      error: null,
      answers,
      history,
      step: history.length,
      total: history.length,
      package: buildPackage(answers),
    };
  }

  global.DocsPickerEngine = { nextStep };
})(window);
