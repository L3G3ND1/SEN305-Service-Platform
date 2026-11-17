# SEN305 Enterprise Service Request and Maintenance Platform

Django 5.2 project prepared against the supplied Veritas University SEN305 Lab Session 2, 3 and 4 notes and the Part N in-lab exercise shared in the conversation.

## Project contents
- `backend/core`: public Home, About, Contact and Workflow pages from Lab 2.
- `backend/requests_app`: Lab 3 domain models and Lab 4 secure request workflow.
- `backend/requests_app/migrations/0001_initial.py`: original Lab 3 schema.
- `backend/requests_app/migrations/0002_service_request_due_at_resolution_summary_and_index.py`: Part N extension only. Do not edit 0001.
- Model validation, admin overdue filter, forms, selectors, transaction-safe services, authenticated CRUD, assignment, resolution, pagination and tests.
- Management commands to create synthetic lab data and print SQL/EXPLAIN evidence.

## Windows setup (PowerShell)
From the extracted project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend
equirements.txt
Copy-Item backend\.env.example backend\.env
cd backend
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_lab_data
python manage.py test requests_app -v 2
python manage.py runserver
```

Open `http://127.0.0.1:8000/`, `/requests/` and `/admin/`. The default database is SQLite so the project can be opened immediately. The Lab 3 acceptance criterion specifically requires MySQL 8; configure MySQL as described below before collecting final database evidence.

## MySQL 8 configuration (required for Lab 3 evidence)
1. Install and start MySQL 8 / MySQL80.
2. In MySQL as an administrator, create the database and least-privilege user (replace the password):

```sql
CREATE DATABASE sen305_servicedesk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sen305_app'@'localhost' IDENTIFIED BY 'replace-with-a-strong-password';
GRANT ALL PRIVILEGES ON sen305_servicedesk.* TO 'sen305_app'@'localhost';
FLUSH PRIVILEGES;
```
3. Edit `backend/.env` and set `DB_ENGINE=mysql`, `DB_NAME=sen305_servicedesk`, `DB_USER=sen305_app`, `DB_PASSWORD=your-password`, `DB_HOST=127.0.0.1`, `DB_PORT=3306`.
4. Install the driver if needed: `pip install mysqlclient` (Windows may require the matching Visual C++ build tools / wheel).
5. Run `python manage.py check`, `python manage.py migrate`, `python manage.py seed_lab_data`, then `python manage.py analyse_requests`.

Never commit `backend/.env`. `.env.example` contains placeholders only. Do not use real service-request or personal data; the seed command creates synthetic records.

## Required exercise commands

```powershell
python manage.py makemigrations --check --dry-run
python manage.py showmigrations requests_app
python manage.py sqlmigrate requests_app 0002
python manage.py migrate
python manage.py test requests_app -v 2
python manage.py seed_lab_data
python manage.py analyse_requests
```

`analyse_requests` prints the generated queryset SQL and database EXPLAIN plan. `docs/ROLLBACK_TEST.md` contains the Lab 4 deliberate rollback demonstration. Record the actual index selected by your MySQL server. With a small synthetic table, MySQL may correctly choose a table scan; do not claim an index was used unless the real EXPLAIN output shows it.

## Important submission note
This is a complete project scaffold with reviewed migration files and test/evidence commands. The project files were syntax-checked and the archive integrity was checked, but Django could not be installed in the build environment because package-network access was unavailable; therefore the automated Django test suite has not been executed here. The archive cannot truthfully contain a live MySQL server result from your computer. Run the commands above on the target MySQL 8 instance and capture the actual output/screenshots before claiming the MySQL acceptance criterion is verified. Also check your lecturer's submission portal for the exact required evidence format.
