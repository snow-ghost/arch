# Исследование архитектурных дефектов LLM-кода

Дата среза: 19 августа 2026 года.

## Задача

Исследование отвечает на пять вопросов:

1. Какие дефекты возникают при генерации и длительном развитии кода агентами?
2. Какие меры дают проверяемый эффект?
3. Какие сигналы допускают автоматизацию?
4. Где язык и экосистема меняют архитектурное решение?
5. Какие архитектурные представления помогают проверке кода и где они создают ложную точность?

Выводы используются как основания workflow. Они не задают универсальный порог качества.

## Основные результаты

### Структурная деградация на длинном горизонте

[SlopCodeBench](https://arxiv.org/abs/2603.24755) исследует 36 Python-задач, 15 агентов и 196 промежуточных checkpoints. Ни один агент не решил целую задачу по строгому критерию. Structural erosion вырос в 77 процентах траекторий, verbosity — в 75,5 процента. В сравнении с 473 open-source Python-проектами agent code оказался в 2,3 раза многословнее и в 2,0 раза структурно эродированнее по метрикам работы.

Quality prompt уменьшал часть начальных дефектов, но не останавливал деградацию между checkpoints. В работе также зафиксированы рост стоимости и небольшое снижение correctness при таком prompting.

Следствие для скилла: тесты результата дополняются сравнением структуры по ходу изменения. Порог и детекторы SlopCodeBench остаются характеристиками Python benchmark, а не общим CI-стандартом.

[Preprint об architectural smells](https://arxiv.org/abs/2605.02741) сообщает о method bloat, God classes, redundant implementation и coupling в небольшой выборке MetaGPT. Размер кода сильно коррелировал с числом smells в этой постановке. Ограничения включают одну систему, малую выборку и preprint-статус. Работа поддерживает triage по росту размера, но не универсальную зависимость.

### Static analysis находит разные классы проблем

[Исследование 4066 Java- и Python-фрагментов](https://arxiv.org/abs/2307.12596) обнаружило 1930 фрагментов с maintainability или style issues по static analyzers. Доминирующие предупреждения различались между языками, а инструменты имели неполное пересечение. Static и runtime feedback исправляли часть результатов.

Постановка использовала более ранний ChatGPT и snippet-задачи. Число 47 процентов описывает данную выборку. Практический вывод ограничен: нужен набор repository-native проверок, подходящий языку; один linter не заменяет анализ механизма.

### Недостаток repository context ведёт к выдуманным API и повтору кода

[RepoCoder](https://arxiv.org/abs/2303.12570) использует итеративный retrieval repository context и показывает прирост более 10 процентов относительно in-file completion в своих тестах. [De-Hallucinator](https://arxiv.org/abs/2401.01701) извлекает project API references и сообщает прирост correct API recall в исследованных условиях. [DocPrompting](https://arxiv.org/abs/2207.05987) извлекает документацию до генерации и улучшает результаты на своём наборе задач.

Эти работы поддерживают обязательный поиск callers, helpers, tests, manifests и lockfiles до генерации. Они не доказывают, что retrieval автоматически выбирает правильную архитектуру.

### Модели используют deprecated API и устаревшее знание

[Работа ICSE 2025](https://arxiv.org/abs/2406.09834) проверила семь LLM, 145 deprecated-to-current mappings, восемь Python-библиотек и 28125 prompts. Доля deprecated API среди правдоподобных completions зависела от модели и контекста и оставалась существенной.

[Preprint 2026 года об evolving API](https://arxiv.org/abs/2604.09515) сообщает рост executable migrations при передаче структурированной документации. Конфликт со старым параметрическим знанием сохранялся.

Следствие: target runtime читается из репозитория, а статус API проверяется по текущей официальной документации. Замена требует проверки сигнатуры, return value, errors и поведения. Название replacement не гарантирует совместимость.

### Названия пакетов требуют отдельной верификации

[USENIX Security 2025 Distinguished Paper](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen) анализирует 576000 Python- и JavaScript-генераций 16 моделей. Авторы нашли hallucinated packages во всех исследованных группах и 205474 разных выдуманных названия.

Следствие: model-suggested package считается непроверенным вводом. До установки проверяются официальный registry, upstream repository, точное имя, владелец, license, target compatibility и transitive cost. Правдоподобное имя само по себе не подтверждает существование пакета.

### Тесты ограниченно защищают dependency update

[Исследование 262 Java-проектов](https://arxiv.org/abs/2109.11921) внедряло faults в обновления зависимостей. Test suites находили в среднем 47 процентов faults в direct dependencies и 35 процентов в transitive dependencies.

Метод с injected faults имеет ограничения. Для скилла он обосновывает сочетание tests, static analysis, release и migration notes, API usage inspection и build matrix.

### Данные по безопасности зависят от постановки

[Ранняя работа о GitHub Copilot](https://arxiv.org/abs/2108.09293) получила около 40 процентов уязвимых программ в 89 security-сценариях. [Контролируемое исследование пользователей](https://arxiv.org/abs/2211.03622) зафиксировало менее безопасные решения и избыточную уверенность группы с AI assistant. [USENIX Security 2023](https://www.usenix.org/conference/usenixsecurity23/presentation/sandoval) на 58 участниках и одной C-задаче не обнаружил крупного роста critical security bugs.

Общий вывод ограничен: generated code требует threat-specific проверки. Формула «LLM-код всегда небезопасен» противоречит неоднородным данным.

### Clone detector не выдаёт готовое решение

[Исследование восьми систем](https://ink.library.smu.edu.sg/sis_research/6193/) сообщает, что 61–84,7 процента найденных clones не были harmful по мере consistent maintenance. [PMD CPD](https://pmd.github.io/pmd/pmd_userdocs_cpd.html) предоставляет token-based поиск кандидатов во многих языках.

Следствие: finding о дублировании требует общего policy ownership, divergence или change coupling. Дублирование между независимыми adapters сохраняет раздельное владение; общая функция создаёт зависимость между boundaries.

### Code smell и metric требуют причинной интерпретации

[Систематический обзор code smells](https://www.mdpi.com/2078-2489/9/11/273) и [обзор связи smells с faults](https://arxiv.org/abs/2004.10777) показывают неоднородность определений, detectors, thresholds и результатов.

Cyclomatic complexity, cognitive complexity, clone percentage, fan-out и file size используются как очередь для чтения. Изменение оправдывает механизм: дефект, цикл, несколько источников истины, сложная проверка, нестабильная граница или измеренный cost.

SlopCodeBench определяет complexity mass функции как cyclomatic complexity, умноженную на квадратный корень из SLOC. Structural erosion — доля общей массы в функциях с complexity выше 10. Формула подходит для репликации benchmark и локальной динамики; перенос порога на другой язык требует проверки.

### Паттерны имеют собственную стоимость

[Исследование метрик design patterns](https://doaj.org/article/a4555bd1dbac445ca13360fbbb2a8420) показывает возможность снижения cyclomatic complexity одновременно с ростом числа классов и SLOC. [Работа об object-oriented overkill](https://scholars.duke.edu/publication/758386), [исследование untangling dependency cycles](https://arxiv.org/abs/2306.10599) и [исследование architectural complexity в Google](https://research.google/pubs/understanding-architectural-complexity-maintenance-burden-and-developer-sentiment-a-large-scale-study/) связывают оценку архитектуры с контекстом и burden разработки.

Следствие: Strategy требует независимой вариативности поведения, State Machine — переходов и temporal state, Adapter — внешней границы. Небольшой закрытый switch и compiler-checked exhaustive match сохраняются, если дают меньшую стоимость.

### Regex оценивается по grammar и exposure

[OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) и [MITRE CWE-1333](https://cwe.mitre.org/data/definitions/1333.html) описывают excessive backtracking на crafted inputs. [Документация urllib.parse](https://docs.python.org/3/library/urllib.parse.html) отдельно предупреждает о необходимости validation при security-sensitive использовании URL parser.

Regex подходит для ограниченного regular language. Nested grammar, quoting, escaping, evolving standard и untrusted input с backtracking требуют специализированного parser, bounds и adversarial tests. Переход на standard parser не отменяет policy validation.

### Представление архитектуры выбирается по вопросу

[C4 model](https://c4model.com/abstractions) задаёт уровни software system, container, component и code. [Рекомендации C4 по диаграммам](https://c4model.com/diagrams) допускают выбор только тех уровней, которые приносят пользу аудитории. Для скилла это означает укрупнение файлов и символов до подтверждённых границ ответственности, runtime, данных или внешнего контракта.

[OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html) включает в DFD внешние сущности, процессы, хранилища, потоки данных и trust boundaries. Такой вид подходит для security-relevant движения данных. DFD служит входом для threat analysis и сам по себе не доказывает безопасность.

Официальная документация Mermaid описывает [flowchart](https://mermaid.js.org/syntax/flowchart.html), [sequence](https://mermaid.js.org/syntax/sequenceDiagram.html) и [state](https://mermaid.js.org/syntax/stateDiagram.html). [C4-синтаксис Mermaid](https://mermaid.js.org/syntax/c4.html) имеет статус experimental. Поэтому скилл предпочитает формат репозитория, а при его отсутствии — переносимые flowchart, sequence и state без новой runtime-зависимости.

[FIPS PUB 183](https://nvlpubs.nist.gov/nistpubs/Legacy/FIPS/fipspub183.pdf) определял IDEF0 через input, control, output и mechanism. [Индекс NIST](https://www.nist.gov/system/files/documents/2016/12/15/withdrawn_fips_by_numerical_order_index.pdf) указывает, что стандарт отозван 2 сентября 2008 года. IDEF0 остаётся опциональной legacy-нотацией для существующих требований; Mermaid-аппроксимация не считается строгим соответствием.

Следствие: диаграмма получает вопрос, snapshot, scope, viewpoint и статус as-is или to-be. Материальные узлы и связи имеют evidence IDs, а observed, inferred, proposed и unknown отношения разделяются. Для локального helper с одним caller, без I/O, state и boundary используется текстовая карта: набор диаграмм не добавляет проверяемых отношений.

## Отличия языков

| Экосистема | Предпочтение | Специфический риск | Примеры проверки |
|---|---|---|---|
| Python | функции и модули до появления реальной вариативности | dynamic API, runtime-only paths, resolver и wheel compatibility | Ruff, type checker, pip check, pip-audit, Import Linter |
| JavaScript и TypeScript | discriminated unions для закрытых вариантов, platform parsers | package identity, ESM/CJS, browser и bundle targets | TypeScript, ESLint, npm outdated/audit, dependency-cruiser |
| Go | прямой control flow и consumer-owned small interfaces | context, goroutine ownership, module path, build tags | go test, vet, Staticcheck SA1019, govulncheck |
| Rust | enums и exhaustive match для закрытого мира | feature flags, MSRV, unsafe, build scripts | cargo check/test/clippy, cargo tree, cargo-deny |
| JVM | sealed variants и framework-aware boundaries | bytecode target, BOM, reflection, transactions | wrapper build, javac deprecation, ArchUnit, jdeps |
| .NET | явные async, disposal и DI lifetime contracts | multi-targeting, trimming, source generators | dotnet build/test, package list status, analyzers |
| C и C++ | явное ownership и узкие boundaries | ABI, undefined behavior, compilers, target matrix | warnings, sanitizers, clang-tidy, matrix build |

Команды зависят от версий. skills/arch/references/language-tooling.md требует сначала использовать конфигурацию проекта и сверять текущую официальную документацию.

## Архитектура скилла

Рабочий алгоритм состоит из шести проверяемых решений:

1. Установить scope, contracts и target versions.
2. Построить локальную карту callers, data ownership, tests и dependency direction.
3. Выбрать нужный архитектурный вид и масштаб или явно отказаться от диаграммы.
4. Пройти reuse ladder.
5. Для finding связать signal с harm mechanism.
6. Выбрать минимальную correction и проверку.

Подробные справочники загружаются условно. Такой дизайн учитывает результаты [SkillsBench](https://arxiv.org/abs/2602.12670), где curated skills в среднем помогали, но отдельные skills ухудшали результат, и [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401), где средний эффект public SWE skills был мал, а version-mismatched guidance давала ухудшение. Обе оценки зависят от набора задач; SWE-Skills-Bench на дату среза имеет preprint-статус.

## Проверяемые гипотезы

Версия 0.1 проверяет следующие гипотезы:

- repository-first поиск уменьшает предложение duplicate helpers и внешних packages;
- evidence schema снижает ложные findings по regex, switch, clone и age;
- language profiles уменьшают перенос объектных паттернов в Go и Rust;
- evidence-backed views уменьшают выдуманные runtime-связи и избыточную детализацию архитектурных карт;
- current-documentation step уменьшает ошибки по deprecated API и dependency migration;
- штраф architecture_theater снижает лишние layers без ухудшения correctness.

Eval сравнивает arch с baseline на одинаковых prompts. До поведенческого прогона гипотезы остаются гипотезами.
