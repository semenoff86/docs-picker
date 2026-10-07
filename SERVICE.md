# Контракт сервиса

Сервис не рисует страницу. Он принимает набор ответов и возвращает либо следующий вопрос, либо готовый список документов.

Состояние диалога — JSON-объект `answers`. Его хранит страница (сессия, скрытое поле, JS). Сервис его не сохраняет.

## Файлы

| Файл | Назначение |
| --- | --- |
| `scheme.json` | Справочники, порядок вопросов, правила документов |
| `src/DocsPickerService.php` | Логика на PHP для 1С-Битрикс |
| `src/ajax.php` | HTTP API: POST JSON |
| `src/engine.js` | Та же логика в браузере, если страницу делают на JS |

## PHP

```php
require $_SERVER["DOCUMENT_ROOT"] . "/local/docs-picker/DocsPickerService.php";

$picker = DocsPickerService::fromFile($_SERVER["DOCUMENT_ROOT"] . "/local/docs-picker/scheme.json");

$step = $picker->start();
$step = $picker->answer($step["answers"], $step["question"]["id"], "lt1m");
$step = $picker->rewind($step["answers"], "channel");
$step = $picker->nextStep($answers);
```

## HTTP

Скопируйте `scheme.json`, `DocsPickerService.php` и `ajax.php` в `/local/docs-picker/`.

```
POST /local/docs-picker/ajax.php
Content-Type: application/json
```

```json
{ "action": "start" }
```

```json
{ "action": "answer", "answers": {}, "question_id": "amount", "value": "lt1m" }
```

Для `multi` в `value` передайте массив id, например `["usn","osno"]`. Пустой массив на шаге обеспечения означает «залога нет».

```json
{ "action": "rewind", "answers": { "...": "..." }, "question_id": "form" }
```

```json
{ "action": "next", "answers": { "amount": "lt1m", "channel": "office" } }
```

## Ответ, пока опрос не закончен

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
  },
  "package": null
}
```

`type`: `single` — одно значение-строка, `multi` — массив id.

## Ответ, когда список готов

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

## Правила ветвления

- `family` и `spouse_tax` только для ИП / главы КФХ.
- `spouse_tax` только если супруг(а) тоже ИП.
- `owner` только если выбран хотя бы один вид залога.
- Если сумма «от 1 000 000» и обеспечение пустое, сервис возвращает текущий вопрос `collateral` и текст ошибки в `error`.
- Для ЮЛ вопросы про семью не задаются.

Тексты вопросов живут в PHP/JS. Менять перечень документов и налоговые режимы — в `scheme.json`.

## JS (если страница без PHP)

```javascript
fetch("/local/docs-picker/scheme.json")
  .then(function (r) { return r.json(); })
  .then(function (scheme) {
    var picker = DocsPicker.create(scheme);
    var step = picker.start();
  });
```
