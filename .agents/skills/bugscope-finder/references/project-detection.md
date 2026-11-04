# Project detection (Phase 0)

The goal is to learn how *this* project is built before reasoning about where a bug lives.
A bug skill that assumes a stack will confidently search the wrong directories and produce a
plan that looks rigorous and points at nothing.

Detection runs in two tiers. Stop as soon as you have enough to search the codebase
intelligently — this phase is a lookup, not an audit.

## Tier 1 — the project's own agent configuration (authoritative)

These files are written by the team for agents. They beat anything you infer, because they
encode intent ("we're migrating off X", "tests run via `make check`, not `pytest`") that no
amount of file-sniffing recovers.

Read whichever exist, in this order:

| Path | Written for |
|---|---|
| `AGENTS.md`, `.agents/*.md` | The cross-vendor agent convention |
| `CLAUDE.md`, `.claude/CLAUDE.md` | Claude Code |
| `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` | GitHub Copilot |
| `.cursor/rules/*.mdc`, `.cursorrules` | Cursor |
| `.windsurfrules`, `.aider.conf.yml`, `.junie/guidelines.md` | Other agent tools |
| `CONTRIBUTING.md`, `docs/architecture*.md` | Humans, but usually accurate |

Extract, and quote in the plan:

- **Stack and versions** as the team states them.
- **Test and build commands** verbatim. Your Success criteria must use *their* command, not
  a plausible-looking one — `npm test` in a repo that uses `pnpm vitest run` is a broken
  success criterion.
- **Directory layout conventions**: where features live, where tests live.
- **Local rules that constrain a fix**: "never edit files under `generated/`", "all HTTP
  goes through `ApiClient`", "no new dependencies without an ADR".

If Tier 1 answers everything, skip Tier 2.

## Tier 2 — manifest heuristics (fallback)

Used when there is no agent config, or it is silent on something you need. Read the
manifest itself; a filename tells you the ecosystem, the contents tell you the framework.

| Manifest / marker | Ecosystem | Then read for the framework |
|---|---|---|
| `package.json` | Node / browser | `dependencies` — `@angular/core`, `react`, `vue`, `svelte`, `next`, `express`, `fastify`, `nestjs` |
| `tsconfig.json` | TypeScript | `compilerOptions.paths` for module aliases |
| `deno.json`, `jsr.json` | Deno | |
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py` | Python | `django`, `flask`, `fastapi`, `pytest` |
| `manage.py` | Python | Django, definitively |
| `go.mod` | Go | `module` line for the import prefix; `gin`, `echo`, `chi` in `require` |
| `Cargo.toml` | Rust | `axum`, `actix-web`, `tokio` |
| `pom.xml`, `build.gradle(.kts)` | JVM | `spring-boot`, `quarkus`, `micronaut` |
| `*.csproj`, `*.sln`, `Directory.Build.props` | .NET | `Microsoft.NET.Sdk.Web` → ASP.NET Core |
| `Gemfile` | Ruby | `rails`, `sinatra` |
| `composer.json` | PHP | `laravel/framework`, `symfony/*` |
| `pubspec.yaml` | Dart / Flutter | |
| `Package.swift`, `*.xcodeproj` | Swift | |
| `mix.exs` | Elixir | `phoenix` |
| `Dockerfile`, `docker-compose.yml` | — | Runtime versions, service topology, entrypoint commands |
| `Makefile`, `Taskfile.yml`, `justfile` | — | The real test/build commands, often better than the manifest's |

**Monorepos.** `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `go.work`, a
Cargo `[workspace]`, or a `packages/`–`apps/` split means the answer is per-package. Detect
the stack of the package the bug lives in, and say so in `project_stack`
("Nx monorepo; bug is in `apps/web` — Angular 17"). A plan scoped to the wrong package is
worse than no plan.

**No recognizable manifest at all.** Fall back to file extensions and the directory tree:
count source files by extension, read the entry point, read the largest few files.
Then say explicitly in the plan that the stack was inferred from file extensions alone and
lower `confidence` accordingly — an unverified stack guess is an unverified assumption
sitting underneath every other conclusion.

## Where a bug of this shape usually lives

Once the stack is known, this maps the report to a search starting point. It is a starting
point, not an answer — follow the actual code.

| Symptom | Frontend (Angular/React/Vue) | Backend (Django/Rails/Spring/.NET/Express) |
|---|---|---|
| Control does nothing on click | event binding, handler, unsubscribed observable / unawaited promise | — |
| Wrong value displayed | component state, selector/computed, formatting pipe | serializer / DTO mapping, aggregation query |
| Wrong value stored | form model, request payload construction | validation, service layer, ORM write, transaction boundary |
| Stale data after update | cache layer, store/reducer, missing change detection | cache, read replica, missing invalidation, object identity |
| Layout / visual | component stylesheet, stacking context, container overflow | — |
| 4xx/5xx on a route | HTTP interceptor, request builder | routing, middleware order, auth guard, serializer errors |
| Intermittent / timing | race between async calls, missing `takeUntil` | connection pool, lock ordering, retry logic |

## What Phase 0 must produce

Two lines you carry into every later phase:

1. `project_stack` — the string that goes in the plan's frontmatter, **with its evidence**:
   `"Django 5.2 (requirements.txt, manage.py); tests via ./manage.py test (per .github/copilot-instructions.md)"`.
2. The project's own **test/build/lint commands**, to be reused verbatim in Success criteria.

If you could not determine the stack, say so out loud in the plan rather than proceeding on
a silent assumption. A stated unknown is something a reviewer can fix in ten seconds; a
silent one costs an hour.
