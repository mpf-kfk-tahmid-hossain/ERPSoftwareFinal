# Audit Log

## List Logs
- **URL:** `/audit-logs/`
- **Method:** `GET`
- **Auth:** Logged in users with `view_auditlog` permission or superuser.
- **Description:** Shows latest 100 audit log entries. Non-superusers only see logs from their company.
- **Response:** HTML table with timestamp, user, action, request type, target user, and company.
