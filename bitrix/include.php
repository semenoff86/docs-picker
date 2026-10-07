<?php
if (!function_exists("htmlspecialcharsbx")) {
    function htmlspecialcharsbx($value)
    {
        return htmlspecialchars((string) $value, ENT_QUOTES, "UTF-8");
    }
}

$docsPickerBase = "/local/docs-picker/";
?>
<link rel="stylesheet" href="<?= htmlspecialcharsbx($docsPickerBase) ?>assets/css/picker.css">
<div class="docs-picker" id="docs-picker"></div>
<script src="<?= htmlspecialcharsbx($docsPickerBase) ?>assets/js/scheme.js"></script>
<script src="<?= htmlspecialcharsbx($docsPickerBase) ?>assets/js/engine.js"></script>
<script src="<?= htmlspecialcharsbx($docsPickerBase) ?>assets/js/app.js"></script>
