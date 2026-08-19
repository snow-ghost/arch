# Architecture Guard for Code Agents

Agent Skill для архитектурного надзора над сгенерированным и существующим кодом. Скилл помогает агенту найти уже реализованное поведение, проверить зависимости и API, обнаружить вредную связанность и выбрать минимальную языково-идиоматичную конструкцию. Для межмодульных задач он строит укрупнённые архитектурные представления с привязкой узлов и связей к доказательствам из репозитория.

Один пакет поддерживает Codex, Claude Code, Cursor и OpenCode. Каноническая реализация хранится в skills/arch; продуктовые манифесты содержат только метаданные и ссылку на этот каталог.

Статус: версия 0.1 — исследовательский прототип. Методика, тесты и парный eval harness реализованы. Первый зафиксированный прогон на Codex gpt-5.6-sol не показал общего прироста: средняя парная дельта составила +0,00, arch выиграл 13 сравнений, baseline — 10, ещё 19 завершились ничьей. Результат и ограничения описаны в [отчёте от 6 августа 2026 года](docs/benchmark-2026-08-06.md).

## Что проверяет скилл

- повтор уже существующего поведения в репозитории;
- ручную реализацию возможностей стандартной библиотеки или принятой зависимости;
- выдуманные, устаревшие, неподдерживаемые, уязвимые или несовместимые зависимости;
- deprecated API с учётом целевой версии среды;
- нарушение направления зависимостей, циклы и неясное владение состоянием;
- концентрацию решений и обязанностей, затрудняющую проверку и изменение;
- regex и локальные обходы, подменяющие структурный parser;
- абстракции и паттерны без текущей вариативности или границы;
- попытки улучшить метрику переносом той же сложности в новые классы и регистрации.
- компонентные и dependency-графы, sequence, DFD, process, state, ownership, deployment и IDEF0-представления с подходящим масштабом.

Скилл допускает старую зависимость, дублирование, switch, exhaustive match или regex, если они соответствуют контракту и имеют меньшую стоимость владения. Возраст, число строк и порог метрики используются как сигналы для проверки.

## Установка

Universal Skills CLI устанавливает скилл для одного или нескольких агентов:

~~~sh
npx skills add snow-ghost/arch --skill arch
~~~

Целевая установка:

~~~sh
npx skills add snow-ghost/arch --skill arch \
  -a codex -a claude-code -a cursor -a opencode
~~~

Перед выдачей доступа проверьте поведение стороннего установщика. Для ручной установки скопируйте весь каталог skills/arch:

| Агент | Каталог проекта | Каталог пользователя |
|---|---|---|
| Codex | .agents/skills/arch | ~/.agents/skills/arch |
| Claude Code | .claude/skills/arch | ~/.claude/skills/arch |
| Cursor | .cursor/skills/arch | ~/.cursor/skills/arch |
| OpenCode | .opencode/skills/arch или .agents/skills/arch | ~/.config/opencode/skills/arch или ~/.agents/skills/arch |

Claude Code может загрузить checkout как plugin:

~~~sh
claude --plugin-dir .
~~~

В plugin-режиме команда имеет вид /arch:arch, при отдельной установке — /arch. В Codex скилл вызывается как $arch. Cursor и OpenCode показывают arch в интерфейсе skills или slash-команд.

## Применение

Явный вызов:

~~~text
Use $arch to review this generated client. Search the repository before adding helpers,
verify every package and deprecated API, and keep only evidence-backed findings.
~~~

Ревью без изменений:

~~~text
Проверь diff на дублирование поведения, нарушение границ, устаревшие API,
необоснованные абстракции и хрупкий parsing. Код не меняй.
~~~

Модернизация:

~~~text
Обнови зависимости в пределах заявленных runtime targets. Используй официальные
migration notes, сохрани lockfile determinism и перечисли непроверенные риски.
~~~

Архитектурное представление:

~~~text
Построй as-is component graph затронутого checkout-пути и sequence оплаты.
Покажи компоненты, а детали классов оставь в evidence index. Привяжи узлы и связи к путям, registrations
и тестам; отдели наблюдаемое от inferred, unknown и proposed.
~~~

Контрпример:

~~~text
В Rust reducer есть exhaustive match по закрытому enum. Не заменяй его паттерном,
если компиляторная полнота и локальность дают более простой дизайн.
~~~

## Устройство репозитория

~~~text
skills/arch/
  SKILL.md
  agents/openai.yaml
  references/
.codex-plugin/plugin.json
.claude-plugin/plugin.json
.cursor-plugin/plugin.json
evals/
tests/
docs/
~~~

Основной файл содержит короткий рабочий алгоритм. Справочники подгружаются по задаче: методика ревью, архитектурные представления, выбор дизайна, метрики, языковые инструменты, примеры и научные источники.

## Проверка

Зависимости Python не требуются:

~~~sh
python3 -m unittest discover -s tests -v
python3 evals/run_eval.py --dry-run
~~~

Дополнительные проверки разработки:

- Agent Skill validator;
- Codex plugin validator;
- расширенный технический lint русскоязычной документации;
- компиляция Python-скриптов.

Актуальные результаты указаны в [отчёте об оценке](docs/evaluation.md).

## Benchmark

Создать prompts без вызова модели:

~~~sh
python3 evals/run_eval.py --dry-run
~~~

Запустить три повтора для выбранных кейсов через Codex:

~~~sh
python3 evals/run_eval.py \
  --runs 3 \
  --case python-url-regex-parser \
  --case rust-exhaustive-reducer \
  --case python-old-pinned-dependency \
  -- codex exec --sandbox read-only --skip-git-repo-check -
~~~

Ослепить пары, запустить judge и посчитать результат:

~~~sh
python3 evals/build_blind_pairs.py evals/runs/RUN_ID
python3 evals/run_judge.py --jobs 2 evals/runs/RUN_ID/blind \
  -- JUDGE_COMMAND
python3 evals/score_judgments.py evals/runs/RUN_ID/blind
~~~

Runner создаёт отдельный временный project для каждой генерации. Условие arch получает локальный skill, baseline — нет. Пользовательский профиль агента остаётся доступен для аутентификации, поэтому глобально установленные инструкции следует отдельно проверить.

Кейсы включают три типа правильного решения: применить изменение, оставить подходящую конструкцию, запросить недостающие данные. Архитектурные кейсы также проверяют выбор масштаба и вида, отказ от лишней диаграммы и честное отображение неизвестных runtime-связей. Rubric штрафует архитектурный театр, ложную визуальную точность и выдуманные факты. Подробности: [evals/README.md](evals/README.md).

## Материалы

- [Исследование](docs/research.md)
- [План и границы версии 0.1](docs/plan.md)
- [Методика и результаты оценки](docs/evaluation.md)
- [Первый поведенческий benchmark](docs/benchmark-2026-08-06.md)
- [Аннотированные первичные источники](skills/arch/references/sources.md)
- [Правила архитектурных представлений](skills/arch/references/architecture-views.md)

## Лицензия

MIT, см. [LICENSE](LICENSE).
