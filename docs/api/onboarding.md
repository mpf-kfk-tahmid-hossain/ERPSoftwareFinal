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

## Create Company User
- **URL:** `/companies/<id>/users/add/`
- **Method:** `POST`
- **Auth:** Company Admin or Superuser
- **Payload:** `username`, `password1`, `password2`

## User Detail
- **URL:** `/users/<id>/`
- **Method:** `GET`
- **Auth:** Company Admin or Superuser

## Update User
- **URL:** `/users/<id>/edit/`
- **Method:** `POST`

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


