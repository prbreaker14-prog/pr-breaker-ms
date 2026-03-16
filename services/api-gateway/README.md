## API Gateway

Runs a single public HTTP entrypoint for the frontend and proxies requests to internal microservices based on path prefix:

- `/auth/*` and `/users/*` → identity-service
- `/workouts/*` → workout-service
- `/wgroups/*` → workoutgroups-service
- `/performance/*` → performance-service

Gateway listens on port `5000` by default (override via `PORT`).

