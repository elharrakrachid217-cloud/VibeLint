# Running a security audit with VibeLint

You can test this project’s security with VibeLint in two ways: **CLI (recommended)** or **MCP (file-by-file in Cursor)**.

---

## Option 1 — CLI project scan (recommended)

Run the scanner over the whole repo from the command line. No MCP needed.

**From the project root** (`vibelint_starter`):

```bash
python vibelint/scan_project.py
```

To scan a specific folder:

```bash
python vibelint/scan_project.py landing
python vibelint/scan_project.py supabase
```

**What it does:**

- Finds all `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.html`, `.sql` files
- Skips `tests`, `__pycache__`, `.git`, `node_modules`, `venv`
- Runs VibeLint’s detectors (secrets, auth, injection, Semgrep) on each file
- Prints a summary and any violations

Use this to get a single, repeatable security report for the repo.

---

## Option 2 — MCP file-by-file in Cursor

Use VibeLint as an MCP server so the AI can call `security_check` on code before writing. For an **audit**, the AI can read each relevant file and call the tool with its contents (one file per call).

**Step 1 — Install VibeLint MCP for this project**

1. Open a terminal and go to this project’s `vibelint` folder:
   ```bash
   cd path\to\vibelint_starter\vibelint
   ```
2. Install and register MCP:
   ```bash
   pip install -r requirements.txt
   python install_mcp.py
   ```
3. Restart Cursor (or **Settings → MCP** and restart the **vibelint** server).

**Step 2 — Run a security audit via the AI**

In Cursor, ask the AI something like:

- *“Run a VibeLint security audit on this project: for each of these files — `landing/index.html`, `vibelint/server.py`, `vibelint/install_mcp.py`, `vibelint/install_service.py`, `vibelint/uninstall_service.py` — read the file and call the VibeLint `security_check` tool with the full file contents and the right language. Summarize any violations.”*

The AI will then:

1. Read each file
2. Call the `security_check` tool with that file’s content and language
3. Report pass/fail and any findings

So yes: with MCP, the audit is done **file by file** by the AI invoking the tool once per file.

---

## What to scan

| Area              | Files / folders to include        |
|-------------------|-----------------------------------|
| Landing / frontend| `landing/index.html`              |
| Supabase          | `supabase/migrations/*.sql`       |
| VibeLint / server | `vibelint/server.py`, `vibelint/install_mcp.py`, `vibelint/install_service.py`, `vibelint/uninstall_service.py` |

The CLI script already includes these (and skips tests and cache dirs). For MCP, you can name the same files in your prompt.

---

## Summary

| Goal                         | Use this                          |
|-----------------------------|------------------------------------|
| One-shot audit of the repo  | `python vibelint/scan_project.py` |
| Audit a specific folder     | `python vibelint/scan_project.py <folder>` |
| Audit via Cursor with MCP   | Install MCP, then ask the AI to run `security_check` on each file (file-by-file). |

You do **not** have to choose one forever: use the CLI for quick audits and CI, and MCP when you want the AI to gate every edit with `security_check`.
