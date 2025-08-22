db:
	docker compose -f docker-compose.yml --env-file .env.docker up db -d --build

start-app:
	docker compose -f docker-compose.yml --env-file .env.docker up --build -d

teardown-app:
	docker compose -f docker-compose.yml --env-file .env.docker down -v 

apply-alembic:
	alembic -c migrations/*.ini upgrade head
