<?php
require $_SERVER["DOCUMENT_ROOT"] . "/bitrix/header.php";
$APPLICATION->SetTitle("Подбор документов");
$APPLICATION->SetPageProperty("description", "Подбор пакета документов для заявки на микрозайм");
?>

<h1>Подбор документов</h1>
<p>Ответьте на вопросы — система соберёт перечень документов для заявки на микрозайм.</p>

<?php include $_SERVER["DOCUMENT_ROOT"] . "/local/docs-picker/include.php"; ?>

<?php require $_SERVER["DOCUMENT_ROOT"] . "/bitrix/footer.php"; ?>
