infra:
	docker-compose -f docker/docker-compose.yml --env-file .env up --build -d db

teardown:
	docker-compose -f docker/docker-compose.yml --env-file .env down -v db
