# Project Guidelines

## Code Style
- Keep changes small and consistent with the surrounding service.
- Prefer the existing Django and FastAPI patterns already used in each service instead of introducing new abstractions.
- Link to the main docs instead of repeating architecture or API details in comments.

## Architecture
- This is a monorepo of microservices with an API gateway as the public entry point.
- Treat service boundaries as strict: avoid cross-service SQL joins or shared ORM access; use HTTP between services.
- The gateway owns public routing and page rendering. If you add or rename a routed service, update the gateway mapping as well.
- The bookstore core is documented in [README.md](../README.md), [API_Documentation.md](../API_Documentation.md), and [Technical_Report.md](../Technical_Report.md).

## Build and Test
- Use Docker Compose as the default way to run the system: `docker-compose up --build -d` and `docker-compose down`.
- For local service work, use the service's own `requirements.txt` and `manage.py` entry points.
- Run Django migrations when schema changes are involved; the compose setup does not reliably auto-run them.
- Use the service-specific test command when available; there is no single repo-wide test runner documented.

## Conventions
- The gateway is the canonical external entry point; do not assume direct browser access to internal services.
- Container-internal database hosts use Docker service names such as `postgres-db`, not `localhost`.
- Ports are service-specific and are not interchangeable; the gateway is on 8000, while internal services use their mapped ports.
- The `ai-behavior-service` is FastAPI-based and follows a different startup path from the Django services.
- Docker and database initialization details live in [docker-compose.yml](../docker-compose.yml) and [postgres-init/init.sql](../postgres-init/init.sql).
