# Running Dockerfized Declarative DAGs in Airflow

## Getting Started

Run the docker-compose stack:
```
make up
```

Once it is up, navigate to http://localhost:8080 , login with `admin`:`admin`.

No DAGs will show up at this point.

Trigger deploy from the images:

```
make deploy
```

DAGs will show up in the webserver. Turn them on as usual.
