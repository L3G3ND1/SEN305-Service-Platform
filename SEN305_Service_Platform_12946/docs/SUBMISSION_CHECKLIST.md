# SEN305 final evidence checklist

- [ ] Home, About, Contact, Workflow pages return HTTP 200; unknown URL returns 404.
- [ ] MySQL 8 connection confirmed for database `sen305_servicedesk` without displaying password.
- [ ] `0001_initial.py` is the Lab 3 original schema and is not edited for Part N.
- [ ] `0002` reviewed with `python manage.py sqlmigrate requests_app 0002` and applied.
- [ ] Admin shows due_at and resolution_summary; overdue filter works.
- [ ] Due-date query with two synthetic requests demonstrated.
- [ ] `full_clean()` rejects resolved/closed request without resolved_at and non-empty summary.
- [ ] `python manage.py test requests_app -v 2` passes.
- [ ] At least ten synthetic records across two categories and three statuses exist.
- [ ] Actual queryset SQL and MySQL EXPLAIN output recorded in QUERY_EVIDENCE_TEMPLATE.md.
- [ ] `python manage.py makemigrations --check --dry-run` reports no changes.
- [ ] `.env` is ignored; no real personal/service data or secrets submitted.
