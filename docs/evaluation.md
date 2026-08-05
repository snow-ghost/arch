# Оценка Architecture Guard

Дата среза: 5 августа 2026 года.

## Вопрос оценки

Основной вопрос: улучшает ли arch решение архитектурных задач по сравнению с тем же агентом и тем же prompt без локального скилла?

Успех означает более точную калибровку решения. Условие arch должно находить доказанное нарушение, сохранять подходящую прямую конструкцию и откладывать изменение при недостатке данных.

## Дизайн

Каждый job получает новый временный project. Baseline не содержит локального skill. Условие arch получает копию skills/arch в каталоге выбранного агента. Порядок jobs перемешивается фиксированным seed.

Обеим условиям передаётся общий prompt policy:

- использовать только факты задачи;
- отделять допущения от доказательств;
- указывать остаточные риски;
- указывать результаты, которые ещё не измерены;
- выдавать прямой инженерный ответ без описания внутренней методики.

Manifest фиксирует cases, условия, число повторов, seed, timeout, команду, platform path, версию prompt policy и SHA-256 содержимого skill.

Пользовательский профиль агента сохраняется ради аутентификации. Этот профиль может содержать глобальные skills и инструкции. Отчёт обязан указывать данное ограничение или использовать отдельный чистый профиль.

## Набор кейсов

В версии 0.1 содержится 14 кейсов:

- apply: 6;
- skip: 4;
- clarify: 4.

Языковые контексты: Python, TypeScript или JavaScript, Go, Rust, Java, Kotlin, C# и C++.

Кейсы охватывают repository reuse, deprecated API, package hallucination, dependency direction, открытый и закрытый dispatch, безопасный и хрупкий regex, intentional duplication, version pinning, complexity metric и ABI migration.

Контрпримеры обязательны. Eval, состоящий только из задач с ожидаемым рефакторингом, поощряет лишнее вмешательство.

## Blind A/B

build_blind_pairs.py случайно назначает baseline и arch меткам A и B. Judge получает задачу, task-specific expected properties, rubric и два ответа. key.json хранится отдельно.

Семь измерений оцениваются от 0 до 2:

- evidence and repository grounding;
- reuse and dependency accuracy;
- architectural fit;
- simplicity and maintainability;
- language and API accuracy;
- verification and migration safety;
- clarity and actionability.

Дополнительный штраф architecture_theater от 0 до 3 применяется за слои, паттерны, метрики и процесс, которые вытесняют конкретное решение. Critical errors учитываются отдельно.

## Отчётные показатели

Для каждой серии следует публиковать:

- предпочтения baseline, arch и tie;
- средний paired delta adjusted score;
- распределение delta по кейсам;
- critical errors по условиям;
- timeout и ошибки запуска;
- результаты отдельно для apply, skip и clarify;
- точную модель, параметры, команду и commit;
- skill digest и prompt-policy version;
- judge и способ проверки его независимости;
- число повторов и способ выбора кейсов.

Одна средняя величина не показывает ложные срабатывания. Результат по маршрутам нужен для оценки склонности агента к лишней архитектуре.

## Текущий статус

Реализация runner, blind-pair builder, scorer, rubric и 14 кейсов завершена.

Поведенческие генерации baseline и arch ещё не проводились. Прирост качества, preference rate и score delta не заявлены.

Локальная структурная проверка 5 августа 2026 года дала следующие результаты:

- 16 unit tests: passed;
- Agent Skill validator: passed;
- Codex plugin validator: passed;
- Claude Code plugin validate --strict: passed;
- OpenCode debug skill: обнаружил arch и загрузил его из project-local path;
- Python compilation для evals и tests: passed;
- полный dry-run: 14 кейсов, 28 jobs, 28 dry-run artifacts;
- расширенный technical-style lint русскоязычных документов: passed после разбора четырёх предупреждений.

Cursor manifest покрыт repository tests. Нативный Cursor runtime test не запускался: CLI отсутствует в среде разработки.

Эти результаты подтверждают структуру и воспроизводимость harness. Они не измеряют качество ответов модели.

## Угрозы валидности

- результат зависит от модели, даты, reasoning mode и sampling;
- пользовательский профиль может загрязнить baseline;
- judge может предпочитать стиль, длину или формулировки rubric;
- task-specific oracle отражает решения авторов набора;
- выбранные после tuning кейсы завышают оценку;
- prompt может раскрыть наличие skill косвенно;
- advisory-ответ не доказывает корректность будущего patch;
- 14 синтетических кейсов не представляют все языки и репозитории.

Сильный результат требует независимых повторов, скрытого набора, human spot-check и, где возможно, executable verification.
