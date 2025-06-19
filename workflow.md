# Workflow

## **Workflow Description: Company Onboarding + User Setup**

### **Purpose**

This workflow is the foundational onboarding flow for a multi-tenant ERP system. It enables a superuser to register a new company (tenant), create the company’s first administrative user, and hand off access so that the company admin can manage their organization independently. The workflow also sets up the basic permission and session infrastructure required for all subsequent ERP operations.

---

### **Actors**

* **Superuser**: The system administrator responsible for onboarding new companies and their first admin users.
* **Company Admin**: The first user for a new company, who has administrative permissions within their own company (but not for others).

---

### **Workflow Steps**

1. **Superuser Authentication**

   * Superuser logs into the ERP platform using secure credentials.

2. **Company Registration**

   * Superuser creates a new company by providing the required details (name, code, address).
   * The company record is stored and made available in the system.

3. **Company Admin User Creation**

   * Superuser creates the first user (admin) for the new company.
   * Assigns the “Admin” role to this user.
   * The admin user receives credentials for login.

4. **Company Admin Authentication**

   * The new admin logs in with their credentials.
   * System establishes a session and enforces role-based permissions.

5. **Company Admin Dashboard Access**

   * Upon successful login, the company admin lands on a dashboard/welcome page tailored to their company.
   * The admin can view company information and (optionally) proceed to onboard additional users or configure company settings.

6. **Role and Permission Enforcement**

   * All APIs and UIs enforce role-based permissions.
   * Only superusers can onboard new companies and admins.
   * Company admins can only manage data within their own company.

7. **Session Management**

   * The system manages login/logout for both superuser and company admin, maintaining secure and separate sessions.

---

### **Key Features**

* **Multi-tenant architecture**: Each company’s data is isolated.
* **Role-based access control (RBAC)**: Only users with correct roles can perform onboarding steps.
* **End-to-end onboarding**: Covers both backend (API) and frontend (UI) for registration, login, and basic user management.
* **Auditability**: (Optional for future) System logs each onboarding action for security and compliance.

---

### **Outcome**

After this workflow:

* A new company (tenant) exists in the ERP.
* Its first admin user can securely log in and begin managing the organization.
* Permissions, roles, and session management are in place to support all future ERP operations.

Here’s your **expanded checklist** including **CRUD views, session/auth, and all additional key views** (with task breakdown for API and UI as needed):

---

### 📋 **ERP Workflow Implementation Checklist: Company Onboarding + User Setup**

| #  | Task                                                          | Status            |
| -- | ------------------------------------------------------------- | ----------------- |
| 1  | **Design & Create “Admin” Role (if not seeded)**              | ⬜ Not Implemented |
| 2  | **Superuser Login API**                                       | ⬜ Not Implemented |
| 3  | **Superuser Login UI (Form)**                                 | ⬜ Not Implemented |
| 4  | **Company List API**                                          | ⬜ Not Implemented |
| 5  | **Company List UI (Table/View)**                              | ⬜ Not Implemented |
| 6  | **Company Registration API**                                  | ⬜ Not Implemented |
| 7  | **Company Registration UI (Form)**                            | ⬜ Not Implemented |
| 8  | **Company Detail API**                                        | ⬜ Not Implemented |
| 9  | **Company Detail UI (View)**                                  | ⬜ Not Implemented |
| 10 | **Company Update API**                                        | ⬜ Not Implemented |
| 11 | **Company Update UI (Form/Edit Page)**                        | ⬜ Not Implemented |
| 12 | **User List API (per company)**                               | ⬜ Not Implemented |
| 13 | **User List UI (Table/View)**                                 | ⬜ Not Implemented |
| 14 | **Company Admin User Creation API**                           | ⬜ Not Implemented |
| 15 | **Company Admin User Creation UI (Form)**                     | ⬜ Not Implemented |
| 16 | **User Detail API**                                           | ⬜ Not Implemented |
| 17 | **User Detail UI (Profile/View)**                             | ⬜ Not Implemented |
| 18 | **User Update API**                                           | ⬜ Not Implemented |
| 19 | **User Update UI (Edit Profile/Page)**                        | ⬜ Not Implemented |
| 20 | **Deactivate/Reactivate User API (Soft Delete)**              | ⬜ Not Implemented |
| 21 | **Deactivate/Reactivate User UI (Button/Action)**             | ⬜ Not Implemented |
| 22 | **Assign Admin Role to New User (user\_role) API**            | ⬜ Not Implemented |
| 23 | **Assign Admin Role UI (Role Select/Assign)**                 | ⬜ Not Implemented |
| 24 | **Company Admin Login API**                                   | ⬜ Not Implemented |
| 25 | **Company Admin Login UI (Form)**                             | ⬜ Not Implemented |
| 26 | **Session Management (Login/Logout) API**                     | ⬜ Not Implemented |
| 27 | **Session Management (Login/Logout) UI**                      | ⬜ Not Implemented |
| 28 | **Whoami (Current User) API**                                 | ⬜ Not Implemented |
| 29 | **Company Admin Dashboard API**                               | ⬜ Not Implemented |
| 30 | **Company Admin Dashboard UI (Welcome View)**                 | ⬜ Not Implemented |
| 31 | **Permission/Role Enforcement on All APIs**                   | ⬜ Not Implemented |
| 32 | **Permission/Role Enforcement on All UI (Hide/Show by role)** | ⬜ Not Implemented |
| 33 | **API Documentation for All Above**                           | ⬜ Not Implemented |
| 34 | **UI/Integration Tests for Full Flow**                        | ⬜ Not Implemented |
| 35 | **Permissions Tests (Unauthorized Access Prevention)**        | ⬜ Not Implemented |
| 36 | **Permission Denied/Error Views (UI & API)**                  | ⬜ Not Implemented |

---

### **How to Use**

* **Check** each item (`✅ Implemented`) as you finish.
* This covers all **CRUD**, **specialized**, and **auth/session** views for the onboarding workflow.

