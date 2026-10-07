<?php
if (!defined("B_PROLOG_INCLUDED") || B_PROLOG_INCLUDED !== true) {
    die();
}

$base = htmlspecialcharsbx($arResult["ASSETS_BASE"]);
?>
<link rel="stylesheet" href="<?= $base ?>assets/css/picker.css">
<div class="docs-picker" id="docs-picker"></div>
<script src="<?= $base ?>assets/js/scheme.js"></script>
<script src="<?= $base ?>assets/js/engine.js"></script>
<script src="<?= $base ?>assets/js/app.js"></script>
