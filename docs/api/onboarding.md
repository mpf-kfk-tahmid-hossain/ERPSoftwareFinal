# Company Onboarding API

## Login
- **URL:** `/login/`
- **Method:** `POST`
- **Payload:** `username`, `password`
- **Response:** Redirects to `/` (dashboard) on success

## Add Company
- **URL:** `/companies/add/`
- **Method:** `POST`
- **Auth:** Superuser
- **Payload:** `name`, `code`, `address`
- **Response:** Redirect to company list

## Company Detail
- **URL:** `/companies/<id>/`
- **Method:** `GET`
- **Auth:** Superuser
- **Response:** Company info JSON or HTML

## Company Update
- **URL:** `/companies/<id>/edit/`
- **Method:** `POST`
- **Auth:** Superuser
- **Payload:** `name`, `code`, `address`

## User List
- **URL:** `/companies/<id>/users/`
- **Method:** `GET`
- **Auth:** Company Admin or Superuser
- **Response:** List of users for company
- **Query Params:** `q` search string, `sort` field (`-field` for descending), `is_active` filter, `page` for pagination

## Company List
- **URL:** `/companies/`
- **Method:** `GET`
- **Auth:** Superuser
- **Query Params:** `q` search string, `sort` field (`-field` for descending), `page` for pagination

## Role List
- **URL:** `/roles/`
- **Method:** `GET`
- **Auth:** Company Admin
- **Query Params:** `q` search string, `sort` field (`-field` for descending), `page` for pagination

## Audit Log List
- **URL:** `/audit-logs/`
- **Method:** `GET`
- **Auth:** Auditor or Superuser
- **Query Params:** `q` search string, `request_type` filter, `actor` filter, `sort` field (`-field` for descending), `page` for pagination

## Create Company User
- **URL:** `/companies/<id>/users/add/`
- **Method:** `POST`
- **Auth:** Company Admin or Superuser
- **Payload:** `username`, `password1`, `password2`
- **Files:** `profile_picture` optional image file.
- **Notes:** if the acting user has `add_role` permission they may create a new role during user creation; otherwise only existing roles can be chosen.

## User Detail
- **URL:** `/users/<id>/`
- **Method:** `GET`
- **Auth:** Company Admin or Superuser

## Update User
- **URL:** `/users/<id>/edit/`
- **Method:** `POST`
- **Permissions:**
  - `change_user` permission required for all edits.
  - Current password must be supplied when editing your own profile.
- **Payload:** standard user fields (`username`, `email`, etc.) plus `current_password` when self-editing.
- **Files:** `profile_picture` optional image file.
- **Audit:** all user edits are recorded in `AuditLog` entries.
- **Notes:** new roles can be created during editing only when the user has `add_role` permission.

## Role Management
- **List Roles:** `GET /roles/`
- **Create Role:** `POST /roles/add/`
- **Update Role:** `POST /roles/<id>/edit/`
- **Permissions:** `view_role`, `add_role`, `change_role`


## Toggle User Active
- **URL:** `/users/<id>/toggle/`
- **Method:** `POST`

## Whoami
- **URL:** `/api/whoami/`
- **Method:** `GET`
- **Auth:** Logged in user
- **Response:** JSON with current user info

## Dashboard API
- **URL:** `/api/dashboard/`
- **Method:** `GET`
- **Auth:** Logged in user
- **Response:** JSON summary of user and company

## Errors
- **403 Permission Denied:** Returned when a user lacks required role. JSON format for `/api/*` endpoints: `{ "detail": "Permission denied" }` and `403.html` page for others.

## Session
- **Logout URL:** `/logout/` via `GET`.

## Change Password
- **URL:** `/users/<id>/password/`
- **Method:** `POST`
- **Auth:** Logged in user
- **Permissions:**
  - Users can change their own password.
  - `user_can_change_password` required to change another user's password.
- **Payload:**
  - `current_password` (required when changing your own password)
  - `password1`, `password2`
- **Audit:** password changes are recorded in `AuditLog`.


