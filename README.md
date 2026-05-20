## Fitness Microservices Backend.....

This repository contains a Python microservices backend for a fitness application, with two Flask-based microservices:

- **Identity Service**: authentication, JWT issuance, and user profile management.
- **Workout Service**: CRUD for workout (exercise definition) entities.

The architecture is designed to run in **local development**, **Docker Compose**, and **Kubernetes** environments with **environment-agnostic service discovery** and **shared JWT authentication**.

---

### Project Structure

```text
fitness-microservices/
  services/
    identity-service/
      app/
        routes/
        controllers/
        models/
        services/
        utils/
        app.py
      config.py
      requirements.txt
      Dockerfile
    workout-service/
      app/
        routes/
        controllers/
        models/
        services/
        utils/
        app.py
      config.py
      requirements.txt
      Dockerfile
  shared/
    auth/
      jwt_utils.py
      auth_middleware.py
    utils/
      response.py
  docker-compose.yml
  README.md
```

---

### Technology Stack

- Python 3.11
- Flask, Flask-SQLAlchemy, Flask-Migrate
- SQLAlchemy
- PyJWT
- bcrypt (identity-service only)
- requests
- PostgreSQL

Each service is independently runnable.

---

### Databases

- **Identity Service**
  - DB name: `identity_db`
  - Tables:
    - `users` (UUID primary key, email, username, password_hash, created_at, updated_at)
    - `user_profile` (user_id PK/FK within the same DB, age, gender, height, weight, created_at, updated_at)
  - Passwords are stored using **bcrypt**.

- **Workout Service**
  - DB name: `workout_db`
  - Table:
    - `workouts` (UUID primary key, name, type, has_sets, has_reps, has_weight, has_duration, has_calories, notes, created_at, updated_at)
  - Represents **exercise definitions**, not logs.

Each microservice owns its own database; there are **no cross-service foreign keys**.

---

### Authentication Flow

- Identity service issues JWT access tokens.
- Endpoints:
  - `POST /auth/register`
  - `POST /auth/login`
  - `GET /users/me`
- Login response includes:
  - `access_token`
  - `token_type` (`bearer`)
  - `user` payload
- JWT payload contains:
  - `user_id`
  - `email`
  - `exp` (10 hour expiry)

JWT signing secret is provided via the shared environment variable:

- **`JWT_SECRET`**

---

### Service Communication & Discovery

Services use environment variables for service URLs (no hardcoded `localhost`):

- `IDENTITY_SERVICE_URL`
- `WORKOUT_SERVICE_URL`

Examples:

- **Local development**:
  - `IDENTITY_SERVICE_URL=http://localhost:5001`
  - `WORKOUT_SERVICE_URL=http://localhost:5002`
- **Docker Compose**:
  - `IDENTITY_SERVICE_URL=http://identity-service:5000`
  - `WORKOUT_SERVICE_URL=http://workout-service:5000`
- **Kubernetes** (example services named `identity-service` and `workout-service`):
  - `IDENTITY_SERVICE_URL=http://identity-service`
  - `WORKOUT_SERVICE_URL=http://workout-service`

Use `os.getenv()` in code to read these variables; no URLs are hardcoded.

---

### Standardized API Responses

All APIs return a standardized JSON envelope:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {}
}
```

Helpers are implemented in `shared/utils/response.py`:

- `success_response(message, data, status_code=200)`
- `error_response(message, status_code=400, data=None)`

---

### Local Development

#### Prerequisites

- Python 3.11
- PostgreSQL (or update DB URLs to point to your instance)

#### Shared Environment

At the repo root (`fitness-microservices`), set key environment variables (PowerShell example):

```powershell
$env:JWT_SECRET = "super-secret-change-me"
$env:IDENTITY_SERVICE_URL = "http://localhost:5001"
$env:WORKOUT_SERVICE_URL = "http://localhost:5002"
```

#### Identity Service (port 5001)

```bash
cd services/identity-service
pip install -r requirements.txt
python app/app.py
```

By default it uses:

- `IDENTITY_DATABASE_URL` or fallback `postgresql+psycopg2://identity_user:identity_password@localhost:5432/identity_db`
- Port: `5001` (override with `PORT` env)

#### Workout Service (port 5002)

```bash
cd services/workout-service
pip install -r requirements.txt
python app/app.py
```

By default it uses:

- `WORKOUT_DATABASE_URL` or fallback `postgresql+psycopg2://workout_user:workout_password@localhost:5432/workout_db`
- Port: `5002` (override with `PORT` env)

---

### Docker Compose

#### Build and Run

From the `fitness-microservices` root:

```bash
docker-compose up --build
```

Services exposed on the host:

- Identity service: `http://localhost:5001`
- Workout service: `http://localhost:5002`
- Identity Postgres: `localhost:5433`
- Workout Postgres: `localhost:5434`

Container-internal service discovery:

- Identity: `http://identity-service:5000`
- Workout: `http://workout-service:5000`

JWT secret, DB URLs and service URLs are provided via environment variables in `docker-compose.yml`.

---

### Kubernetes (High-Level)

You can reuse the same Docker images in Kubernetes:

1. Build and push images for `identity-service` and `workout-service`.
2. Create `Deployment` and `Service` resources named:
   - `identity-service`
   - `workout-service`
3. Configure environment variables on Pods:
   - `JWT_SECRET`
   - `IDENTITY_SERVICE_URL=http://identity-service`
   - `WORKOUT_SERVICE_URL=http://workout-service`
   - `IDENTITY_DATABASE_URL` / `WORKOUT_DATABASE_URL` pointing to appropriate Postgres services.

The services will continue to use the same environment-based configuration without any code changes.

---

### Key Endpoints

- **Identity Service**
  - `POST /auth/register`
  - `POST /auth/login`
  - `GET /users/me`

- **Workout Service**
  - `GET /workouts`
  - `POST /workouts`
  - `GET /workouts/<id>`
  - `PUT /workouts/<id>`
  - `PATCH /workouts/<id>`
  - `DELETE /workouts/<id>`

All workout endpoints require:

```http
Authorization: Bearer <token>
```

where `<token>` is the JWT issued by the identity-service.

