# Smart Resume Analyzer AI

A Flask backend and Tailwind frontend project for resume-job matching, skill-gap analysis, and course/project recommendations.

## Local setup

1. Install Python dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. Start the backend:
   ```powershell
   python backend/app.py
   ```
3. Open `frontend/index.html` in your browser or host it with any static server.

## Deploying to Vercel

This repository is now configured to run entirely on Vercel:
- Static frontend served from `frontend/`
- Python API routes served from `/api`
- Root paths rewritten to the frontend and backend endpoints mapped correctly

### Deploy on Vercel

1. Push the repository to GitHub.
2. Create a new Vercel project and connect the GitHub repo.
3. Make sure Vercel uses the root `vercel.json` configuration.
4. Confirm `requirements.txt` is present in the project root.
5. Deploy.

### Notes

- Frontend requests to `/analyze-text`, `/upload-file`, and `/health` will route to Vercel Python functions.
- File upload is supported through the existing form upload flow.

## Deploying the backend elsewhere

The frontend is configured to use local backend at `localhost:5000` only during development. In production, it sends requests to the same host as the site.

If your backend is deployed to a separate host, update `API_BASE_URL` in `frontend/index.html` to the full backend URL.
