# Database migrations

Model changes do not update existing tables through `Base.metadata.create_all()`.
Apply the migration from the backend directory after backing up the database:

```powershell
cd backend
..\venv\Scripts\python.exe -m alembic upgrade head
```

Docker deployments run this command automatically before the API starts. The
user migration replaces the required email field with a display name and uses
the existing username as the initial name for accounts already in the database.

The inventory and location unique constraints will not be created when duplicate
rows exist. The migration stops with an error so the duplicate data can be merged
without silently deleting stock records.
