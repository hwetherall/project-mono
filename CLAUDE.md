# Innovera Research — Claude Module Index

This workspace uses modular Claude briefs to avoid overloading the model context.

## How To Use These Files

Load only the module you need for the current task. Do not paste all modules into a single Claude Code run unless the model can comfortably handle the combined size.

Recommended sequence:

1. `claude-1.md`
   Runtime hotfixes: Tavily payload compatibility, `.env`/Tavily-key assumptions, and terminal output mirroring into the Activity Stream.

2. `claude-2.md`
   Checkpoint-and-resume design: durable category checkpoints, `Continue` button semantics, resume endpoint, and timeout recovery.

3. `claude-3.md`
   Broader v2 product work: report overhaul, history, search, sources, dark mode, PDF export, verdict dashboard, build order, and implementation notes.

## Guidance

- If the task is a blocking runtime fix, start with `claude-1.md`.
- If the task is timeout recovery or resumability, run `claude-2.md` after `claude-1.md` if needed.
- If the task is the broader product/UI build, use `claude-3.md`.
- Keep the implementation modular. Avoid cross-cutting rewrites unless the module explicitly requires them.
- Do not edit Python `site-packages`.
- Assume a real local `.env` exists and contains the necessary secrets unless runtime evidence proves otherwise.

## Success Condition For This Index

The main `CLAUDE.md` should stay lightweight, while the numbered Claude briefs can be executed one after another without exceeding the practical context budget.
