<?php

/**
 * Сервис подбора документов для микрозайма.
 *
 * Состояние — только массив ответов. Страницу и хранение делает вызывающий код.
 *
 *   $picker = DocsPickerService::fromFile(__DIR__ . '/../scheme.json');
 *   $step = $picker->start();
 *   $step = $picker->answer($step['answers'], $step['question']['id'], 'lt1m');
 */
class DocsPickerService
{
    /** @var array */
    private $scheme;

    public static function fromFile($path)
    {
        $json = file_get_contents($path);
        if ($json === false) {
            throw new RuntimeException('Cannot read scheme: ' . $path);
        }
        $scheme = json_decode($json, true);
        if (!is_array($scheme)) {
            throw new RuntimeException('Invalid scheme JSON: ' . $path);
        }
        return new self($scheme);
    }

    public function __construct(array $scheme)
    {
        $this->scheme = $scheme;
    }

    public function start()
    {
        return $this->nextStep(array());
    }

    /**
     * @param array $answers текущие ответы
     * @param string $questionId id вопроса, к которому нужно вернуться (он будет задан заново)
     */
    public function rewind(array $answers, $questionId)
    {
        $step = $this->nextStep($answers);
        $keep = array();
        foreach ($step['history'] as $item) {
            if ($item['id'] === $questionId) {
                break;
            }
            $keep[$item['id']] = true;
        }
        $filtered = array();
        foreach ($answers as $key => $value) {
            if (isset($keep[$key])) {
                $filtered[$key] = $value;
            }
        }
        return $this->nextStep($filtered);
    }

    /**
     * @param mixed $value строка для single, массив id для multi
     */
    public function answer(array $answers, $questionId, $value)
    {
        $answers[$questionId] = $value;
        return $this->nextStep($answers);
    }

    /**
     * Главный метод: по ответам вернуть текущий вопрос или итоговый пакет.
     *
     * @param array $rawAnswers
     * @return array
     */
    public function nextStep(array $rawAnswers)
    {
        $answers = $this->sanitizeAnswers($rawAnswers);
        $error = null;
        if (isset($answers['amount']) && $answers['amount'] === 'gt1m' && array_key_exists('collateral', $rawAnswers)) {
            if (empty($answers['collateral'])) {
                $error = $this->scheme['collateralRequired'];
                unset($answers['collateral']);
            }
        }

        $history = array();
        $current = null;
        foreach ($this->scheme['questionOrder'] as $qid) {
            if (!$this->questionVisible($qid, $answers)) {
                continue;
            }
            if (!array_key_exists($qid, $answers) || ($error && $qid === 'collateral')) {
                $current = $qid;
                break;
            }
            $value = $answers[$qid];
            $labels = is_array($value)
                ? array_map(function ($item) use ($qid, $answers) {
                    return $this->optionLabel($qid, $item, $answers);
                }, $value)
                : array($this->optionLabel($qid, $value, $answers));
            $question = $this->buildQuestion($qid, $answers);
            $history[] = array(
                'id' => $qid,
                'title' => $question['title'],
                'labels' => array_values($labels),
            );
        }

        if ($current) {
            return array(
                'done' => false,
                'question' => $this->buildQuestion($current, $answers),
                'error' => $error,
                'answers' => $answers,
                'history' => $history,
                'step' => count($history) + 1,
                'total' => count($history) + 1 + $this->remainingAfter($current, $answers),
                'package' => null,
            );
        }

        return array(
            'done' => true,
            'question' => null,
            'error' => null,
            'answers' => $answers,
            'history' => $history,
            'step' => count($history),
            'total' => count($history),
            'package' => $this->buildPackage($answers),
        );
    }

    private function questionVisible($qid, array $answers)
    {
        if ($qid === 'family') {
            return isset($answers['form']) && $answers['form'] === 'ip';
        }
        if ($qid === 'spouse_tax') {
            return isset($answers['form'], $answers['family'])
                && $answers['form'] === 'ip'
                && $answers['family'] === 'spouse_ip';
        }
        if ($qid === 'owner') {
            return !empty($answers['collateral']);
        }
        return true;
    }

    private function buildQuestion($qid, array $answers)
    {
        $base = array(
            'id' => $qid,
            'title' => '',
            'type' => 'single',
            'hint' => '',
            'options' => array(),
            'links' => array(),
        );

        switch ($qid) {
            case 'amount':
                return array_merge($base, array(
                    'title' => 'Сумма займа',
                    'hint' => $this->scheme['collateralRequired'],
                    'options' => array(
                        array('id' => 'lt1m', 'label' => 'до 1 000 000'),
                        array('id' => 'gt1m', 'label' => 'от 1 000 000 до 5 000 000'),
                    ),
                ));
            case 'channel':
                return array_merge($base, array(
                    'title' => 'Способ подачи документов',
                    'hint' => 'Ссылку можно открыть в новой вкладке. После подачи вернитесь сюда и продолжите подбор пакета.',
                    'options' => array(
                        array('id' => 'msp', 'label' => 'Цифровая платформа МСП'),
                        array('id' => 'office', 'label' => 'Офис Фонда'),
                    ),
                    'links' => array(
                        array('label' => 'Платформа МСП', 'url' => $this->scheme['urls']['msp']),
                        array('label' => 'Способы подачи в Фонд', 'url' => $this->scheme['urls']['office']),
                    ),
                ));
            case 'form':
                return array_merge($base, array(
                    'title' => 'Организационно-правовая форма',
                    'options' => array(
                        array('id' => 'ip', 'label' => 'Индивидуальный предприниматель или Глава КФХ'),
                        array('id' => 'ul', 'label' => 'Юридическое лицо'),
                    ),
                ));
            case 'tax':
                $mspIp = (isset($answers['channel'], $answers['form'])
                    && $answers['channel'] === 'msp'
                    && $answers['form'] === 'ip');
                $options = isset($answers['form']) && $answers['form'] === 'ip'
                    ? $this->scheme['taxIp']
                    : $this->scheme['taxUl'];
                return array_merge($base, array(
                    'title' => $mspIp
                        ? 'Система налогообложения (за последние два года)'
                        : 'Система налогообложения',
                    'type' => 'multi',
                    'hint' => 'Можно выбрать несколько вариантов, если режимы применялись в разные периоды.',
                    'options' => $this->cloneArray($options),
                ));
            case 'term':
                return array_merge($base, array(
                    'title' => 'Срок ведения деятельности',
                    'options' => array(
                        array('id' => 'lt3', 'label' => 'Менее 3 месяцев'),
                        array('id' => 'ge3', 'label' => '3 месяца и более'),
                    ),
                ));
            case 'family':
                return array_merge($base, array(
                    'title' => 'Семейное положение',
                    'hint' => 'От этого зависит пакет поручительства супруга.',
                    'options' => array(
                        array('id' => 'spouse_ip', 'label' => 'Супруг(а) является ИП'),
                        array('id' => 'spouse_no', 'label' => 'Супруг(а) не являются ИП'),
                        array('id' => 'single', 'label' => 'Не состою в браке'),
                    ),
                ));
            case 'spouse_tax':
                return array_merge($base, array(
                    'title' => 'Система налогообложения супруга(-ги)',
                    'type' => 'multi',
                    'hint' => 'Можно выбрать несколько вариантов.',
                    'options' => $this->cloneArray($this->scheme['taxIp']),
                ));
            case 'refinance':
                return array_merge($base, array(
                    'title' => 'Цель использования займа: рефинансирование кредита на осуществление предпринимательской деятельности',
                    'hint' => 'Если да, в пакет войдут кредитный договор, банковская справка и документы о целевом использовании.',
                    'options' => array(
                        array('id' => 'yes', 'label' => 'Да'),
                        array('id' => 'no', 'label' => 'Нет'),
                    ),
                ));
            case 'collateral':
                $required = isset($answers['amount']) && $answers['amount'] === 'gt1m';
                return array_merge($base, array(
                    'title' => 'Предлагаемое обеспечение',
                    'type' => 'multi',
                    'hint' => $required
                        ? $this->scheme['collateralRequired']
                        : 'Можно выбрать несколько видов обеспечения или пропустить, если залога нет.',
                    'options' => array(
                        array('id' => 'realty', 'label' => 'Нежилое недвижимое имущество, находящееся на территории ХМАО-Югры'),
                        array('id' => 'vehicle', 'label' => 'Транспортное средство, спецтехника, находящееся на территории ХМАО-Югры'),
                    ),
                ));
            case 'owner':
                return array_merge($base, array(
                    'title' => 'Залог принадлежит',
                    'options' => array(
                        array('id' => 'borrower', 'label' => 'Заемщику'),
                        array('id' => 'citizen', 'label' => 'Третьему лицу – гражданину'),
                        array('id' => 'legal', 'label' => 'Третьему лицу – юридическому лицу'),
                    ),
                ));
            default:
                throw new InvalidArgumentException('Unknown question: ' . $qid);
        }
    }

    private function optionLabel($qid, $value, array $answers)
    {
        foreach ($this->buildQuestion($qid, $answers)['options'] as $opt) {
            if ($opt['id'] === $value) {
                return $opt['label'];
            }
        }
        return (string) $value;
    }

    private function sanitizeAnswers(array $raw)
    {
        $answers = $raw;
        if (!isset($answers['form']) || $answers['form'] !== 'ip') {
            unset($answers['family'], $answers['spouse_tax']);
        }
        if (!isset($answers['family']) || $answers['family'] !== 'spouse_ip') {
            unset($answers['spouse_tax']);
        }
        if (empty($answers['collateral'])) {
            unset($answers['owner']);
        }
        return $answers;
    }

    private function remainingAfter($current, array $answers)
    {
        $started = false;
        $count = 0;
        foreach ($this->scheme['questionOrder'] as $qid) {
            if ($qid === $current) {
                $started = true;
                continue;
            }
            if (!$started) {
                continue;
            }
            if ($this->questionVisible($qid, $answers)) {
                $count += 1;
            }
        }
        return $count;
    }

    private function matches(array $when, array $answers)
    {
        foreach ($when as $key => $expected) {
            $value = isset($answers[$key]) ? $answers[$key] : null;
            if (is_array($expected)) {
                $selected = is_array($value) ? $value : ($value ? array($value) : array());
                $hit = false;
                foreach ($expected as $item) {
                    if (in_array($item, $selected, true)) {
                        $hit = true;
                        break;
                    }
                }
                if (!$hit) {
                    return false;
                }
            } elseif ($value !== $expected) {
                return false;
            }
        }
        return true;
    }

    private function buildPackage(array $answers)
    {
        $groups = array();
        foreach ($this->scheme['sectionOrder'] as $name) {
            $groups[$name] = array();
        }
        $seen = array();
        foreach ($this->scheme['documents'] as $item) {
            if (!$this->matches($item['when'], $answers)) {
                continue;
            }
            $note = isset($item['note']) ? $item['note'] : '';
            $url = isset($item['url']) ? $item['url'] : '';
            $key = $item['section'] . "\t" . $item['title'] . "\t" . $note . "\t" . $url;
            if (isset($seen[$key])) {
                continue;
            }
            $seen[$key] = true;
            $groups[$item['section']][] = array(
                'title' => $item['title'],
                'note' => $note,
                'url' => $url,
            );
        }

        $count = 0;
        $outGroups = array();
        foreach ($this->scheme['sectionOrder'] as $name) {
            $count += count($groups[$name]);
            if ($groups[$name]) {
                $outGroups[] = array(
                    'title' => $name,
                    'items' => $groups[$name],
                );
            }
        }

        $channel = isset($answers['channel']) ? $answers['channel'] : '';
        $urls = $this->scheme['urls'];
        return array(
            'count' => $count,
            'notice' => $this->scheme['packageNotice'],
            'channel' => $channel,
            'channel_url' => ($channel && isset($urls[$channel])) ? $urls[$channel] : '',
            'groups' => $outGroups,
        );
    }

    private function cloneArray(array $value)
    {
        return json_decode(json_encode($value), true);
    }
}
