PROJECT_NAME ?= snippetly
COMPOSE := docker compose
COMPOSE_DEV := $(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml

.PHONY: help up up-dev down down-dev logs ps psql prune

help:
	@echo "Available targets:"
	@echo "  up         - Start core services (db, redis) in background"
	@echo "  up-dev     - Start dev stack (db, redis, pgadmin) in background"
	@echo "  down       - Stop stack"
	@echo "  down-dev   - Stop dev stack"
	@echo "  logs       - Tail logs"
	@echo "  ps         - List containers"
	@echo "  psql       - Open psql shell in db container"
	@echo "  prune      - Remove volumes (pgdata, redisdata, pgadmin)"

up:
	$(COMPOSE) up -d db redis

up-dev:
	$(COMPOSE_DEV) up -d

down:
	$(COMPOSE) down

down-dev:
	$(COMPOSE_DEV) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

psql:
	docker exec -it snippetly-db psql -U $${POSTGRES_USER:-snippetly} -d $${POSTGRES_DB:-snippetly}

prune:
	$(COMPOSE) down -v

mongo:
	docker exec -it snippetly-mongodb mongosh -u $${MONGO_USER:-snippetly} -p $${MONGO_PASSWORD:-mongodb} --authenticationDatabase admin
