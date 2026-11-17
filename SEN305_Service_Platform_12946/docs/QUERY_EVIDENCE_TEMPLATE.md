# Query analysis evidence — MySQL 8

Command: `python manage.py seed_lab_data`

Command: `python manage.py analyse_requests`

Query requirement: Electrical category AND status in (open, assigned), ordered by priority then created_at.

## Generated SQL

```sql
SELECT `requests_app_servicerequest`.`id`, `requests_app_servicerequest`.`requester_id`, `requests_app_servicerequest`.`category_id`, `requests_app_servicerequest`.`title`, `requests_app_servicerequest`.`description`, `requests_app_servicerequest`.`location`, `requests_app_servicerequest`.`priority`, `requests_app_servicerequest`.`status`, `requests_app_servicerequest`.`resolved_at`, `requests_app_servicerequest`.`created_at`, `requests_app_servicerequest`.`updated_at`, `requests_app_servicerequest`.`due_at`, `requests_app_servicerequest`.`resolution_summary` FROM `requests_app_servicerequest` WHERE (`requests_app_servicerequest`.`category_id` = 1 AND(`requests_app_servicerequest`.`status` = open OR `requests_app_servicerequest`.`status` = assigned)) ORDER BY `requests_app_servicerequest`.`priority` ASC, `requests_app_servicerequest`.`created_at` ASC
```

## EXPLAIN output

```text
-> Sort row IDs: requests_app_servicerequest.priority, requests_app_servicerequest.created_at  (cost=2.31 rows=4)
    -> Index range scan on requests_app_servicerequest using req_cat_status_idx over (category_id = 1 AND status = 'assigned') OR (category_id = 1 AND status = 'open'), with index condition: ((requests_app_servicerequest.category_id = 1) and ((requests_app_servicerequest.`status` = 'open') or (requests_app_servicerequest.`status` = 'assigned')))  (cost=2.31 rows=4)
```

## Index analysis

MySQL selected **`req_cat_status_idx`** for an index range scan. The plan shows two ranges for the selected category (`category_id = 1`): one for `status = 'assigned'` and one for `status = 'open'`. This index supports the category-and-status filtering. MySQL then performs a separate sort by `priority` and `created_at`; the EXPLAIN output does not show that the index satisfies the requested ordering.

The plan estimates 4 matching rows. The reported plan is an index range scan, not a full table scan (`type=ALL` / `key=NULL`).

**Details still to add if required by the lecturer:** MySQL server version and total synthetic row count. They were not included in the terminal output supplied for this evidence, so they have deliberately not been guessed.
