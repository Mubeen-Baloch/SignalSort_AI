# SignalSort AI

SignalSort AI turns noisy WhatsApp/Telegram community exports into a searchable, intent-aware feed. It uses Llama 3 through an OpenAI-compatible inference endpoint when configured and `fastembed` (`all-MiniLM-L6-v2`) for 384-dimensional embeddings.

## Local run

1. Create PostgreSQL with pgvector, then run `psql "$DATABASE_URL" -f db/schema.sql`.
2. `copy backend\\.env.example backend\\.env` and set `DATABASE_URL` and `JWT_SECRET`.
3. `cd backend; python -m venv .venv; .venv\\Scripts\\pip install -r requirements.txt; .venv\\Scripts\\python -m app.seed; .venv\\Scripts\\uvicorn app.main:app --reload --port 8000`
4. `cd frontend; copy .env.local.example .env.local; npm install; npm run dev`

Open http://localhost:3000 and use `demo@signalsort.ai` / `Demo@1234`.

## Deployment

1. Create a Supabase project, enable the `vector` extension, and run `db/schema.sql` in its SQL editor.
2. Push this repository to GitHub. In Render, create a Blueprint from the repository; set `DATABASE_URL` (Supabase pooler URL), a long `JWT_SECRET`, and optionally `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL=llama-3.1-8b-instant`. Render uses `backend/Dockerfile` and runs the seed command on deploy.
3. In Vercel import the same repository, choose `frontend` as Root Directory, and set `NEXT_PUBLIC_API_URL=https://YOUR-RENDER-SERVICE.onrender.com`.
4. Update Render's `ALLOWED_ORIGINS` to the Vercel URL, redeploy Render, then run `python -m app.seed` in the Render shell once if it was not run automatically.

Free Render services sleep after inactivity; the client displays a waking-server status during a slow first call.

## Architecture

FastAPI receives exports/webhooks, records a durable job, and processes it using `BackgroundTasks`. Messages are cleaned/deduplicated, classified, embedded, then matched against active intent vectors with pgvector cosine distance. Matches create in-app notifications. The queue boundary is isolated in `services/pipeline.py`, so it can later be replaced with a worker.

No OpenAI models or AWS services are used.
