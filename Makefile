
up:
	docker-compose up --build

deploy:
	# docker pull:
	docker-compose build
	# sync dags_folder:
	docker run -it --rm \
		-e DOCKER_COMPOSE_MODE=1 \
		-v `pwd`/_dags:/opt/airflow/dags/ \
		-v /var/run/docker.sock:/var/run/docker.sock \
		airflow_docker_airflow:latest \
		airflow_pull_dags_folder.py airflow_docker_project_simple:latest
	docker run -it --rm \
		-e DOCKER_COMPOSE_MODE=1 \
		-v `pwd`/_dags:/opt/airflow/dags/ \
		-v /var/run/docker.sock:/var/run/docker.sock \
		airflow_docker_airflow:latest \
		airflow_pull_dags_folder.py airflow_docker_project_complex:latest
