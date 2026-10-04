# Technical Preferences

<!-- project.yaml at the repo root is the machine-readable source of truth for
     engine, specialists, naming, performance, platform, and testing.framework.
     This file is the human-readable LEGACY FALLBACK: agents and skills resolve
     each key from project.yaml first and fall back here only when the
     project.yaml key is absent. /setup-engine dual-writes both.
     Forbidden patterns and allowed libraries are NOT migrated — they live only
     in this file. Populated by /setup-engine; updated as decisions are made. -->

## Engine & Language

- **Engine**: Web (no engine) — Node.js 20+ server + browser client
- **Language**: JavaScript (CommonJS server, plain ES modules in the browser, no build step)
- **Rendering**: Browser DOM + inline SVG + Canvas (confetti)
- **Physics**: None

## Input & Platform

<!-- Written by /setup-engine. Read by /ux-design, /ux-review, /test-setup, /team-ui, and /dev-story -->
<!-- to scope interaction specs, test helpers, and implementation to the correct input methods. -->

- **Target Platforms**: Web (phones and laptops, any modern browser)
- **Input Methods**: Touch, Mouse/Keyboard
- **Primary Input**: Touch (phones are the controllers)
- **Gamepad Support**: None
- **Touch Support**: Full
- **Platform Notes**: Mobile-first 360–1280 px, no horizontal scroll, buttons ≥ 44 px, no hover-only interactions

## Naming Conventions

- **Classes**: PascalCase (`Room`, `Rooms`)
- **Variables**: camelCase
- **Signals/Events**: camelCase Socket.IO event names (`join`, `act`, `view`, `fx`)
- **Files**: kebab-case (`secret-hitler.js`)
- **Scenes/Prefabs**: kebab-case client screen modules under `public/js/`
- **Constants**: SCREAMING_SNAKE (`MAX_PLAYERS`)

## Performance Budgets

- **Target Framerate**: [TO BE CONFIGURED]
- **Frame Budget**: [TO BE CONFIGURED]
- **Draw Calls**: [TO BE CONFIGURED]
- **Memory Ceiling**: [TO BE CONFIGURED]

## Testing

- **Framework**: node:test + node:assert/strict (`npm test`); Playwright screenshots for UI checks
- **Minimum Coverage**: [TO BE CONFIGURED]
- **Required Tests**: Balance formulas, gameplay systems, networking (if applicable)

## Forbidden Patterns

<!-- Add patterns that should never appear in this project's codebase -->
- [None configured yet — add as architectural decisions are made]

## Allowed Libraries / Addons

<!-- Add approved third-party dependencies here -->
- express, socket.io, socket.io-client (dev), qrcode-terminal, cloudflared, @dicebear/core + @dicebear/collection (lorelei/notionists, CC0 art), @fontsource/fredoka (OFL)

## Architecture Decisions Log

<!-- Quick reference linking to full ADRs in docs/architecture/ -->
- [No ADRs yet — use /architecture-decision to create one]

## Engine Specialists

<!-- Written by /setup-engine when engine is configured. -->
<!-- Read by /code-review, /architecture-decision, /architecture-review, and team skills -->
<!-- to know which specialist to spawn for engine-specific validation. -->

- **Primary**: gameplay-programmer (no engine specialist applies)
- **Language/Code Specialist**: gameplay-programmer
- **Shader Specialist**: technical-artist (SVG/CSS/Canvas effects)
- **UI Specialist**: ui-programmer
- **Additional Specialists**: network-programmer (Socket.IO, tunnel), security-engineer (public rooms, input validation)
- **Routing Notes**: Web project — Godot/Unity/Unreal specialists do not apply.

### File Extension Routing

<!-- Skills use this table to select the right specialist per file type. -->
<!-- If a row says [TO BE CONFIGURED], fall back to Primary for that file type. -->

| File Extension / Type | Specialist to Spawn |
|-----------------------|---------------------|
| Game code (primary language) | gameplay-programmer |
| Shader / material files | technical-artist |
| UI / screen files | ui-programmer |
| Scene / prefab / level files | ui-programmer |
| Native extension / plugin files | [TO BE CONFIGURED] |
| General architecture review | Primary |
