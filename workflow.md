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
| 37 | **Audit Logging Middleware for all requests**                 | ✅ Implemented by Agent |
| 38 | **Role Management (list/create/update) UI & API**             | ✅ Implemented by Agent |
| 39 | **Audit Log list view with filtering**                        | ✅ Implemented by Agent |
|    | *(2024-??)* Actor filter updated to list all users in the company. | |
| 40 | **Audit Log detail view with formatted JSON**                 | ✅ Implemented by Agent |

---

### **How to Use**

* **Check** each item (`✅ Implemented`) as you finish.
* This covers all **CRUD**, **specialized**, and **auth/session** views for the onboarding workflow.

Navigation updated to include Users link for company admins.
Logout view updated to accept GET requests so the navbar logout button works.
User creation now supports assigning or creating roles with permissions.
Permission checks unified via `@require_permission` decorator.
Added change password flow with self-service capability.
Change password and profile edit now require the current password when performed by the user.
Editing a user requires the `change_user` permission even for self edits.
Password changes and user updates are logged via `AuditLog`.
Buttons are hidden unless the user has the appropriate permission.
Added audit logging middleware to capture every authenticated request.
Implemented role management screens and ability to change a user's role during edit.
Creating a new role from the user form now requires the `add_role` permission.
User detail view now shows role, permissions, recent audit logs and profile pictures. User list supports search and pagination.
Fixed profile picture display by configuring MEDIA_URL and MEDIA_ROOT.
List views now share filter and pagination components. All list tables allow sorting by any column via reusable headers.
Filter forms now use HTMX for live updates with a 500ms delay and include labels for each field. Sorting arrows display only on the active column and the user profile view uses cards with a recent activity table.

---

## **Workflow Description: Product & Inventory Management (with Warehouse Stock Movement & Adjustment)**

### **Purpose**

This workflow enables each company to manage its entire product catalog, warehouse structure, and inventory levels—including all stock-in, stock-out, transfers, and adjustments—while enforcing company isolation, roles, and audit trails. This is foundational for procurement, sales, and production operations in the ERP.

---

### **Actors**

* **Company Admin**: Manages products, categories, warehouses, and has full access to inventory operations for their company.
* **Warehouse Manager**: (Optional) Handles day-to-day stock movements and adjustments within assigned warehouses.
* **Auditor**: (Optional) Views inventory logs and stock adjustments for compliance.

---

### **Workflow Steps**

1. **Product & Category Setup**

   * Create product categories (with parent/child relationships for organization).
   * Create product units (e.g., pcs, kg, box).
   * Create products with SKU, barcode, type, unit, brand, category, and description.
   * Assign each product to a company (data isolation).

2. **Warehouse Setup**

   * Create warehouses with name and location.
   * Each warehouse is assigned to a company.

3. **Stock Lot/Batch Creation**

   * For products that require batch/lot tracking, create stock lots with batch number, expiry date, and initial quantity in a warehouse.

4. **Inventory Movement (Stock In/Out/Transfer)**

   * Record all inbound (purchase, production, adjustment) and outbound (sales, consumption) stock movements.
   * Transfer stock between warehouses with clear “from” and “to” locations.
   * Each movement records date, user, reference, warehouse(s), product, batch, and quantity.

5. **Inventory Adjustment**

   * Allow authorized users to adjust stock levels for a product/warehouse/lot with a required reason (e.g., damage, audit correction).
   * All adjustments are logged for audit purposes.

6. **Stock On Hand Calculation**

   * System provides real-time inventory on hand per product, per warehouse, per lot.

7. **Audit & Reporting**

   * All inventory changes (movement, adjustment) are logged and reportable.
   * List and filter inventory transactions by product, warehouse, date, type, or user.
   * Full audit trail viewable by authorized roles.

---

### **Key Features**

* **Multi-company isolation:** All inventory data is separated per company.
* **RBAC:** Only authorized users can create/edit/delete products, manage warehouses, and perform inventory movements or adjustments.
* **Comprehensive CRUD:** Products, categories, units, warehouses, stock lots.
* **Inventory movement:** Every stock in, out, and transfer is tracked and reportable.
* **Auditability:** All stock operations are audit logged.
* **Search & filter:** Inventory lists, movement logs, and reports can be filtered and sorted.

---

### **Outcome**

After this workflow:

* Each company manages their own product catalog and warehouses.
* All inventory movements and adjustments are tracked and auditable.
* Users have real-time, accurate stock visibility across the organization.
* System is ready for expansion to purchasing, sales, and production flows.

---

### 📋 **ERP Workflow Implementation Checklist: Product & Inventory Management**

| #  | Task                                               | Status            |
| -- | -------------------------------------------------- | ----------------- |
| 1  | **Product Category CRUD (API + UI)**               | ✅ Implemented by Agent |
| 2  | **Product Unit CRUD (API + UI)**                   | ✅ Implemented by Agent |
| 3  | **Product CRUD (API + UI)**                        | ✅ Implemented by Agent |
| 4  | **Warehouse CRUD (API + UI)**                      | ✅ Implemented by Agent |
| 5  | **Stock Lot CRUD (API + UI)**                      | ✅ Implemented by Agent |
| 6  | **Inventory Movement: In/Out/Transfer (API + UI)** | ✅ Implemented by Agent |
| 7  | **Inventory Adjustment (API + UI, with reason)**   | ✅ Implemented by Agent |
| 8  | **Stock On Hand Listing/Report (API + UI)**        | ✅ Implemented by Agent |
| 9  | **Audit Logging for Inventory Actions**            | ✅ Implemented by Agent |
| 10 | **Permission/Role Enforcement for all actions**    | ✅ Implemented by Agent |
| 11 | **Stock Movement History/Log (API + UI)**          | ✅ Implemented by Agent |
| 12 | **API Documentation for all endpoints**            | ✅ Implemented by Agent |
| 13 | **Integration/UI Tests for full workflow**         | ✅ Implemented by Agent |
| 14 | **Category Tree management UI**                    | ✅ Implemented by Agent |

---

### **How to Use**

* **Check** each item (`✅ Implemented`) as you finish.
* This covers all **CRUD**, inventory movement, stock tracking, adjustment, and reporting for the inventory workflow.

---
