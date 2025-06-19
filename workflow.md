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
| 1  | **Design & Create “Admin” Role (if not seeded)**              | ✅ Implemented by Agent |
| 2  | **Superuser Login API**                                       | ✅ Implemented by Agent |
| 3  | **Superuser Login UI (Form)**                                 | ✅ Implemented by Agent |
| 4  | **Company List API**                                          | ✅ Implemented by Agent |
| 5  | **Company List UI (Table/View)**                              | ✅ Implemented by Agent |
| 6  | **Company Registration API**                                  | ✅ Implemented by Agent |
| 7  | **Company Registration UI (Form)**                            | ✅ Implemented by Agent |
| 8  | **Company Detail API**                                        | ✅ Implemented by Agent |
| 9  | **Company Detail UI (View)**                                  | ✅ Implemented by Agent |
| 10 | **Company Update API**                                        | ✅ Implemented by Agent |
| 11 | **Company Update UI (Form/Edit Page)**                        | ✅ Implemented by Agent |
| 12 | **User List API (per company)**                               | ✅ Implemented by Agent |
| 13 | **User List UI (Table/View)**                                 | ✅ Implemented by Agent |
| 14 | **Company Admin User Creation API**                           | ✅ Implemented by Agent |
| 15 | **Company Admin User Creation UI (Form)**                     | ✅ Implemented by Agent |
| 16 | **User Detail API**                                           | ✅ Implemented by Agent |
| 17 | **User Detail UI (Profile/View)**                             | ✅ Implemented by Agent |
| 18 | **User Update API**                                           | ✅ Implemented by Agent |
| 19 | **User Update UI (Edit Profile/Page)**                        | ✅ Implemented by Agent |
| 20 | **Deactivate/Reactivate User API (Soft Delete)**              | ✅ Implemented by Agent |
| 21 | **Deactivate/Reactivate User UI (Button/Action)**             | ✅ Implemented by Agent |
| 22 | **Assign Admin Role to New User (user\_role) API**            | ✅ Implemented by Agent |
| 23 | **Assign Admin Role UI (Role Select/Assign)**                 | ✅ Implemented by Agent |
| 24 | **Company Admin Login API**                                   | ✅ Implemented by Agent |
| 25 | **Company Admin Login UI (Form)**                             | ✅ Implemented by Agent |
| 26 | **Session Management (Login/Logout) API**                     | ✅ Implemented by Agent |
| 27 | **Session Management (Login/Logout) UI**                      | ✅ Implemented by Agent |
| 28 | **Whoami (Current User) API**                                 | ✅ Implemented by Agent |
| 29 | **Company Admin Dashboard API**                               | ✅ Implemented by Agent |
| 30 | **Company Admin Dashboard UI (Welcome View)**                 | ✅ Implemented by Agent |
| 31 | **Permission/Role Enforcement on All APIs**                   | ✅ Implemented by Agent |
| 32 | **Permission/Role Enforcement on All UI (Hide/Show by role)** | ✅ Implemented by Agent |
| 33 | **API Documentation for All Above**                           | ✅ Implemented by Agent |
| 34 | **UI/Integration Tests for Full Flow**                        | ✅ Implemented by Agent |
| 35 | **Permissions Tests (Unauthorized Access Prevention)**        | ✅ Implemented by Agent |
| 36 | **Permission Denied/Error Views (UI & API)**                  | ✅ Implemented by Agent |

---

### **How to Use**

* **Check** each item (`✅ Implemented`) as you finish.
* This covers all **CRUD**, **specialized**, and **auth/session** views for the onboarding workflow.

Navigation updated to include Users link for company admins.
