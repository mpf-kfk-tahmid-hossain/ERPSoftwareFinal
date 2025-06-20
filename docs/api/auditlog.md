# Audit Log

## List Logs
- **URL:** `/audit-logs/`
- **Method:** `GET`
- **Auth:** Logged in users with `view_auditlog` permission or superuser.
- **Description:** Shows latest 100 audit log entries. Non-superusers only see logs from their company.
- **Query Params:** `q` search string, `request_type` filter, `actor` filter, `sort` field (`-field` for descending), `page` for pagination
- **Response:** HTML table with timestamp, user, action, request type, target user, and company.

## Log Detail
- **URL:** `/audit-logs/<id>/`
- **Method:** `GET`
- **Auth:** Logged in users with `view_auditlog` permission or superuser.
- **Description:** Shows a single audit log entry with fields and formatted JSON details.
- **Response:** HTML page with log info and pretty-printed details.
