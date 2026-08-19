# Language and ecosystem profiles

Use the repository's configured commands and versions first. The commands below are discovery options, not an instruction to add every tool. Confirm current syntax in official documentation before changing CI or dependencies.

## Contents

- [Cross-language pass](#cross-language-pass)
- [Python](#python)
- [JavaScript and TypeScript](#javascript-and-typescript)
- [Go](#go)
- [Rust](#rust)
- [JVM: Java and Kotlin](#jvm-java-and-kotlin)
- [.NET and C sharp](#net-and-c-sharp)
- [C and C++](#c-and-c)
- [Architecture-test selection](#architecture-test-selection)

## Cross-language pass

For every ecosystem:

1. Read the runtime and compiler targets.
2. Read both dependency declarations and resolved lock data.
3. Run the native build, test, type, and lint commands already used in CI.
4. Search for an existing repository implementation before an external package.
5. Check official deprecation and migration documentation for the exact target.
6. Verify a suggested package in the official registry and upstream repository.
7. Separate API age, release availability, support status, vulnerability, and actual reachability.
8. Use clone and complexity output as a review queue.

PMD Copy/Paste Detector supports multiple languages and can provide one clone baseline across a polyglot repository. Its token thresholds and language support still need repository-specific configuration.

## Python

### Design tendencies

- Prefer modules and functions until shared state or substitutable behavior justifies classes.
- Use standard parsers for URLs, paths, JSON, CSV, XML, dates, and shell arguments rather than ad hoc string handling.
- Preserve sync versus async semantics, context-manager cleanup, iterator behavior, and exception contracts.
- Treat monkey-patching, dynamic imports, decorators, and framework registration as hidden edges in an architecture map.
- Type-aware checks matter because many deprecations cannot be found from syntax alone.

### Existing-tool checks

Typical repository commands include:

    python -m pytest
    python -m compileall .
    ruff check .
    mypy .
    pyright
    python -m pip check
    python -m pip list --outdated
    pip-audit

Ruff C901 reports complex structures through McCabe complexity. Ruff UP035 finds selected deprecated imports. Import Linter can enforce contracts between Python packages. pip-audit checks installed or resolved Python dependencies against vulnerability data.

Do not add all of these to an unconfigured project. Inspect pyproject.toml, requirements files, lockfiles, tox.ini, and CI.

### Dependency cautions

Confirm the Python version range, implementation, platform wheels, native build requirements, extras, and resolver lock. An API replacement may be unavailable on the oldest supported Python. A library with infrequent releases can still be stable; inspect support statements and issues rather than cadence alone.

## JavaScript and TypeScript

### Design tendencies

- Distinguish build-time, server, browser, edge, and test dependencies.
- Account for ESM versus CommonJS, package exports, tree shaking, bundler conditions, and supported browsers or Node versions.
- Prefer discriminated unions and exhaustive checks for closed variants in TypeScript.
- Avoid registries, decorators, or dependency-injection containers for local fixed behavior.
- Use platform parsers for URLs, query strings, JSON, streams, paths, and internationalization.

### Existing-tool checks

Typical commands include:

    npm test
    npm run build
    npm run lint
    npm ls
    npm outdated
    npm audit

The typescript-eslint no-deprecated rule can report symbols annotated as deprecated and requires type information. dependency-cruiser can validate module dependency rules and cycles when already adopted.

Inspect package.json scripts, packageManager, engines, workspaces, tsconfig files, lockfile, bundler configuration, and CI before choosing a command. Do not rewrite a lockfile with a different package manager.

### Dependency cautions

Confirm exact package identity and scope. Package hallucination and typosquatting are material risks in npm's large namespace. Check registry ownership, upstream repository, exports, type declarations, license, transitive install scripts, runtime targets, and bundle impact. npm audit severity does not by itself establish runtime reachability.

## Go

### Design tendencies

- Prefer explicit control flow and small consumer-owned interfaces.
- Do not create interfaces only to mirror one concrete implementation.
- Use standard library packages for protocols, parsing, concurrency, and errors when they fit.
- Keep package dependencies acyclic; the compiler rejects import cycles.
- Preserve context cancellation, error wrapping, goroutine ownership, and resource closure.

### Existing-tool checks

Typical commands include:

    go test ./...
    go test -race ./...
    go vet ./...
    staticcheck ./...
    govulncheck ./...
    go list -m -u all
    go mod graph

Staticcheck SA1019 reports uses of deprecated code from declarations and documentation. govulncheck analyzes known vulnerabilities in dependencies and relates reports to usage. golangci-lint depguard can enforce allowed or denied imports when the repository already uses that aggregator.

Inspect go.mod, go.sum, toolchain directives, build tags, generated files, and CI. Do not run go mod tidy as a harmless inspection; it mutates dependency files.

### Dependency cautions

Semantic import versioning, minimum Go versions, module replacements, private proxies, and vendoring affect modernization. A major-version change can require a new import path.

## Rust

### Design tendencies

- Prefer enums and exhaustive match expressions for closed state and variants.
- Use traits for real behavioral substitution or boundaries, not for every type.
- Preserve ownership, lifetimes, Send and Sync constraints, error types, feature flags, and no_std requirements.
- Favor established crates for cryptography, protocols, and parsing after supply-chain review; keep trivial domain logic local.

### Existing-tool checks

Typical commands include:

    cargo check --all-targets
    cargo test
    cargo clippy --all-targets
    cargo tree
    cargo tree --duplicates
    cargo update --dry-run
    cargo deny check

Clippy supplies language-specific correctness and maintainability lints. cargo-deny can check advisories, licenses, sources, and duplicate versions when configured.

Inspect Cargo.toml, Cargo.lock, rust-toolchain files, workspace inheritance, feature matrices, target triples, and CI. Default-feature changes can alter behavior even when source APIs compile.

### Dependency cautions

Check MSRV, target support, unsafe code policy, native libraries, build scripts, proc macros, feature unification, and crate ownership. Do not replace an exhaustive match with trait objects merely to reduce branch count.

## JVM: Java and Kotlin

### Design tendencies

- Use sealed types and exhaustive switches or when expressions for closed variants when target versions support them.
- Introduce interfaces at ownership or external boundaries, not automatically between every layer.
- Preserve nullability, exception, transaction, threading, reflection, annotation-processing, and serialization behavior.
- Framework conventions can be architectural constraints; avoid parallel homemade containers or lifecycle systems.

### Existing-tool checks

Use the repository's Maven or Gradle wrapper. Typical checks include test, compilation, configured static analysis, and dependency reports. javac deprecation warnings can be enabled with:

    javac -Xlint:deprecation

ArchUnit can express and test package, class, layer, and cycle rules. jdeps can inspect Java dependencies. PMD and its Copy/Paste Detector can provide static and clone signals.

Do not assume a global Maven or Gradle version. Inspect wrapper files, toolchains, source and target compatibility, platform or BOM constraints, dependency locking, and plugin versions.

### Dependency cautions

Confirm JDK and bytecode targets, framework BOMs, binary and serialization compatibility, automatic modules, reflection configuration, shaded dependencies, and container runtime. Direct replacement of a deprecated API can change checked exceptions or null behavior.

## .NET and C sharp

### Design tendencies

- Use interfaces for substitutable behavior and boundaries with ownership value, not every service class.
- Prefer discriminated representations available in the project, exhaustive enum handling where analyzers support it, and direct functions for fixed local logic.
- Preserve async cancellation, disposal, nullable annotations, dependency-injection lifetimes, serialization contracts, and trimming or ahead-of-time requirements.

### Existing-tool checks

Typical commands include:

    dotnet build
    dotnet test
    dotnet package list --outdated
    dotnet package list --deprecated
    dotnet package list --vulnerable

With SDK versions before .NET 10, the package command uses the older verb-first form: dotnet list package. Confirm the installed SDK before scripting it. Compiler analyzers and warnings can detect deprecated symbols. NetArchTest can express architecture rules when a project already uses it.

Inspect global.json, target frameworks, Directory.Build files, central package management, lockfiles, runtime identifiers, analyzers, and CI.

### Dependency cautions

A package may support one target framework but not another in a multi-target project. Check assembly binding, strong names, source generators, native assets, trimming, and transitive framework references.

## C and C++

### Design tendencies

- Prefer explicit ownership and narrow interfaces. Treat lifetime, aliasing, undefined behavior, ABI, and error handling as architecture concerns.
- Use standard or proven libraries for complex parsing, cryptography, concurrency, and protocols only after checking toolchain and target constraints.
- Do not add virtual dispatch, templates, or inheritance solely to replace a short fixed switch.
- Preserve allocation, exception, real-time, embedded, and binary-size constraints.

### Existing-tool checks

Typical configured checks include compiler warnings, tests, sanitizers, clang-tidy, static analyzers, formatting, and build-matrix compilation. Useful compiler or analyzer signals include deprecated declarations, lifetime and ownership defects, unsafe APIs, and include dependencies.

clang-tidy provides modular checks but versions and check names follow the installed LLVM toolchain. Inspect CMake, Meson, Bazel, Make, Conan, vcpkg, lockfiles, compiler presets, target platforms, generated code, and CI.

### Dependency cautions

A source-compatible upgrade can still break ABI, link order, compiler support, exception or RTTI settings, or target platforms. Test every supported toolchain and relevant sanitizer configuration. Security-sensitive parsing needs fuzz or adversarial tests, not only example tests.

## Architecture-test selection

Use architecture tests for a stable rule whose violation has a demonstrated cost, such as domain packages not importing transport, plugins not importing each other, or adapters being the only consumers of an SDK.

Prefer:

- existing compiler or module boundaries;
- existing linter import rules;
- a small dependency-graph assertion;
- an ecosystem tool already in the repository.

Add a new framework only when the rule is important, repeated, and otherwise difficult to enforce. Document allowed exceptions and ownership.
