# VibeLint — 2‑minute setup

You don’t need to know Python or MCP. Follow these steps in order; each one is a single copy‑paste.

---

## What you need

- **Python 3.8 or newer** (we’ll check in Step 0).
- **This project** on your machine (e.g. you cloned or downloaded `vibelint_starter`).

---

## Step 0 — Check Python (30 seconds)

Open a **terminal**:

- **Windows:** Press `Win + R`, type `cmd`, press Enter. Or in File Explorer, type `cmd` in the address bar and press Enter.
- **Mac:** Press `Cmd + Space`, type `Terminal`, press Enter.
- **Linux:** `Ctrl+Alt+T` or open “Terminal” from your app menu.

In the terminal, run **one** of these (try the first; if it says “not found”, try the second):

```bash
python --version
```

```bash
python3 --version
```

You should see something like `Python 3.10.0` or `Python 3.12.1`.  
If you get “not found” or “not recognized”, install Python from [python.org/downloads](https://www.python.org/downloads/) and run this step again.

---

## Step 1 — Go to the VibeLint folder (10 seconds)

In the **same terminal**, go to this project folder, then into the `vibelint` folder.

**Windows (Command Prompt or PowerShell):**

```bash
cd path\to\vibelint_starter
cd vibelint
```

**Mac / Linux:**

```bash
cd /path/to/vibelint_starter
cd vibelint
```

Replace `path\to\vibelint_starter` (or `/path/to/vibelint_starter`) with the real path where the project lives.  
Example on Windows: `cd C:\Users\Ahmed\Downloads\vibelint_starter` then `cd vibelint`.  
Example on Mac: `cd ~/Projects/vibelint_starter` then `cd vibelint`.

---

## Step 2 — Install dependencies (about 30 seconds)

Still in the `vibelint` folder, run:

```bash
pip install -r requirements.txt
```

If you get “pip not found”, use this instead (use the same word you used in Step 0: `python` or `python3`):

```bash
python -m pip install -r requirements.txt
```

```bash
python3 -m pip install -r requirements.txt
```

You should see "Successfully installed" near the end of the output. Wait until it finishes without errors.

---

## Step 3 — Register VibeLint in your IDE (10 seconds)

In the **same terminal**, still in the `vibelint` folder, run:

**If you use Cursor:**

```bash
python install_mcp.py --ide cursor
```

**If you use Windsurf:**

```bash
python install_mcp.py --ide windsurf
```

**If you use Claude Desktop:**

```bash
python install_mcp.py --ide claude
```

**If you’re not sure:** run without `--ide` and the script will try to detect your IDE:

```bash
python install_mcp.py
```

Use `python3` instead of `python` if that’s what worked in Step 0.  
You should see “Done! Restart your IDE to activate VibeLint.”

---

## Step 4 — Restart your IDE (10 seconds)

- **Cursor:** Restart Cursor, or go to **Settings → MCP** and click the restart button next to **vibelint**.
- **Windsurf / Claude Desktop:** Fully quit the app and open it again.

---

## Verify it works — recommended

In the terminal, in the `vibelint` folder, run:

```bash
python server.py
```

You should see a line like: **VibeLint — AI Code Security Scanner** (it may take a second to appear).  
Press `Ctrl+C` to stop the server. Your IDE will start it automatically when needed.

---

## If something goes wrong

| Problem | What to do |
|--------|------------|
| **“Python not found” / “python is not recognized”** | Install Python from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick “Add Python to PATH” in the installer. |
| **“pip not found”** | Use `python -m pip install -r requirements.txt` (or `python3 -m pip ...`) in Step 2. |
| **“No supported IDE config found”** | Use Step 3 with `--ide cursor`, `--ide windsurf`, or `--ide claude`. Make sure that IDE has been opened at least once so its config folder exists. |
| **“'mcp' package not installed”** | You’re not in the `vibelint` folder, or Step 2 didn’t finish. Run `cd vibelint` and `pip install -r requirements.txt` again. |
| **VibeLint doesn’t appear in my IDE** | Restart the IDE (Step 4). In Cursor, check **Settings → MCP** and restart the **vibelint** server. |

---

You’re done. VibeLint will now scan AI‑generated code before it’s written to your project.
