# Как вызывать сервис

Вся логика в `wizard.py`. HTTP-обёртка — `app.py`. Состояние диалога — словарь `answers`, его хранит вызывающий код.

## Python

```python
from wizard import start, answer, rewind, next_step

step = start()
step = answer(step["answers"], step["question"]["id"], "lt1m")
step = rewind(step["answers"], "amount")
step = next_step({"amount": "lt1m", "channel": "office"})
```

Пока опрос не закончен: `done` = false и объект `question`.
Когда все ответы есть: `done` = true и объект `package` со списком документов.

Для `multi` значение — список id, например `["usn", "osno"]`. Пустой список на шаге обеспечения означает «залога нет».

## HTTP

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

- `GET /` — первый вопрос
- `POST /step` — `{"answers": {...}}`
- `POST /answer` — `{"answers": {...}, "question_id": "amount", "value": "lt1m"}`
- `POST /rewind` — `{"answers": {...}, "question_id": "form"}`

## Ответ с вопросом

```json
{
  "done": false,
  "step": 1,
  "total": 9,
  "error": null,
  "answers": {},
  "history": [],
  "question": {
    "id": "amount",
    "title": "Сумма займа",
    "type": "single",
    "hint": "...",
    "options": [{ "id": "lt1m", "label": "до 1 000 000" }],
    "links": []
  }
}
```

`type`: `single` — строка, `multi` — массив id.

## Ответ со списком документов

```json
{
  "done": true,
  "question": null,
  "package": {
    "count": 12,
    "notice": "Данный перечень является базовым. Фонд может запросить дополнительные документы.",
    "channel": "office",
    "channel_url": "https://fundmicro86.ru/clients/sposobi.php",
    "groups": [
      {
        "title": "Заёмщик",
        "items": [{ "title": "...", "note": "", "url": "https://..." }]
      }
    ]
  }
}
```

## Ветвление

- `family` и `spouse_tax` только для ИП / главы КФХ
- `spouse_tax` только если супруг(а) тоже ИП
- `owner` только если выбран хотя бы один вид залога
- сумма от 1 млн и пустой залог: снова вопрос `collateral` и текст в `error`
- для ЮЛ вопросы про семью не задаются
