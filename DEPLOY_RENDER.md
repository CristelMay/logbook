# Deploy to Render (CI + Production Guide)

This guide documents the full flow from branch setup to a live Render deployment.

## 1. Create a Dedicated Production Branch

If you do not have a production branch yet, create one:

```bash
git checkout main
git pull origin main
git checkout -b prod
git push -u origin prod
```

If `prod` already exists, just use it as your deployment branch.

## 2. Protect the Production Branch

In GitHub repository settings:

1. Open Branch protection rules.
2. Add a rule for `prod`.
3. Require pull requests before merge.
4. Require status checks to pass before merge.

This prevents direct pushes to production and enforces CI.

## 3. Use Feature Branches for Changes

Do all work in a feature branch and merge to `prod` through PR.

```bash
git checkout prod
git pull origin prod
git checkout -b feature/your-change
```

Push feature branch:

```bash
git push -u origin feature/your-change
```

## 4. Add CI Workflow (GitHub Actions)

Workflow file:

- `.github/workflows/ci.yml`

Trigger configuration:

- Pushes to `prod`
- Pull requests targeting `prod`

Pipeline should include:

- Backend job:
  - PostgreSQL service
  - `pip install -r requirements.txt`
  - `python manage.py migrate --noinput`
  - `python manage.py check`
  - `python manage.py test`
- Frontend job:
  - Node setup
  - `npm ci --prefix theme/static_src`
  - `npm run build --prefix theme/static_src`

## 5. Commit Frontend Lockfile (Best Practice)

Ensure this file is committed:

- `theme/static_src/package-lock.json`

If `.gitignore` blocks lockfiles globally, allow this one explicitly:

```gitignore
!theme/static_src/package-lock.json
```

## 6. Open PR and Merge to Production

1. Open PR from your feature branch to `prod`.
2. Wait for CI checks to pass.
3. Merge PR.

Render should deploy from the latest commit on `prod`.

## 7. Configure Render Service

Set Render to use branch:

- `prod`

Ensure Root Directory is repository root (same folder as `manage.py` and `requirements.txt`).

### Build Command

```bash
pip install -r requirements.txt && npm ci --prefix theme/static_src && python manage.py tailwind build && python manage.py collectstatic --no-input
```

Optional (only if you want deploy-time migrations):

```bash
python manage.py migrate --no-input
```

### Start Command

```bash
gunicorn logbook.wsgi:application --bind 0.0.0.0:$PORT
```

Do not use `gunicorn app:app` for this Django project.

## 8. Set Required Render Environment Variables

Set at least:

- `ENV=production`
- `SECRET_KEY=<strong-random-secret>`
- `ALLOWED_HOSTS=logbook-qj9f.onrender.com`
- `DB_NAME=<value>`
- `DB_USER=<value>`
- `DB_PASSWORD=<value>`
- `DB_HOST=<value>`
- `DB_PORT=<value>`
- `DB_SSLMODE=require` (or your DB requirement)
- `USE_DJANGO_MIGRATIONS=<true_or_false>`
- `SUPABASE_URL=<value>`
- `SUPABASE_KEY=<value>`
- `SUPABASE_BUCKET=<value>`
- `SUPABASE_SIGNED_SECONDS=<value>`

Notes:

- `ALLOWED_HOSTS` must contain hostnames only (no `https://`).
- Keep credentials and keys in Render env vars, not in source control.

## 9. Python and Django Compatibility

Current setup target:

- Python 3.14 on Render
- Django pinned in `requirements.txt`: `Django==5.2.12`

If you hit template/context runtime errors, confirm deployed Python and Django versions from Render logs.

## 10. Deploy and Verify

After merge to `prod`:

1. Confirm Render build succeeds.
2. Confirm Gunicorn starts and binds to `$PORT`.
3. Open the live URL.

Smoke test:

1. Home URL redirects correctly.
2. Login page loads at `/logbook/login/`.
3. Login works.
4. Dashboard loads.
5. Guest registration and checkout flows work.
6. Static CSS and images load correctly.

## 11. Common Errors and Fixes

### A) npm ci fails with missing lockfile

Fix:

- Commit `theme/static_src/package-lock.json`.
- Ensure `.gitignore` allows it.

### B) Start command error: `No module named app`

Fix:

- Use `gunicorn logbook.wsgi:application --bind 0.0.0.0:$PORT`.

### C) Bad Request (400)

Fix:

- Add the Render hostname to `ALLOWED_HOSTS`.

### D) Internal Server Error (500) on login/template rendering

Fix:

- Verify Python/Django compatibility.
- Confirm requirements in `prod` are up to date.
- Redeploy from latest `prod` commit.

## 12. Security Reminders

- Never commit `.env` with real credentials.
- Rotate exposed keys/secrets immediately.
- Keep `DEBUG=False` in production.
- Use a strong `SECRET_KEY`.

---

Owner note:
When deployment fails, copy the first error block from Render logs and troubleshoot from the first failing step: build, collectstatic, start, or first request.
