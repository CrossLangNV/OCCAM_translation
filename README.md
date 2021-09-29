FASTAPI for the microservice: translation of layout XML

### Get in docker

```
docker-compose up -d
docker-compose exec xml_trans bash
```

#### Alembic

[Tutorial]([https://sairamkrish.medium.com/python-rest-api-using-fastapi-and-sqlalchemy-f3e9a92ae2ad)

1.

```cd app```

1.

This will scan the models and generate upgrade & downgrade scripts

```
alembic revision --autogenerate -m "Update table with use-tm"

alembic upgrade head
```

1. (If Alembic is not yet initialised:)

```
alembic init db-migration
```
