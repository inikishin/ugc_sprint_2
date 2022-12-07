rerun:
	docker-compose down
	docker image rm auth_sprint_1_auth_api
	docker-compose up --detach --force-recreate
	docker-compose ps
