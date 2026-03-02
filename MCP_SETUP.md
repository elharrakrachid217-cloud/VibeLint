# Adding VibeGuard MCP in Cursor (Windows)

If Cursor doesn’t pick up the MCP automatically, use one of these methods.

---

## Method 1: Use project config (recommended)

1. **Open the correct folder in Cursor**
   - File → Open Folder
   - Choose: `vibeguard_starter` (the parent folder that contains the `vibeguard` subfolder)
   - Cursor looks for `.cursor/mcp.json` in the folder you open; the config is now at `vibeguard_starter/.cursor/mcp.json`.

2. **Reload so Cursor sees the config**
   - `Ctrl+Shift+P` → run **“Developer: Reload Window”**
   - Or close Cursor and open the `vibeguard_starter` folder again.

3. **Check MCP**
   - `Ctrl+Shift+P` → **“Cursor: Open MCP Servers”** (or go to **Settings → Cursor Settings → Features → MCP**)
   - You should see **vibeguard** in the list. If it’s disabled or has an error, turn it on / fix the error.

4. **Ensure the server can run**
   - In a terminal, from the `vibeguard` folder, run: `python server.py`
   - It should start without errors (you can stop it with Ctrl+C). Cursor will start it automatically when using the MCP.

---

## Method 2: Add via Cursor Settings UI

1. **Open Cursor Settings**
   - `Ctrl+,` (comma) or **File → Preferences → Cursor Settings**.

2. **Open MCP**
   - Go to **Features** (or **Tools & MCP**) → **MCP**.

3. **Add a new server**
   - Click **“+ Add new MCP server”** (or **“Add Server”**).

4. **Enter VibeGuard details**
   - **Name:** `vibeguard`
   - **Type:** **Command** (run a local process).
   - **Command:** `python`
   - **Arguments:** `server.py` (as a single argument).
   - **Working directory (cwd):**  
     `C:\Users\hp\Favorites\Downloads\vibeguard project\vibeguard_starter\vibeguard`  
     (If the UI has a “cwd” or “Working directory” field, paste this path.)

5. **Save** and **restart Cursor** (fully quit and reopen).

---

## Method 3: Global MCP config (all projects)

Cursor can also read a global MCP config. On Windows it’s often:

- `%APPDATA%\Cursor\mcp.json`, or  
- `C:\Users\hp\.cursor\mcp.json`

1. Create or open that file (e.g. `C:\Users\hp\AppData\Roaming\Cursor\mcp.json`).
2. Paste the same JSON as in `vibeguard_starter/.cursor/mcp.json` (the `mcpServers.vibeguard` block with `command`, `args`, `cwd`).
3. Save, then fully restart Cursor.

---

## If it still doesn’t work

- **Python on PATH**  
  In a **new** terminal run: `python --version`  
  If that fails, add your Python install to PATH or use the full path to `python.exe` in the MCP **Command** (e.g. `C:\Users\hp\AppData\Local\Python\pythoncore-3.14-64\python.exe`).

- **Path with spaces**  
  Your path has a space (`vibeguard project`). The JSON `cwd` we use is correct. If you moved the project, update `cwd` in `.cursor/mcp.json` (and in the Settings UI if you used Method 2) to the new path.

- **Check MCP logs**  
  In Cursor: **Help → Toggle Developer Tools → Console**, or check logs under  
  `%APPDATA%\Cursor\logs\` for MCP-related errors.
