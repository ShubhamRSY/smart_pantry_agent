# Copilot / AI Agent Instructions for Smart Pantry Agent

This file gives focused, actionable guidance for AI coding agents working on this repository.

1) Big picture
- Single-process Streamlit app: the UI surface is `main.py` which wires together four main features: auth, receipt scanner, pantry inventory UI, and chef recipe suggestions.
- Data storage: per-user SQLite DBs in `user_data/<username>.db` (created by `database.operations.init_pantry_db`). Global auth table lives in `users.db` managed by `database/operations.py`.
- Core components:
  - `main.py` — Streamlit UI and session flow (`st.session_state['user']`).
  - `logic/scanner.py` — saves uploads to `receipts/<username>/` and calls OpenAI for receipt parsing; prompt embeds base64 image and expects JSON list of items with `clean_name`, `category`, `quantity`, `unit`.
  - `logic/chef.py` — reads inventory and calls OpenAI to return a JSON object `{ "recipes": [...] }` with `used_ingredients` for each recipe.
  - `database/operations.py` — all DB interactions, inventory thresholds, decimal quantities, and the deduction rules used when a recipe is cooked.

2) Important workflows & run commands
- Run locally using the project's Streamlit app (activate your venv first):

```bash
source .venv/bin/activate
streamlit run main.py
```

- Environment: `OPENAI_API_KEY` must be set (project uses `python-dotenv` via `load_dotenv()` in modules). Do not commit keys.

3) Project-specific patterns and constraints (do not change without regression checks)
- Inventory quantities are floats (`REAL`) and the code uses small thresholds: items with `quantity > 0.05` are considered present; `<= 0.05` appear on the grocery list. See `get_current_inventory` and `get_grocery_list` in `database/operations.py`.
- `deduct_ingredients()` contains the domain rules (usage factor = `0.125 * people_count`) and category-driven deduction heuristics. If you change recipe-to-deduction mapping, update both `chef.py` prompt expectations and UI messages.
- `logic/scanner.py` enforces strict categories inside the LLM prompt — keep category names consistent (`Dairy`, `Produce`, `Snacks`, `Meat`, `Pantry`, `Frozen`, `Household`). Downstream code expects these strings for grouping and action buttons in `main.py`.
- OpenAI usage: code uses `openai.OpenAI` client and `chat.completions.create` with `response_format={"type":"json_object"}`. Agent changes that contract only if updating both caller and downstream parsing.

4) Files to inspect when making changes
- UI flows and session state: `main.py`.
- Receipt ingestion and prompt rules: `logic/scanner.py`.
- Recipe generation and expected JSON shape: `logic/chef.py` (returns `recipes` with `used_ingredients`).
- DB schema and business rules: `database/operations.py`.
- Dependencies: `requirements.txt`.

5) Testing and debugging tips
- To verify receipt parsing, upload a sample image in the Streamlit UI and inspect `receipts/<username>/` for saved file and returned parsed JSON.
- Check per-user DB files in `user_data/` and the global `users.db` when debugging auth or inventory issues.
- Watch Streamlit logs in the terminal for printed exceptions (scanner and chef modules print errors). Use `print()` statements or raise informative exceptions when adding features.

6) Security & ops
- Keep `OPENAI_API_KEY` and other secrets in `.env`; never hardcode keys.
- Be mindful of image sizes when encoding base64 in `scanner.py` (performance/cost when calling OpenAI). Consider caching or resizing images before encode.

7) Examples (expected shapes)
- Receipt parse item: `{"clean_name": "Basmati Rice", "category": "Pantry", "quantity": 1, "unit": "bag"}`
- Recipe response: `{ "recipes": [{ "name": "Fried Rice", "time_minutes": 20, "description": "...", "used_ingredients": ["Rice","Egg"], "steps": ["..."] }] }
 
If anything here looks wrong or incomplete for your task, tell me which area you want expanded (prompts, DB rules, runtime commands, or an example change), and I'll iterate.
