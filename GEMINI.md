# Gemini Instructions — BiasAperture

Please strictly follow the universal project context defined in:
@AGENTS.md

## Gemini-Specific Rules & Directives
- **CRITICAL**: You must read and strictly adhere to the universal core guidelines located in `./AGENTS.md` before processing any tasks.
- All architecture specifications, locked M1 schema taxonomies, NumPy docstring standards, and testing workflows defined in `@AGENTS.md` are authoritative.
- **Testing & Verification**: Always run the complete test suite via `uv run --extra dev pytest` and linting via `uv run --extra dev ruff check src/`.
- **Git & Sync Operations**: Raw `git commit` and `git push` are strictly forbidden. All version control operations must execute through `.\sync.bat` (or `.\sync.ps1 -m "type(scope): summary (#issue)"`).
