(function (root) {
  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function createDocsPicker(scheme) {
    function question(id, title, extra) {
      return Object.assign(
        { id: id, title: title, type: "single", hint: "", options: [], links: [] },
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
      if (qid === "amount") {
        return question(qid, "Сумма займа", {
          hint: scheme.collateralRequired,
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
            { label: "Платформа МСП", url: scheme.urls.msp },
            { label: "Способы подачи в Фонд", url: scheme.urls.office },
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
        var mspIp = answers.channel === "msp" && answers.form === "ip";
        return question(qid, mspIp ? "Система налогообложения (за последние два года)" : "Система налогообложения", {
          type: "multi",
          hint: "Можно выбрать несколько вариантов, если режимы применялись в разные периоды.",
          options: clone(answers.form === "ip" ? scheme.taxIp : scheme.taxUl),
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
          options: clone(scheme.taxIp),
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
              ? scheme.collateralRequired
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
      var found = buildQuestion(qid, answers).options.filter(function (opt) {
        return opt.id === value;
      })[0];
      return found ? found.label : value;
    }

    function sanitizeAnswers(raw) {
      var answers = Object.assign({}, raw || {});
      if (answers.form !== "ip") {
        delete answers.family;
        delete answers.spouse_tax;
      }
      if (answers.family !== "spouse_ip") delete answers.spouse_tax;
      if (!answers.collateral || !answers.collateral.length) delete answers.owner;
      return answers;
    }

    function remainingAfter(current, answers) {
      var started = false;
      var count = 0;
      scheme.questionOrder.forEach(function (qid) {
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
      return Object.keys(when).every(function (key) {
        var expected = when[key];
        var value = answers[key];
        if (Array.isArray(expected)) {
          var selected = Array.isArray(value) ? value : value ? [value] : [];
          return expected.some(function (item) {
            return selected.indexOf(item) !== -1;
          });
        }
        return value === expected;
      });
    }

    function buildPackage(answers) {
      var groups = {};
      scheme.sectionOrder.forEach(function (name) {
        groups[name] = [];
      });
      var seen = {};
      scheme.documents.forEach(function (item) {
        if (!matches(item.when, answers)) return;
        var key = [item.section, item.title, item.note || "", item.url || ""].join("\t");
        if (seen[key]) return;
        seen[key] = true;
        groups[item.section].push({
          title: item.title,
          note: item.note || "",
          url: item.url || "",
        });
      });
      var count = 0;
      var outGroups = [];
      scheme.sectionOrder.forEach(function (name) {
        count += groups[name].length;
        if (groups[name].length) outGroups.push({ title: name, items: groups[name] });
      });
      return {
        count: count,
        notice: scheme.packageNotice,
        channel: answers.channel,
        channel_url: scheme.urls[answers.channel] || "",
        groups: outGroups,
      };
    }

    function nextStep(rawAnswers) {
      var answers = sanitizeAnswers(rawAnswers);
      var error = null;
      if (answers.amount === "gt1m" && Object.prototype.hasOwnProperty.call(rawAnswers || {}, "collateral")) {
        if (!answers.collateral || !answers.collateral.length) {
          error = scheme.collateralRequired;
          delete answers.collateral;
        }
      }

      var history = [];
      var current = null;
      for (var i = 0; i < scheme.questionOrder.length; i += 1) {
        var qid = scheme.questionOrder[i];
        if (!questionVisible(qid, answers)) continue;
        if (!(qid in answers) || (error && qid === "collateral")) {
          current = qid;
          break;
        }
        var value = answers[qid];
        var labels = Array.isArray(value)
          ? value.map(function (item) {
              return optionLabel(qid, item, answers);
            })
          : [optionLabel(qid, value, answers)];
        history.push({
          id: qid,
          title: buildQuestion(qid, answers).title,
          labels: labels,
        });
      }

      if (current) {
        return {
          done: false,
          question: buildQuestion(current, answers),
          error: error,
          answers: answers,
          history: history,
          step: history.length + 1,
          total: history.length + 1 + remainingAfter(current, answers),
          package: null,
        };
      }

      return {
        done: true,
        question: null,
        error: null,
        answers: answers,
        history: history,
        step: history.length,
        total: history.length,
        package: buildPackage(answers),
      };
    }

    function answer(answers, questionId, value) {
      var next = Object.assign({}, answers || {});
      next[questionId] = value;
      return nextStep(next);
    }

    function rewind(answers, questionId) {
      var step = nextStep(answers);
      var keep = {};
      for (var i = 0; i < step.history.length; i += 1) {
        if (step.history[i].id === questionId) break;
        keep[step.history[i].id] = true;
      }
      var filtered = {};
      Object.keys(answers || {}).forEach(function (key) {
        if (keep[key]) filtered[key] = answers[key];
      });
      return nextStep(filtered);
    }

    return {
      start: function () {
        return nextStep({});
      },
      nextStep: nextStep,
      answer: answer,
      rewind: rewind,
    };
  }

  var api = { create: createDocsPicker };
  root.DocsPicker = api;
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
