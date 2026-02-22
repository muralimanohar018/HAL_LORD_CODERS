# CampusShield Frontend

React/Vite frontend wired to CampusShield backend contract:
- `POST /analyze` for plain text
- `POST /ocr/extract` for image/pdf
- `Authorization: Bearer <supabase_access_token>` on every backend call

## Required Environment Variables

Create `.env` in project root:

```bash
VITE_BACKEND_URL=https://your-backend.onrender.com
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Run Locally

```bash
npm install
npm run dev
```

## Backend Integration Notes

- Frontend login/signup uses Supabase Auth (`@supabase/supabase-js`).
- Access token is fetched using `supabase.auth.getSession()` before API calls.
- Text flow sends `{ "text": "..." }` to `/analyze`.
- File flow sends multipart `file` to `/ocr/extract`.
- On `401`, UI redirects user to login.
- On `422`, `502`, `503`, UI shows clear error messages.

## Key Files

- `/Users/muralimanoharmga/Documents/New project/src/lib/supabaseClient.js`
- `/Users/muralimanoharmga/Documents/New project/src/lib/backendApi.js`
- `/Users/muralimanoharmga/Documents/New project/src/pages/AuthPage.jsx`
- `/Users/muralimanoharmga/Documents/New project/src/pages/Dashboard.jsx`
