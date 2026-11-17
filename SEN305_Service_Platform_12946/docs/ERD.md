# Entity relationship design

- User 1 — many ServiceRequest (`requester`, PROTECT)
- Category 1 — many ServiceRequest (PROTECT)
- ServiceRequest 1 — 0..1 WorkOrder (CASCADE; OneToOneField)
- User 1 — many WorkOrder (`technician`, PROTECT)
- ServiceRequest 1 — many Comment (CASCADE)
- User 1 — many Comment (`author`, PROTECT)

ServiceRequest uses a UUID primary key. Category names are unique. Priority is constrained to 1 (highest) through 5 (lowest), in both model validation and a database check constraint. Status is a controlled TextChoices field. Lab 3 indexes support category/status and priority/created date; Part N adds status/due date.
