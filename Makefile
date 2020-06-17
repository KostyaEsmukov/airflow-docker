
up:
	docker-compose up --build

deploy:
	# docker pull:
	docker-compose build
	# sync dags_folder:
	# XXX airflow_pull_dags_folder.py
