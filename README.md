# Подбор документов для микрозайма

Отдельный модуль без парсера истории браузера. Вся логика опроса и сборки пакета документов работает в браузере: HTML, CSS и JavaScript. Сервер Python не нужен, поэтому модуль можно вставить в сайт на 1С-Битрикс как обычную страницу.

## Состав

- `public/` — готовая страница для проверки в браузере
- `public/assets/` — стили и скрипты, которые копируются на сайт
- `bitrix/page.php` — пример страницы Битрикс
- `bitrix/include.php` — вставка виджета в любую страницу
- `bitrix/local/components/fundmicro/document.picker/` — компонент для визуального редактора

## Как проверить локально

Откройте `public/index.html` в браузере. Можно просто двойным щелчком, сервер не обязателен.

## Как вставить в 1С-Битрикс

1. Скопируйте папку `public/assets` в  
   `/local/docs-picker/assets/`
2. Скопируйте `bitrix/include.php` в  
   `/local/docs-picker/include.php`
3. Создайте раздел, например `/podbor-dokumentov/`, и положите туда `bitrix/page.php` как `index.php`.

Либо вставьте виджет в существующую страницу:

```php
<?php include $_SERVER["DOCUMENT_ROOT"] . "/local/docs-picker/include.php"; ?>
```

### Вариант через компонент

1. Скопируйте  
   `bitrix/local/components/fundmicro/document.picker/`  
   в  
   `/local/components/fundmicro/document.picker/`
2. На странице добавьте:

```php
<?$APPLICATION->IncludeComponent("fundmicro:document.picker", ".default", []);?>
```

Компонент тоже читает файлы из `/local/docs-picker/assets/`, поэтому шаг с копированием `assets` обязателен.

## Что умеет

- пошаговые вопросы с ветвлением
- возврат к предыдущему ответу
- итоговый список документов со ссылками на бланки
- печать / сохранение в PDF через диалог печати браузера

Логика подбора совпадает с текущей схемой. Менять вопросы и перечень документов нужно в `public/assets/js/scheme.js`.
