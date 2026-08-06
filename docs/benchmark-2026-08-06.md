# Поведенческая оценка: Codex gpt-5.6-sol

Дата прогона: 6 августа 2026 года.

## Вывод

Первый зафиксированный парный прогон не показал общего прироста качества от arch. Средний adjusted score составил 13,52 из 14 в обоих условиях; средняя парная дельта arch − baseline равна +0,00. Judge предпочёл arch в 13 парах, baseline в 10, ещё 19 пар признал равными. Critical errors отсутствовали.

Результат различается по маршрутам. Arch дал +0,33 балла на задачах, где требовалось изменение, и уступил на задачах, где следовало сохранить конструкцию или запросить данные. Поэтому результат не подтверждает общий quality lift. Данных для утверждения об эквивалентности условий недостаточно. Набор мал, ответы близки к потолку rubric, а независимой человеческой оценки не было.

## Результаты

| Маршрут | Пар | Baseline | Arch | Дельта | Победы baseline | Победы arch | Ничьи |
|---|---:|---:|---:|---:|---:|---:|---:|
| apply | 18 | 13,61 | 13,94 | +0,33 | 2 | 7 | 9 |
| skip | 12 | 13,67 | 13,50 | −0,17 | 3 | 2 | 7 |
| clarify | 12 | 13,25 | 12,92 | −0,33 | 5 | 4 | 3 |
| все | 42 | 13,52 | 13,52 | +0,00 | 10 | 13 | 19 |

Дельта score была положительной в 10 парах, отрицательной в 9 и нулевой в 23. Preference и score расходятся, потому что judge выбирал лучший ответ с учётом практического риска даже при равной целочисленной сумме. Штраф architecture theater составил 3 балла для baseline и 1 для arch. В обоих условиях было 0 critical errors.

Средние оценки по семи измерениям почти совпали:

| Измерение | Baseline | Arch | Дельта |
|---|---:|---:|---:|
| evidence and repository grounding | 1,98 | 1,98 | +0,00 |
| reuse and dependency accuracy | 1,93 | 1,90 | −0,02 |
| architectural fit | 1,98 | 1,98 | +0,00 |
| simplicity and maintainability | 1,98 | 2,00 | +0,02 |
| language and API accuracy | 1,81 | 1,79 | −0,02 |
| verification and migration safety | 1,93 | 1,90 | −0,02 |
| clarity and actionability | 2,00 | 2,00 | +0,00 |

## Конфигурация генерации

- commit harness: acb64e0;
- содержимое skill совпадало с commit 60472e1;
- SHA-256 skill: 295e5e3926c4a5c12a4c6a9a468ab315d24557d476986db1e652deeb96dc46d0;
- Codex CLI: 0.146.1;
- модель: gpt-5.6-sol;
- reasoning effort: max;
- prompt-policy version: 2;
- seed: 20260806;
- timeout одного job: 600 секунд;
- параллельных jobs: 2;
- 14 заранее заданных кейсов, 3 повтора, 2 условия, 84 генерации и 42 пары.

Кейсы: python-url-regex-parser, typescript-existing-retry-helper, java-open-provider-dispatch, csharp-domain-http-boundary, javascript-hallucinated-package, go-deprecated-ioutil, rust-exhaustive-reducer, go-small-wire-switch, python-bounded-tag-regex, independent-vendor-mappers, python-old-pinned-dependency, typescript-retry-library-choice, java-complexity-threshold-only и cpp-major-upgrade-abi.

Точная команда:

~~~sh
python3 evals/run_eval.py \
  --runs 3 \
  --jobs 2 \
  --seed 20260806 \
  --timeout 600 \
  --agent codex \
  --output-dir /tmp/arch-benchmark-codex-gpt56sol-max-r3-20260806 \
  -- codex exec --ephemeral --ignore-user-config --ignore-rules \
    --sandbox read-only --skip-git-repo-check \
    --model gpt-5.6-sol -c 'model_reasoning_effort="max"' \
    --color never -
~~~

Перед основным прогоном один отдельный pilot на rust-exhaustive-reducer дал ничью 14:14. Pilot не входит в 42 опубликованные пары. Кейсы, skill и rubric после просмотра основного результата не менялись. После прогона scorer получил только разбиение уже существующих оценок по маршрутам и измерениям.

## Blind judge

Пары были ослеплены с seed 9173. Judge не видел key.json. Все 42 вызова завершились валидным JSON без timeout.

- Claude Code CLI, зафиксированный перед прогоном: 2.1.222;
- запрошенная модель: opus;
- resolved model из metadata ответов: claude-opus-5;
- во всех ответах metadata также указывала helper model claude-haiku-4-5-20251001;
- суммарная стоимость по metadata: 9,320446 доллара США;
- web search requests: 0.

Точные команды blinding, judge и scoring:

~~~sh
python3 evals/build_blind_pairs.py \
  --seed 9173 \
  /tmp/arch-benchmark-codex-gpt56sol-max-r3-20260806
python3 evals/run_judge.py \
  --jobs 2 \
  --timeout 600 \
  /tmp/arch-benchmark-codex-gpt56sol-max-r3-20260806/blind \
  -- claude --print --model opus --effort max \
    --output-format json --no-session-persistence \
    --disable-slash-commands --max-budget-usd 1.00
python3 evals/score_judgments.py \
  /tmp/arch-benchmark-codex-gpt56sol-max-r3-20260806/blind
~~~

Judge использовал другую модель, работал вслепую к соответствию A/B и оставался автоматическим рецензентом без независимой человеческой проверки. Prompt judge содержал авторские expected properties и rubric. В паре python-url-regex-parser--run-003 judge получил два отказа на запуск Bash-команд для локальной проверки urllib.parse; итоговый JSON был валиден, влияние отказов на решение неизвестно.

## Исполнение и стоимость

Все 84 процесса завершились со статусом ok, без timeout и пустых ответов. Средняя длительность одного job была 47,80 секунды для baseline и 81,08 секунды для arch; медиана — 33,49 и 65,03 секунды соответственно. Codex сообщил 210 883 токена для baseline и 637 685 для arch, то есть в 3,02 раза больше для условия со skill. Эти числа взяты из stderr CLI и не равны подтверждённому API billing.

Средний финальный ответ arch был короче: 314 слов против 342 у baseline. Дополнительные токены расходовались на работу агента, а не на увеличение ответа пользователю.

## Нарушения исполнения

Каждый вызов работал в новом временном project с read-only sandbox. Команда отключала пользовательские rules и config, а проверка перед прогоном не нашла глобально установленный arch/SKILL.md. Профиль пользователя оставался доступен для аутентификации, поэтому полная изоляция не доказана.

Три генерации сообщили о sandbox-сбое при доступе к окружению:

- arch, java-open-provider-dispatch--run-001: локальная guidance не прочитана;
- arch, rust-exhaustive-reducer--run-002: локальная guidance не прочитана;
- baseline, typescript-retry-library-choice--run-003: repository search не выполнен.

Первые два случая нарушают treatment compliance и совпадают с двумя проигрышами arch по score. Исключение этих пар после просмотра результата исказило бы выборку, поэтому они сохранены. Сбой baseline также сохранён. Общий вывод следует читать как результат данного harness и окружения, а не как чистую оценку текста skill.

## Контрольные суммы локальных артефактов

Generated run не коммитится согласно правилам репозитория. Для сверки сохранённой локальной копии указаны контрольные суммы:

| Файл | SHA-256 |
|---|---|
| manifest.json | 028a9f920eca20f451dd6d7e70a5783f347dd51f4ec2ca7dd07618906838fa40 |
| results.json | 019aa1fb6fe724a5a73d59d96fe8db557553868e96d5bc28690ceac0ea4e182b |
| blind/key.json | 26a3880dc15980256ffd9deec10e442a73dc567d821f2a780dd53537f2073453 |
| blind/judgments.json | 4664e7459e44f97e9dd6210ca60cf7ef70ff5133ca21542da68b3900ebbdab2a |
| blind/judge-manifest.json | 89f7faa5dc5dbe11acfea802fd6ecfbe34c394b069dc83960e79cbfc30bb128d |
| blind/judge-results.json | 4625e4908d8b8bdecbfa84175fc68fb672b864969891cb5c32cf71516b944c7a |
| blind/summary.md | 022f910512f3cc15830440dd0d90375e41d0118c6954dce3d291267d2ded466f |

## Следующая проверка

Повтор на тех же кейсах после правки skill будет tuning на test set. Следующая содержательная оценка должна использовать скрытый набор или executable repository fixtures, независимый human spot-check и чистые профили генератора и judge. Отдельные гипотезы для новой версии: сократить clarify-ответы до конкретных repository targets и проверок runtime, связывать verification в skip-ответах с остаточным риском и выбирать newest compatible dependency вместо автоматического перехода на последний major.
