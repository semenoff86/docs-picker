<?php
/**
 * HTTP-точка входа для 1С-Битрикс.
 * Скопируйте вместе с DocsPickerService.php и scheme.json, например в /local/docs-picker/.
 *
 * POST JSON:
 *   { "action": "start" }
 *   { "action": "next", "answers": { ... } }
 *   { "action": "answer", "answers": { ... }, "question_id": "amount", "value": "lt1m" }
 *   { "action": "rewind", "answers": { ... }, "question_id": "form" }
 */

header("Content-Type: application/json; charset=utf-8");
header("X-Content-Type-Options: nosniff");

if (isset($_SERVER["DOCUMENT_ROOT"])) {
    $prolog = $_SERVER["DOCUMENT_ROOT"] . "/bitrix/modules/main/include/prolog_before.php";
    if (is_file($prolog)) {
        define("NO_KEEP_STATISTIC", true);
        define("NOT_CHECK_PERMISSIONS", true);
        require $prolog;
    }
}

require_once __DIR__ . "/DocsPickerService.php";

$schemePath = is_file(__DIR__ . "/scheme.json")
    ? __DIR__ . "/scheme.json"
    : dirname(__DIR__) . "/scheme.json";

try {
    $picker = DocsPickerService::fromFile($schemePath);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(array("error" => $e->getMessage()), JSON_UNESCAPED_UNICODE);
    return;
}

$raw = file_get_contents("php://input");
$input = json_decode($raw, true);
if (!is_array($input)) {
    $input = $_POST;
}
if (!is_array($input)) {
    $input = array();
}

$action = isset($input["action"]) ? $input["action"] : "next";
$answers = isset($input["answers"]) && is_array($input["answers"]) ? $input["answers"] : array();
$questionId = isset($input["question_id"]) ? $input["question_id"] : "";

try {
    if ($action === "start") {
        $result = $picker->start();
    } elseif ($action === "rewind") {
        $result = $picker->rewind($answers, $questionId);
    } elseif ($action === "answer") {
        $value = array_key_exists("value", $input) ? $input["value"] : null;
        $result = $picker->answer($answers, $questionId, $value);
    } else {
        $result = $picker->nextStep($answers);
    }
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode(array("error" => $e->getMessage()), JSON_UNESCAPED_UNICODE);
    return;
}

echo json_encode($result, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
