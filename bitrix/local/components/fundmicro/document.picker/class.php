<?php
if (!defined("B_PROLOG_INCLUDED") || B_PROLOG_INCLUDED !== true) {
    die();
}

class FundmicroDocumentPicker extends CBitrixComponent
{
    public function executeComponent()
    {
        $this->arResult["ASSETS_BASE"] = "/local/docs-picker/";
        $this->includeComponentTemplate();
    }
}
