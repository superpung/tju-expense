# TJU-Expense Desktop

A desktop app for browsing your TJU campus-card income/expense flow and yearly
statistics. Log in with your campus-card username and password; the app fetches
your records directly, caches them locally, and lets you export CSV. The UI
follows Vercel's [Geist](https://vercel.com/geist) design system.

```
web/
├── backend/    FastAPI — login, scraping, local cache, and serves the frontend
├── frontend/   Vite + React + TypeScript, Geist design tokens
└── desktop/    pywebview launcher + PyInstaller spec
```

## Why a desktop app (and not a website)

The campus-card site sends no CORS headers and lives on the campus intranet, so
a browser page **cannot** call it directly. The requests must run outside the
browser sandbox — in native code. This app runs a small FastAPI server on
`127.0.0.1` (in-process, Python does the campus requests) and shows it in a
native window. There is no server to host and no CORS: everything runs on your
own machine, on the campus network.

Data is cached to `~/.tju-expense/data/<stuid>/<year>.csv`, so it opens
instantly next time and the CSV is a plain file you can find and export.

## Run from source

```sh
# 1. build the frontend (once, or after frontend changes)
cd web/frontend
npm install
npm run build

# 2. install backend + desktop deps
cd ../desktop
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ../..            # the tju_expense package (scraping logic)

# 3. launch the app
python main.py
```

The machine must be on the campus network (the app reaches
`59.67.37.10:8180`). On Linux, pywebview needs a system webview
(e.g. `python3-gi gir1.2-webkit2-4.1` for the GTK backend).

## Build a binary

Matches the project's existing PyInstaller distribution:

```sh
cd web/frontend && npm run build          # produce dist/
cd ../desktop && pyinstaller tju-expense-desktop.spec
# -> dist/tju-expense  (double-click, no Python needed)
```

## Frontend dev

For iterating on the UI in the browser (with hot reload), run the backend and
the Vite dev server separately:

```sh
cd web/desktop  && python -m uvicorn app.main:app --port 8000   # backend
cd web/frontend && npm run dev                                   # http://localhost:5173
```

The dev server proxies `/api` to `:8000`. CSV export uses a browser download
here; in the packaged app it uses a native Save dialog via the pywebview bridge.

## Design system

Colors are the official Geist scales (`frontend/src/styles/geist-tokens.css`,
light + dark), consumed through semantic aliases in `globals.css`. Type is Geist
Sans / Mono via `@fontsource-variable`. The theme toggle cycles light / dark /
system and the charts recolor to match.
