# Codebase Mapping — Flows
> Last mapped: 2026-06-15

## Key Logic Flows

### 1. Assessment Flow
```
[Select Framework] ──> [POST /start] ──> [Load Questions]
                                             │
[Results radar] <── [Calculate Scores] <── [POST /submit]
```

### 2. Multi-Agent PMO Chat Flow
```
[User Message] ──> [Orchestrator Classifier]
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  [Risk Agent]     [Resource Agent]  [Timeline Agent]
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                [Markdown / Stream]
```
