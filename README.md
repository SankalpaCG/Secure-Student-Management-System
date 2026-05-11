# Secure Student Management System (SSMS)

A full-stack student management platform with JWT authentication, role-based access control (Admin, Teacher, Student), optional TOTP two-factor authentication, and security-focused middleware. The stack uses **React + Vite** on the frontend and **Node.js + Express + Sequelize + MySQL** on the backend, packaged as a **npm workspaces monorepo**.

## Repository layout

```
secure-student-management-system/
├── backend/                 # Express API, Sequelize, JWT, RBAC, 2FA
├── frontend/                # React (Vite), Tailwind, dashboard UI
├── docs/                    # Architecture and setup notes
├── .github/workflows/       # CI/CD and security pipelines
├── docker-compose.yml       # MySQL 8 for local development
├── package.json             # Workspace root scripts
└── README.md
```

## Prerequisites

- **Node.js** 20 or newer
- **npm** 10+
- **Docker** and **Docker Compose** (recommended for MySQL), or a local **MySQL 8** instance compatible with MySQL Workbench

## Quick start

### 1. Start MySQL

From the repository root:

```bash
docker compose up -d
```

This starts MySQL on port **3306** with database `ssms` (defaults in `docker-compose.yml`). Adjust credentials via a root `.env` if needed (see [Environment variables](#environment-variables)).

### 2. Backend

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set DATABASE_URL or discrete DB_* vars and JWT_SECRET
npm install
cd backend && npm run db:migrate && npm run db:seed && cd ..
```

Run the API:

```bash
npm run dev -w backend
```

API base URL defaults to `http://localhost:4000`.

### 3. Frontend

```bash
cp frontend/.env.example frontend/.env
npm run dev -w frontend
```

Open `http://localhost:5173`. Demo logins after seeding:

| Role    | Email              | Password   |
|---------|--------------------|------------|
| Admin   | admin@ssms.local   | ChangeMe!1 |
| Teacher | teacher@ssms.local | ChangeMe!1 |
| Student | student@ssms.local | ChangeMe!1 |

Change passwords immediately in any shared or production environment.

### 4. Run both (monorepo)

```bash
npm install
npm run dev
```

## Environment variables

See `backend/.env.example` and `frontend/.env.example`. Never commit real secrets.

- **Backend**: database connection, `JWT_SECRET`, `CSRF_SECRET`, optional `FRONTEND_ORIGIN` for CORS, `BCRYPT_ROUNDS`, rate limit tuning.
- **Frontend**: `VITE_API_URL` pointing at the Express API.

## Security features (backend)

- **Helmet** for HTTP security headers
- **CORS** with configurable origin and credentials
- **Rate limiting** on auth and global tiers
- **Double-submit CSRF** for cookie-based flows and aligned SPA header checks on mutating routes
- **Input validation** (`express-validator`) and **sanitization** (`sanitize-html`, `validator`)
- **JWT** access tokens and **RBAC** middleware
- **TOTP 2FA** (speakeasy) with QR setup for enrolled users

## Testing and quality

```bash
npm test                 # backend Jest + frontend Vitest
npm run lint             # ESLint (backend + frontend)
npm audit --workspaces   # include devDependencies; CI uses production-only audit
```

CI runs `npm audit --workspaces --omit=dev --audit-level=high` to focus on production dependency paths.

## CI/CD and DevSecOps

GitHub Actions workflows under `.github/workflows/` include:

- **CI**: install, lint, test, `npm audit`
- **SonarCloud**: static analysis (requires `SONAR_TOKEN` and SonarCloud project configuration)
- **Trivy**: filesystem vulnerability scan
- **OWASP ZAP**: baseline DAST (expects a reachable target URL via `ZAP_TARGET` secret for scheduled/manual runs)

See `docs/DEVSECOPS.md` for secret names and tuning.

## MySQL Workbench

Connect to `localhost:3306` with the user/password from `docker-compose.yml` (or your overrides). The default database name is `ssms`.

## License

MIT (adjust as needed for your organization).
