# TJU-Expense Web

A web version of TJU-Expense: log in with your campus-card username and password
and browse your card income/expense flow and yearly statistics in the browser.
The UI follows Vercel's [Geist](https://vercel.com/geist) design system.

```
web/
├── backend/    FastAPI — proxies the campus-card login and scraping
└── frontend/   Vite + React + TypeScript, Geist design tokens
```

## How it works

Browsers cannot reach the campus intranet or hold the login session, so a thin
backend proxies the flow:

1. `POST /api/login` submits the campus-card Spring Security form with the
   student id, password and the page's CSRF token (no captcha is required), and
   keeps the authenticated session in memory — nothing is written to disk.
2. `GET /api/records` and `/api/user` return data, reusing the proven scraping
   from the root `tju_expense` package: the authenticated JSESSIONID is handed
   to the existing `Fetcher`.

Card income/expense records only; dormitory electricity is out of scope (handled
by the separate `tju-ecard` project).

## Backend (FastAPI)

```sh
cd web/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ../..            # the tju_expense package (scraping logic)
uvicorn app.main:app --reload   # http://localhost:8000
```

The backend must run somewhere that can reach the campus-card host
(`59.67.37.10:8180`) — i.e. on the campus network.

## Frontend (Vite + React)

```sh
cd web/frontend
npm install
npm run dev        # http://localhost:5173, proxies /api to :8000
npm run build      # production build in dist/
```

## Design system

Colors are the official Geist scales (`src/styles/geist-tokens.css`, light +
dark), consumed through semantic aliases in `src/styles/globals.css`. Type is
Geist Sans / Geist Mono via `@fontsource-variable`. The theme toggle cycles
light / dark / system and charts recolor to match.
