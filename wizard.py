from __future__ import annotations

from copy import deepcopy

URLS = {
    "msp": "https://мсп.рф/services/microloan/",
    "office": "https://fundmicro86.ru/clients/sposobi.php",
    "app_ip": "https://fundmicro86.ru/upload/31890/Zayavlenie_anketa_na_poluchenie_mikrozayma_dlya_IP.XLSX",
    "app_ul": "https://fundmicro86.ru/upload/Zayavlenie_Anketa_na_zaym_YUL.XLSX",
    "consent": "https://fundmicro86.ru/upload/Soglasie_po_obrabotke_PD_ot_14.05.2026.docx",
    "income_12": "https://cloud.mail.ru/public/aoxY/5kzUjdZVN",
    "income_6": "https://fundmicro86.ru/upload/Svedeniya_o_dokhodakh_raskhodakh_za_6_mes..xlsx",
    "teo": "https://fundmicro86.ru/upload/TEO_Biznes_plan_srok_deyatelnosti_menee_3_mesyatsev.xlsx",
    "anketa_ul": "https://fundmicro86.ru/upload/information/Anketa_poruchitelya_zalogodatelya_YUL_IP_glavy_KFKH.XLS",
    "anketa_fl": "https://fundmicro86.ru/upload/32253/Anketa_poruchitelya_zalogodatelya_FL.xls",
}

TAX_IP = [
    {"id": "usn", "label": "Упрощенная система налогообложения (УСН)"},
    {"id": "eshn", "label": "Единый сельскохозяйственный налог (ЕСХН)"},
    {"id": "patent", "label": "Патентная система налогообложения (ПСН)"},
    {"id": "npd", "label": "Налог на профессиональный доход (НПД)"},
    {"id": "auto_usn", "label": "Автоматизированная упрощённая система налогообложения (АУСН)"},
    {"id": "osno", "label": "Общая система налогообложения (ОСНО)"},
]

TAX_UL = [
    {"id": "osno", "label": "Общая система налогообложения (ОСНО)"},
    {"id": "usn", "label": "Упрощенная система налогообложения (УСН)"},
    {"id": "eshn", "label": "Единый сельскохозяйственный налог (ЕСХН)"},
    {"id": "auto_usn", "label": "Автоматизированная упрощённая система налогообложения (АУСН)"},
]

QUESTION_ORDER = [
    "amount",
    "channel",
    "form",
    "tax",
    "term",
    "family",
    "spouse_tax",
    "refinance",
    "collateral",
    "owner",
]

COLLATERAL_REQUIRED = "Наличие залога является обязательным в случае, если сумма займа более 1 000 000 руб."
PACKAGE_NOTICE = "Данный перечень является базовым. Фонд может запросить дополнительные документы."


def _q(qid, title, *, qtype="single", hint="", options=None, links=None):
    return {
        "id": qid,
        "title": title,
        "type": qtype,
        "hint": hint,
        "options": options or [],
        "links": links or [],
    }


def question_visible(qid: str, answers: dict) -> bool:
    if qid == "family":
        return answers.get("form") == "ip"
    if qid == "spouse_tax":
        return answers.get("form") == "ip" and answers.get("family") == "spouse_ip"
    if qid == "owner":
        return bool(answers.get("collateral"))
    return True


def build_question(qid: str, answers: dict) -> dict:
    if qid == "amount":
        return _q(
            qid,
            "Сумма займа",
            hint=COLLATERAL_REQUIRED,
            options=[
                {"id": "lt1m", "label": "до 1 000 000"},
                {"id": "gt1m", "label": "от 1 000 000 до 5 000 000"},
            ],
        )
    if qid == "channel":
        return _q(
            qid,
            "Способ подачи документов",
            hint="Ссылку можно открыть в новой вкладке. После подачи вернитесь сюда и продолжите подбор пакета.",
            options=[
                {"id": "msp", "label": "Цифровая платформа МСП"},
                {"id": "office", "label": "Офис Фонда"},
            ],
            links=[
                {"label": "Платформа МСП", "url": URLS["msp"]},
                {"label": "Способы подачи в Фонд", "url": URLS["office"]},
            ],
        )
    if qid == "form":
        return _q(
            qid,
            "Организационно-правовая форма",
            options=[
                {"id": "ip", "label": "Индивидуальный предприниматель или Глава КФХ"},
                {"id": "ul", "label": "Юридическое лицо"},
            ],
        )
    if qid == "tax":
        msp_ip = answers.get("channel") == "msp" and answers.get("form") == "ip"
        title = (
            "Система налогообложения (за последние два года)"
            if msp_ip
            else "Система налогообложения"
        )
        options = deepcopy(TAX_IP if answers.get("form") == "ip" else TAX_UL)
        return _q(
            qid,
            title,
            qtype="multi",
            hint="Можно выбрать несколько вариантов, если режимы применялись в разные периоды.",
            options=options,
        )
    if qid == "term":
        return _q(
            qid,
            "Срок ведения деятельности",
            options=[
                {"id": "lt3", "label": "Менее 3 месяцев"},
                {"id": "ge3", "label": "3 месяца и более"},
            ],
        )
    if qid == "family":
        return _q(
            qid,
            "Семейное положение",
            hint="От этого зависит пакет поручительства супруга.",
            options=[
                {"id": "spouse_ip", "label": "Супруг(а) является ИП"},
                {"id": "spouse_no", "label": "Супруг(а) не являются ИП"},
                {"id": "single", "label": "Не состою в браке"},
            ],
        )
    if qid == "spouse_tax":
        return _q(
            qid,
            "Система налогообложения супруга(-ги)",
            qtype="multi",
            hint="Можно выбрать несколько вариантов.",
            options=deepcopy(TAX_IP),
        )
    if qid == "refinance":
        return _q(
            qid,
            "Цель использования займа: рефинансирование кредита на осуществление предпринимательской деятельности",
            hint="Если да, в пакет войдут кредитный договор, банковская справка и документы о целевом использовании.",
            options=[
                {"id": "yes", "label": "Да"},
                {"id": "no", "label": "Нет"},
            ],
        )
    if qid == "collateral":
        hint = COLLATERAL_REQUIRED if answers.get("amount") == "gt1m" else "Можно выбрать несколько видов обеспечения или пропустить, если залога нет."
        return _q(
            qid,
            "Предлагаемое обеспечение",
            qtype="multi",
            hint=hint,
            options=[
                {
                    "id": "realty",
                    "label": "Нежилое недвижимое имущество, находящееся на территории ХМАО-Югры",
                },
                {
                    "id": "vehicle",
                    "label": "Транспортное средство, спецтехника, находящееся на территории ХМАО-Югры",
                },
            ],
        )
    if qid == "owner":
        return _q(
            qid,
            "Залог принадлежит",
            options=[
                {"id": "borrower", "label": "Заемщику"},
                {"id": "citizen", "label": "Третьему лицу – гражданину"},
                {"id": "legal", "label": "Третьему лицу – юридическому лицу"},
            ],
        )
    raise KeyError(qid)


def option_label(qid: str, value: str, answers: dict) -> str:
    question = build_question(qid, answers)
    for opt in question["options"]:
        if opt["id"] == value:
            return opt["label"]
    return value


def sanitize_answers(raw: dict) -> dict:
    answers = dict(raw or {})
    if answers.get("form") != "ip":
        answers.pop("family", None)
        answers.pop("spouse_tax", None)
    if answers.get("family") != "spouse_ip":
        answers.pop("spouse_tax", None)
    if not answers.get("collateral"):
        answers.pop("owner", None)
    return answers


def next_step(raw_answers: dict) -> dict:
    answers = sanitize_answers(raw_answers)
    error = None
    if answers.get("amount") == "gt1m" and "collateral" in raw_answers:
        if not answers.get("collateral"):
            error = COLLATERAL_REQUIRED
            answers.pop("collateral", None)

    history = []
    current = None
    for qid in QUESTION_ORDER:
        if not question_visible(qid, answers):
            continue
        if qid not in answers or error and qid == "collateral":
            current = qid
            break
        value = answers[qid]
        labels = (
            [option_label(qid, item, answers) for item in value]
            if isinstance(value, list)
            else [option_label(qid, value, answers)]
        )
        history.append(
            {
                "id": qid,
                "title": build_question(qid, answers)["title"],
                "labels": labels,
            }
        )

    if current:
        question = build_question(current, answers)
        return {
            "done": False,
            "question": question,
            "error": error,
            "answers": answers,
            "history": history,
            "step": len(history) + 1,
            "total": len(history) + 1 + _remaining_after(current, answers),
        }

    package = build_package(answers)
    return {
        "done": True,
        "question": None,
        "error": None,
        "answers": answers,
        "history": history,
        "step": len(history),
        "total": len(history),
        "package": package,
    }


def _remaining_after(current: str, answers: dict) -> int:
    started = False
    count = 0
    probe = dict(answers)
    for qid in QUESTION_ORDER:
        if qid == current:
            started = True
            continue
        if not started:
            continue
        if question_visible(qid, probe):
            count += 1
    return count


def _doc(title, *, note="", url="", section="Заёмщик", **when):
    return {
        "title": title,
        "note": note,
        "url": url,
        "section": section,
        "when": when,
    }


def _catalog() -> list[dict]:
    docs: list[dict] = []

    docs += [
        _doc("Заявление-анкета на получение микрозайма + приложение (вторая закладка в Excel)", url=URLS["app_ip"], form="ip"),
        _doc("Паспорт (все страницы)", form="ip"),
        _doc("Согласие на обработку персональных данных", url=URLS["consent"], form="ip"),
        _doc("Карточка предприятия (реквизиты с подписью и печатью)", form="ip"),
        _doc("Выписки по всем расчётным счетам с назначением платежей (Excel)", note="за последние 12 месяцев", form="ip", channel="msp"),
        _doc("Выписки по всем расчётным счетам с назначением платежей (Excel)", note="не менее 6 последних месяцев", form="ip", channel="office"),
        _doc("Отчёт по онлайн-кассе с разбивкой помесячно", note="не менее 6 последних месяцев, если применение онлайн-кассы обязательно", form="ip", channel="msp"),
        _doc("Отчёт по онлайн-кассе (Excel) или копия книги учёта доходов и расходов / хозяйственных операций, если онлайн-кассы нет", note="не менее 6 последних месяцев", form="ip", channel="office"),
        _doc("Книга учёта доходов и расходов и/или хозяйственных операций (Excel)", note="за предыдущий год и на текущий год с 1 января до месяца подачи заявки", form="ip", channel="msp"),
        _doc("Сведения о доходах и расходах", note="за последние 12 месяцев", url=URLS["income_12"], form="ip", channel="msp"),
        _doc("Сведения о доходах и расходах", note="не менее 6 последних месяцев", url=URLS["income_6"], form="ip", channel="office"),
        _doc("Справка об исполнении обязанности по уплате налогов, сборов, страховых взносов, пеней, штрафов, процентов (ЭЦП или оригинал)", note="при наличии задолженности приложите подтверждающие документы", form="ip"),
        _doc("Справка ФНС о сальдо единого налогового счёта", form="ip"),
        _doc("Лицензия", note="при наличии", form="ip"),
        _doc("Отзывы контрагентов в произвольной письменной форме", note="при наличии", form="ip"),
        _doc("Страница 001 формы «Расчёт страховых взносов» — при наличии сотрудников; иначе заявление об отсутствии сотрудников", note="за последний отчётный период", form="ip"),
        _doc("СНИЛС или иной документ (уведомление)", form="ip"),
        _doc("Договор аренды либо иной документ на место ведения деятельности", note="если есть место осуществления предпринимательской деятельности", form="ip"),
    ]

    docs += [
        _doc("Налоговая декларация по УСН (отметка налогового органа или подтверждение приёма в электронном виде)", note="за 2 последних года", section="Налогообложение", form="ip", channel="msp", tax=["usn"]),
        _doc("Налоговая декларация по ЕСХН (отметка налогового органа или подтверждение приёма в электронном виде)", note="за 2 последних года", section="Налогообложение", form="ip", channel="msp", tax=["eshn"]),
        _doc("Патент(ы) на право применения патентной системы налогообложения (копия)", note="за прошедший и на текущий год", section="Налогообложение", form="ip", channel="msp", tax=["patent"]),
        _doc("Справка ФНС о состоянии расчётов (доходах) по НПД", section="Налогообложение", form="ip", channel="msp", tax=["npd"]),
        _doc("Справка ФНС о применении АвтоУСН и справка о состоянии расчётов по АвтоУСН (ЭЦП или оригинал)", section="Налогообложение", form="ip", channel="msp", tax=["auto_usn"]),
        _doc("Инструкция по запросу справок в личном кабинете налогоплательщика", section="Налогообложение", form="ip", channel="msp", tax=["auto_usn"]),
        _doc("3-НДФЛ (отметка налогового органа или подтверждение приёма в электронном виде)", note="за 2 последних года", section="Налогообложение", form="ip", channel="msp", tax=["osno"]),
        _doc("Налоговая декларация по УСН (отметка налогового органа или подтверждение приёма в электронном виде)", note="за последний налоговый период", section="Налогообложение", form="ip", channel="office", tax=["usn"]),
        _doc("Налоговая декларация по ЕСХН (отметка налогового органа или подтверждение приёма в электронном виде)", note="за последний налоговый период", section="Налогообложение", form="ip", channel="office", tax=["eshn"]),
        _doc("Патент(ы) на право применения патентной системы налогообложения (копия)", note="за прошедший и на текущий год", section="Налогообложение", form="ip", channel="office", tax=["patent"]),
        _doc("Справка ФНС о состоянии расчётов (доходах) по НПД", section="Налогообложение", form="ip", channel="office", tax=["npd"]),
        _doc("Справка ФНС о применении АвтоУСН и справка о состоянии расчётов по АвтоУСН (ЭЦП или оригинал)", section="Налогообложение", form="ip", channel="office", tax=["auto_usn"]),
        _doc("Инструкция по запросу справок в личном кабинете налогоплательщика", section="Налогообложение", form="ip", channel="office", tax=["auto_usn"]),
        _doc("3-НДФЛ (отметка налогового органа или подтверждение приёма в электронном виде)", note="за последний налоговый период", section="Налогообложение", form="ip", channel="office", tax=["osno"]),
    ]

    docs += [
        _doc("Заявление-анкета на получение микрозайма + приложение (вторая закладка в Excel)", url=URLS["app_ul"], form="ul"),
        _doc("Действующая редакция устава (копия)", form="ul"),
        _doc("Паспорт руководителя организации (все страницы)", form="ul"),
        _doc("Согласие на обработку персональных данных", url=URLS["consent"], form="ul"),
        _doc("Карточка предприятия (реквизиты с подписью и печатью)", form="ul"),
        _doc("Документы, подтверждающие полномочия руководителя (решение об избрании единоличного исполнительного органа)", note="если дата документа после 01.09.2024, требуется нотариальное заверение", form="ul"),
        _doc("Бухгалтерская (финансовая) отчётность: баланс и отчёт о финансовых результатах с отметкой налогового органа", note="за последний отчётный год", form="ul"),
        _doc("Бухгалтерская (финансовая) отчётность за подписью руководителя и печатью организации", note="за последний отчётный период (промежуточная, квартальная)", form="ul"),
        _doc("Выписки по всем расчётным счетам с назначением платежей (Excel)", note="за последние 12 месяцев", form="ul", channel="msp"),
        _doc("Выписки по всем расчётным счетам с назначением платежей (Excel)", note="не менее 6 последних месяцев", form="ul", channel="office"),
        _doc("Отчёт по онлайн-кассе с разбивкой помесячно", note="не менее 6 последних месяцев, если применение онлайн-кассы обязательно", form="ul", channel="msp"),
        _doc("Отчёт по онлайн-кассе (Excel) или копия книги учёта доходов и расходов / хозяйственных операций, если онлайн-кассы нет", note="не менее 6 последних месяцев", form="ul", channel="office"),
        _doc("Книга учёта доходов и расходов и/или хозяйственных операций (Excel)", note="за предыдущий год и на текущий год с 1 января до месяца подачи заявки", form="ul"),
        _doc("Сведения о доходах и расходах", note="за последние 12 месяцев", url=URLS["income_12"], form="ul", channel="msp"),
        _doc("Сведения о доходах и расходах", note="не менее 6 последних месяцев", url=URLS["income_6"], form="ul", channel="office"),
        _doc("Оборотно-сальдовая ведомость общая", note="за предыдущий год", form="ul", channel="msp"),
        _doc("Оборотно-сальдовая ведомость общая", note="за последний отчётный период (промежуточный)", form="ul", channel="msp"),
        _doc("Оборотно-сальдовая ведомость к счетам 01, 02, 58, 60, 62, 66, 67, 76, 91", note="за предыдущий год", form="ul", channel="msp"),
        _doc("Оборотно-сальдовая ведомость к счетам 01, 02, 58, 60, 62, 66, 67, 76, 91", note="за последний отчётный период (промежуточный)", form="ul", channel="msp"),
        _doc("Карточка 51 счёта", note="за последние 12 месяцев", form="ul", channel="msp"),
        _doc("Решение органа управления юридического лица о привлечении заёмных средств (одобрении сделки)", form="ul"),
        _doc("Справка об исполнении обязанности по уплате налогов, сборов, страховых взносов, пеней, штрафов, процентов (ЭЦП или оригинал)", note="при наличии задолженности приложите подтверждающие документы", form="ul"),
        _doc("Справка ФНС о сальдо единого налогового счёта", form="ul"),
        _doc("Справка об отсутствии задолженности перед работниками по заработной плате более 3 месяцев", form="ul"),
        _doc("Лицензия", note="при наличии", form="ul"),
        _doc("Отзывы контрагентов в произвольной письменной форме", note="при наличии", form="ul"),
        _doc("Страница 001 формы «Расчёт страховых взносов»", note="за последний отчётный период", form="ul"),
        _doc("Договор аренды либо иной документ на место ведения деятельности", note="если есть место осуществления предпринимательской деятельности", form="ul"),
    ]

    docs += [
        _doc("Налоговая декларация по УСН (отметка налогового органа или подтверждение приёма в электронном виде)", note="за последний налоговый период", section="Налогообложение", form="ul", tax=["usn"]),
        _doc("Налоговая декларация по ЕСХН (отметка налогового органа или подтверждение приёма в электронном виде)", note="за последний налоговый период", section="Налогообложение", form="ul", tax=["eshn"]),
        _doc("Справка ФНС о применении АвтоУСН и справка о состоянии расчётов по АвтоУСН (ЭЦП или оригинал)", section="Налогообложение", form="ul", tax=["auto_usn"]),
        _doc("Инструкция по запросу справок в личном кабинете налогоплательщика", section="Налогообложение", form="ul", tax=["auto_usn"]),
    ]

    docs += [
        _doc("Технико-экономическое обоснование (бизнес-план)", note="если срок ведения деятельности менее 3 месяцев", url=URLS["teo"], section="Срок деятельности", term="lt3"),
    ]

    docs += [
        _doc("Анкета поручителя / залогодателя — физическое лицо", section="Поручительство супруга", family="spouse_no"),
        _doc("Паспорт супруга (все страницы)", section="Поручительство супруга", family="spouse_no"),
        _doc("Согласие на обработку персональных данных супруга", url=URLS["consent"], section="Поручительство супруга", family="spouse_no"),
        _doc("Справка о доходах физического лица (КНД 1175018) или сведения о доходах / выплатах через Госуслуги", note="не менее 6 последних месяцев", section="Поручительство супруга", family="spouse_no"),
        _doc("Трудовая книжка (копия) или сведения о трудовой деятельности", section="Поручительство супруга", family="spouse_no"),
        _doc("СНИЛС супруга (копия) или иной документ", section="Поручительство супруга", family="spouse_no"),
        _doc("Анкета поручителя / залогодателя — ЮЛ, ИП, глава КФХ", url=URLS["anketa_ul"], section="Поручительство супруга", family="spouse_ip"),
        _doc("Паспорт супруга (все страницы)", section="Поручительство супруга", family="spouse_ip"),
        _doc("Согласие на обработку персональных данных супруга", url=URLS["consent"], section="Поручительство супруга", family="spouse_ip"),
        _doc("Карточка предприятия супруга (реквизиты с подписью и печатью)", section="Поручительство супруга", family="spouse_ip"),
        _doc("Выписки по всем расчётным счетам супруга (Excel)", note="не менее 6 последних месяцев", section="Поручительство супруга", family="spouse_ip"),
        _doc("Отчёт по онлайн-кассе супруга или копия книги учёта доходов и расходов", note="не менее 6 последних месяцев", section="Поручительство супруга", family="spouse_ip"),
        _doc("Сведения о доходах и расходах супруга", note="не менее 6 последних месяцев", section="Поручительство супруга", family="spouse_ip"),
        _doc("СНИЛС супруга (копия) или иной документ", section="Поручительство супруга", family="spouse_ip"),
        _doc("Налоговая декларация супруга по УСН", note="за последний налоговый период", section="Поручительство супруга", family="spouse_ip", spouse_tax=["usn"]),
        _doc("Налоговая декларация супруга по ЕСХН", note="за последний налоговый период", section="Поручительство супруга", family="spouse_ip", spouse_tax=["eshn"]),
        _doc("Патент(ы) супруга на патентную систему налогообложения (копия)", note="за прошедший и на текущий год", section="Поручительство супруга", family="spouse_ip", spouse_tax=["patent"]),
        _doc("Справка ФНС о состоянии расчётов (доходах) супруга по НПД", section="Поручительство супруга", family="spouse_ip", spouse_tax=["npd"]),
        _doc("Справки ФНС супруга по АвтоУСН", section="Поручительство супруга", family="spouse_ip", spouse_tax=["auto_usn"]),
        _doc("3-НДФЛ супруга", note="за последний налоговый период", section="Поручительство супруга", family="spouse_ip", spouse_tax=["osno"]),
    ]

    docs += [
        _doc("Копия кредитного договора", section="Рефинансирование", refinance="yes"),
        _doc("Справка банка: текущий остаток задолженности по кредиту, процентам, штрафам, пеням; число и длительность просрочек", section="Рефинансирование", refinance="yes"),
        _doc("Документы, подтверждающие целевое использование кредита на предпринимательскую деятельность", section="Рефинансирование", refinance="yes"),
    ]

    docs += [
        _doc("Отчёт об оценке недвижимого имущества", note="дата оценки не старше 12 месяцев; не нужен, если объект уже в залоге Фонда и имеющемуся отчёту не более 3 лет", section="Обеспечение", collateral=["realty"]),
        _doc("Кадастровый или технический паспорт", note="при наличии", section="Обеспечение", collateral=["realty"]),
        _doc("Свидетельство о регистрации ТС", section="Обеспечение", collateral=["vehicle"]),
        _doc("Паспорт транспортного средства (ПТС) или выписка из электронного ПТС (копия)", section="Обеспечение", channel="msp", collateral=["vehicle"]),
        _doc("Договор купли-продажи / лизинга", section="Обеспечение", channel="msp", collateral=["vehicle"]),
    ]

    docs += [
        _doc("Выписка или сведения из ЕГРН (не позднее 30 дней, ЭЦП или оригинал)", section="Залогодатель", owner="borrower"),
        _doc("Нотариально удостоверенное согласие супруга собственника на залог", note="можно представить после решения Фонда, но не позднее обращения в Росреестр", section="Залогодатель", form="ip", owner="borrower"),
        _doc("Анкета поручителя / залогодателя — физическое лицо", url=URLS["anketa_fl"], section="Залогодатель", owner="citizen"),
        _doc("Паспорт залогодателя (все страницы)", section="Залогодатель", owner="citizen"),
        _doc("Согласие на обработку персональных данных залогодателя", url=URLS["consent"], section="Залогодатель", owner="citizen"),
        _doc("СНИЛС залогодателя (копия) или иной документ", section="Залогодатель", owner="citizen"),
        _doc("Выписка или сведения из ЕГРН (не позднее 30 дней, ЭЦП или оригинал)", section="Залогодатель", owner="citizen"),
        _doc("Нотариально удостоверенное согласие супруга собственника на залог", note="можно представить после решения Фонда, но не позднее обращения в Росреестр", section="Залогодатель", owner="citizen"),
        _doc("Анкета поручителя / залогодателя — ЮЛ, ИП, глава КФХ", url=URLS["anketa_ul"], section="Залогодатель", owner="legal"),
        _doc("Действующая редакция устава залогодателя (копия)", section="Залогодатель", owner="legal"),
        _doc("Паспорт руководителя залогодателя (все страницы)", section="Залогодатель", owner="legal"),
        _doc("Согласие на обработку персональных данных", url=URLS["consent"], section="Залогодатель", owner="legal"),
        _doc("Карточка предприятия залогодателя", section="Залогодатель", owner="legal"),
        _doc("Документы, подтверждающие полномочия руководителя залогодателя", note="если дата документа после 01.09.2024, требуется нотариальное заверение", section="Залогодатель", owner="legal"),
        _doc("Решение органа управления о предоставлении обеспечения (одобрении сделки) перед Фондом", section="Залогодатель", owner="legal"),
    ]
    return docs


DOCUMENTS = _catalog()
SECTION_ORDER = [
    "Заёмщик",
    "Налогообложение",
    "Срок деятельности",
    "Поручительство супруга",
    "Рефинансирование",
    "Обеспечение",
    "Залогодатель",
]


def _matches(when: dict, answers: dict) -> bool:
    for key, expected in when.items():
        value = answers.get(key)
        if isinstance(expected, list):
            selected = value if isinstance(value, list) else ([value] if value else [])
            if not any(item in selected for item in expected):
                return False
        elif value != expected:
            return False
    return True


def start() -> dict:
    return next_step({})


def answer(answers: dict, question_id: str, value) -> dict:
    next_answers = dict(answers or {})
    next_answers[question_id] = value
    return next_step(next_answers)


def rewind(answers: dict, question_id: str) -> dict:
    step = next_step(answers or {})
    keep = set()
    for item in step["history"]:
        if item["id"] == question_id:
            break
        keep.add(item["id"])
    filtered = {key: val for key, val in (answers or {}).items() if key in keep}
    return next_step(filtered)


def build_package(answers: dict) -> dict:
    groups: dict[str, list] = {name: [] for name in SECTION_ORDER}
    seen: set[tuple] = set()
    for item in DOCUMENTS:
        if not _matches(item["when"], answers):
            continue
        key = (item["section"], item["title"], item["note"], item["url"])
        if key in seen:
            continue
        seen.add(key)
        groups[item["section"]].append(
            {"title": item["title"], "note": item["note"], "url": item["url"]}
        )

    channel = answers.get("channel")
    return {
        "count": sum(len(items) for items in groups.values()),
        "notice": PACKAGE_NOTICE,
        "channel": channel,
        "channel_url": URLS.get(channel, ""),
        "groups": [
            {"title": name, "items": items}
            for name, items in groups.items()
            if items
        ],
    }
