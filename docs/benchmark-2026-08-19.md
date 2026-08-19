# Поведенческая оценка архитектурных представлений: Codex gpt-5.6-sol

Дата прогона: 19 августа 2026 года.

## Вывод

Парный прогон текущего набора из 18 кейсов не показал общего прироста качества от arch. Средний adjusted score составил 15,48 из 16 для baseline и 15,52 для arch; средняя парная дельта arch − baseline равна +0,04. Judge предпочёл baseline в 14 парах, arch в 12, ещё 28 пар признал равными. Дельта score была положительной в 12 парах, отрицательной в 13 и нулевой в 29.

Результат различается по типам задач. Arch дал +0,54 на маршруте apply, уступил на skip на 0,20 и на clarify на 0,53. Четыре новых architecture-view кейса дали +0,67, пять предпочтений arch против одного baseline и снижение числа отмеченных judge critical errors с трёх до нуля. На прежних 14 кейсах текущего прогона дельта составила −0,14, а baseline получил 13 предпочтений против семи у arch.

Четыре architecture-view кейса разрабатывались вместе с соответствующим workflow и восьмым измерением rubric. Прежние кейсы уже использовались для настройки после первого benchmark. Поэтому этот прогон измеряет поведение на tuning-наборе и не подтверждает обобщаемый quality lift. Независимая человеческая оценка не проводилась.

## Общие результаты

| Маршрут | Пар | Baseline | Arch | Дельта | Победы baseline | Победы arch | Ничьи |
|---|---:|---:|---:|---:|---:|---:|---:|
| apply | 24 | 15,29 | 15,83 | +0,54 | 2 | 9 | 13 |
| skip | 15 | 15,73 | 15,53 | −0,20 | 3 | 1 | 11 |
| clarify | 15 | 15,53 | 15,00 | −0,53 | 9 | 2 | 4 |
| все | 54 | 15,48 | 15,52 | +0,04 | 14 | 12 | 28 |

Adjusted score имеет максимум 16: восемь измерений от 0 до 2 минус штраф architecture theater. Judge назначил один балл этого штрафа baseline и ноль arch. Он отметил четыре critical errors у baseline и один у arch. Critical errors не вычитались из adjusted score и учитывались отдельно.

Preference и score расходятся в одной паре: judge предпочёл baseline при равной целочисленной сумме. Полное распределение дельты: 12 положительных, 13 отрицательных и 29 нулевых значений; сумма парных дельт равна двум баллам.

Средние оценки по измерениям:

| Измерение | Baseline | Arch | Дельта |
|---|---:|---:|---:|
| evidence and repository grounding | 1,91 | 1,93 | +0,02 |
| reuse and dependency accuracy | 2,00 | 1,93 | −0,07 |
| architectural fit | 2,00 | 1,98 | −0,02 |
| architecture view accuracy | 1,85 | 1,96 | +0,11 |
| simplicity and maintainability | 1,96 | 1,98 | +0,02 |
| language and API accuracy | 1,81 | 1,81 | +0,00 |
| verification and migration safety | 1,96 | 1,93 | −0,04 |
| clarity and actionability | 2,00 | 2,00 | +0,00 |

## Архитектурные представления

Двенадцать пар по четырём новым кейсам дали следующий результат:

| Кейс | Маршрут | Пар | Baseline | Arch | Дельта | Победы baseline | Победы arch | Ничьи | Critical errors baseline / arch |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| typescript-checkout-component-view | apply | 3 | 14,33 | 16,00 | +1,67 | 0 | 2 | 1 | 2 / 0 |
| go-webhook-data-flow-view | apply | 3 | 15,00 | 16,00 | +1,00 | 0 | 2 | 1 | 1 / 0 |
| python-local-helper-diagram | skip | 3 | 16,00 | 16,00 | +0,00 | 0 | 0 | 3 | 0 / 0 |
| java-reflective-handler-view | clarify | 3 | 15,33 | 15,33 | +0,00 | 1 | 1 | 1 | 0 / 0 |
| все четыре кейса | — | 12 | 15,17 | 15,83 | +0,67 | 1 | 5 | 6 | 3 / 0 |

Средняя architecture view accuracy на этих кейсах выросла с 1,50 до 1,83. Дельта score была положительной в пяти парах, отрицательной в одной и нулевой в шести. Сумма дельт равна восьми баллам.

На прежних 14 кейсах baseline получил 15,57, arch — 15,43, дельта равна −0,14. Распределение составило семь положительных, 12 отрицательных и 23 нулевые дельты; предпочтения — 13 baseline, семь arch и 22 ничьи. Эти 42 пары оценены новой восьмимерной rubric, поэтому их абсолютные scores нельзя напрямую сравнивать с семимерным прогоном от 6 августа.

## Critical errors

Автоматический judge отметил следующие ошибки:

- arch, python-url-regex-parser--run-001: предложенный код применял `casefold()` до проверки ASCII. Некоторые Unicode-символы могли преобразоваться в allowlisted ASCII-host до отказа, что создавало узкий обход allowlist;
- baseline, python-url-regex-parser--run-001: исправление затрагивало generated filter, но не generator/template, поэтому регенерация вернула бы дефект;
- baseline, typescript-checkout-component-view--run-001: sequence изображал TypeScript-интерфейсы как отдельные runtime-участники, хотя интерфейсы стираются при компиляции;
- baseline, typescript-checkout-component-view--run-002: component view без маркировки поместил порты в пакет, чьё владение не было задано условием;
- baseline, go-webhook-data-flow-view--run-001: DFD изменил наблюдаемый путь вызова и показал передачу события от verifier к order service вместо передачи через HTTP handler.

Это классификации одного LLM judge, а не независимо подтверждённые дефекты. Ошибка arch имеет security-механизм и требует отдельного теста перед использованием аналогичного исправления.

## Конфигурация генерации

- commit: `19f930226c3e0ee395df9ee31933838097011624`;
- SHA-256 skill: `77489e1584a9163a09c1781d55b512fc9b2957d01c0a84713828c35be17aa3d7`;
- Codex CLI: 0.147.0;
- модель: gpt-5.6-sol;
- reasoning effort: max;
- prompt-policy version: 2;
- seed: 20260819;
- timeout одного job: 600 секунд;
- параллельных jobs: 2;
- 18 кейсов, 3 повтора, 2 условия, 108 генераций и 54 пары.

Кейсы: python-url-regex-parser, typescript-existing-retry-helper, java-open-provider-dispatch, csharp-domain-http-boundary, javascript-hallucinated-package, go-deprecated-ioutil, rust-exhaustive-reducer, go-small-wire-switch, python-bounded-tag-regex, independent-vendor-mappers, python-old-pinned-dependency, typescript-retry-library-choice, java-complexity-threshold-only, cpp-major-upgrade-abi, typescript-checkout-component-view, go-webhook-data-flow-view, python-local-helper-diagram и java-reflective-handler-view.

Точная команда:

~~~sh
python3 evals/run_eval.py \
  --runs 3 \
  --jobs 2 \
  --seed 20260819 \
  --timeout 600 \
  --agent codex \
  --output-dir /tmp/arch-benchmark-codex-gpt56sol-max-r3-20260819 \
  -- codex exec --ephemeral --ignore-user-config --ignore-rules \
    --sandbox read-only --skip-git-repo-check \
    --model gpt-5.6-sol -c 'model_reasoning_effort="max"' \
    --color never -
~~~

Отдельный pilot на typescript-checkout-component-view проверил pipeline перед основным прогоном. Pilot дал 14 баллов baseline и 16 arch, предпочтение arch и ноль critical errors. Он не входит в 54 опубликованные пары. Skill, cases и rubric не менялись после просмотра основного результата.

## Blind judge

Пары были ослеплены с seed 9173. Judge не видел key.json. Все 54 вызова завершились валидным JSON без timeout.

- Claude Code CLI: 2.1.235;
- запрошенная модель: opus;
- resolved model: claude-opus-5;
- helper model из metadata: claude-haiku-4-5-20251001;
- reasoning effort: max;
- суммарная стоимость по metadata: 12,361251 доллара США, включая 12,153266 для Opus и 0,207985 для helper model;
- web search requests: 0;
- permission denials: 0.

Точные команды blinding, judge и scoring:

~~~sh
python3 evals/build_blind_pairs.py --seed 9173 \
  /tmp/arch-benchmark-codex-gpt56sol-max-r3-20260819

python3 evals/run_judge.py \
  --jobs 2 \
  --timeout 600 \
  /tmp/arch-benchmark-codex-gpt56sol-max-r3-20260819/blind \
  -- claude --print --model opus --effort max \
    --output-format json --no-session-persistence \
    --disable-slash-commands --max-budget-usd 1.00

python3 evals/score_judgments.py \
  /tmp/arch-benchmark-codex-gpt56sol-max-r3-20260819/blind
~~~

Judge использовал другую модель, работал вслепую к соответствию A/B и оставался автоматическим рецензентом. Prompt judge содержал авторские expected properties и rubric. Пользовательский профиль judge сохранялся ради аутентификации. Независимая человеческая проверка решений judge не проводилась.

## Исполнение и ресурсы

Все 108 процессов генерации завершились со статусом ok, без timeout и пустых ответов. Средняя длительность одного job составила 40,09 секунды для baseline и 69,74 секунды для arch; медиана — 25,69 и 56,99 секунды соответственно.

Codex сообщил 352 393 токена для baseline и 1 071 088 для arch. Условие со skill использовало в 3,04 раза больше токенов. Эти числа взяты из stderr CLI и не подтверждают размер API billing. Средний финальный ответ arch был короче: 314 слов против 345 у baseline. Рост токенов пришёлся на внутреннюю работу агента, а не на длину ответа.

Средняя длительность одного вызова judge составила 75,52 секунды, медиана — 67,76 секунды. Суммарная длительность отдельных вызовов равна 4 077,81 секунды; два вызова выполнялись параллельно.

## Нарушения исполнения и изоляция

Каждый вызов генератора работал в новом временном project с запрошенным read-only sandbox. Команда отключала пользовательские rules и config. Проверка перед прогоном не нашла глобально установленный arch/SKILL.md в распространённых пользовательских каталогах skills. Профиль пользователя оставался доступен для аутентификации, поэтому полная изоляция baseline и judge не доказана.

Две treatment-генерации явно сообщили, что не смогли прочитать project-local skill из-за sandbox-сбоя:

- arch, python-old-pinned-dependency--run-001;
- arch, python-local-helper-diagram--run-001.

Обе пары завершились ничьей по preference и score. Они сохранены: исключение после просмотра результата сместило бы выборку. В arch, java-open-provider-dispatch--run-003 Codex также сообщил timeout при обновлении списка доступных моделей, но завершил ответ; эта пара дала +2 score и предпочтение arch.

Результат включает влияние данного harness и окружения; отдельно эффект текста skill не измерен.

## Контрольные суммы локальных артефактов

Generated run не коммитится согласно правилам репозитория. Локальная копия хранится в `/tmp/arch-benchmark-codex-gpt56sol-max-r3-20260819`.

| Файл | SHA-256 |
|---|---|
| manifest.json | 3bc42865004386ca9321b1ec858380f1277534a200cb4690b04688cd38010daa |
| results.json | 107ca9f8c205f2b3d85b084260316dc658716d2a2a820c5d067ae214aa7ea617 |
| blind/key.json | 648ad76f38bf71a0f5c991a05157fc2467f7de4f08df35164fdabb7d961e847b |
| blind/judgments.json | 18d5853e3bc85f535eb7873071fd1127a32cf0051ff573f378c488765fa620e2 |
| blind/judge-manifest.json | 170075ebc2a5826caaf70f11ba10d772ebf45de1bcfc6f952d0c5e9e1d3cc9b4 |
| blind/judge-results.json | b3ea3ac71a6dcbd7d1a8921f6d357a18aea8688001cf61dfbdc70ed17ece9b6d |
| blind/summary.md | f65c1887bc1b2cc8e694e634e1fbf8e1fd67d67e70862facd5a1fd7608f2a146 |

## Следующая проверка

Следующая содержательная оценка должна использовать скрытый набор или executable repository fixtures, независимый human spot-check и чистые профили генератора и judge. Отдельной проверки требуют clarify-маршрут, ложные срабатывания на skip-кейсах, Unicode-нормализация URL и трёхкратный расход токенов. Повтор после правок на этих же 18 кейсах останется tuning-измерением.
