# Database migrations

Model changes do not update existing tables through `Base.metadata.create_all()`.
Apply the migration from the backend directory after backing up the database:

```powershell
cd backend
..\venv\Scripts\python.exe -m alembic upgrade head
```

The inventory and location unique constraints will not be created when duplicate
rows exist. The migration stops with an error so the duplicate data can be merged
without silently deleting stock records.
