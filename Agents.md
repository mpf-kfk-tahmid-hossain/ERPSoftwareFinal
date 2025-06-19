# Agents.md

## 👋 Welcome, Agent!

You are an **AI Agent** integrated with this ERP system.
Your core responsibility is to **implement business workflows**—translating workflow documentation into working features using the system’s database and UI stack.

---

## **Your Mission**

1. **Read the Data Model**

   * Reference: `Database_Structure.sql`
   * This file defines the complete table structure, fields, and relationships for the ERP.
   * **Use this as your source of truth** for all database operations and models.

2. **Follow the Workflow Guide**

   * Reference: `workflow.md`
   * This document lists the business workflows and feature tasks to implement, maintain, or improve.
   * **Work through these tasks in order**, reusing any common patterns already described.

---

## **Your Operating Principles**

* **Implement Features End-to-End**

  * For each workflow task, ensure the full user flow: backend (Django), frontend (React), and database logic.
  * Where possible, **reuse or extend** existing workflows or components for consistency and efficiency.

* **Update Navigation**

  * **Always update the Navigation** (sidebar, menu, dashboard links, etc.) whenever you add, modify, or remove a workflow, module, or major feature.
  * Navigation should reflect all current workflows and entry points—**no orphaned or missing links**.
  * Use established navigation patterns; new flows must be accessible from appropriate places.

* **Track Progress**

  * When a task is complete, **mark it as implemented** in `workflow.md` with a short note.
  * If you extend, modify, or reuse a workflow, **reference the original workflow** in your implementation note.

* **Tech Stack Guidelines**

  * **Backend:** Django (Python) for all API, business logic, and data access.
  * **Frontend:** React, using [Bootstrap CDN](https://getbootstrap.com/docs/5.3/getting-started/introduction/) for styling (`<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">`).
  * Your UI must be clean, responsive, and easy to use—no “raw” forms or clunky layouts.

---

## **Navigation Requirements**

* **Navigation is a First-Class Feature**

  * Every time you add, update, or remove a workflow or module, **ensure the navigation menus are updated accordingly**.
  * All new features and flows must be discoverable and easily accessible.
  * Follow project conventions for grouping, icons, and order.
  * When deprecating a feature, remove or update the corresponding navigation item.

* **Documentation**

  * **Document changes to navigation** (if non-obvious) in the relevant workflow documentation, so others can find the new/updated entry points.

---

## **Documentation Requirements**

* **API Documentation**

  * For each workflow or feature you implement, **document the API endpoints** used or created.
  * Include request/response structure, required parameters, authentication/authorization info, and example payloads.
  * API documentation should be maintained in the `/docs/api/` directory or the most appropriate project location.
  * If possible, auto-generate Swagger/OpenAPI docs.

* **Workflow Documentation**

  * When you create or update a workflow, update `workflow.md` with a description of the flow, user roles involved, permissions, and step-by-step actions.
  * **Note any navigation changes** so users know where to access the new/updated feature.

---

## **Testing Requirements**

* **End-to-End Testing**

  * For each workflow, **create tests** to verify that everything works as expected, from the UI to the backend API and database.
  * UI tests should simulate real user actions in React (using libraries such as Jest, React Testing Library, or Cypress).
  * Backend tests should cover API endpoints and business logic in Django (using Django’s test framework or Pytest).
  * All tests should run in CI and must pass before a workflow is marked as complete.

---

## **Best Practices**

* Always validate permissions, check user roles, and log important actions.
* Write code that is readable, modular, and follows project conventions.
* Use existing utilities and patterns when possible; **do not reinvent the wheel**.
* Documentation, navigation, and testing are not optional—they are part of your deliverable.

---

## **Example Workflow**

**Suppose `workflow.md` includes:**
`[ ] Implement "Create Sales Order" flow (see CRM-to-Invoice story in workflow.md).`

You will:

1. Review the `Database_Structure.sql` for all related tables (`sales_order`, `customer`, `product`, etc.).
2. Check if a similar sales order flow exists.

   * If so, reuse or extend components.
3. Build any missing backend endpoints in Django.
4. Create a React form or UI for creating sales orders, using Bootstrap for design.
5. **Add or update the sales order entry in the main navigation, so users can access it.**
6. Document all relevant API endpoints in `/docs/api/`.
7. Update `workflow.md` with the completed flow, referencing permissions and business logic.

   * **Note the navigation change in your documentation.**
8. Write and run tests for both backend and frontend covering the workflow.
9. Mark the task in `workflow.md` as `[x] Implemented by Agent on YYYY-MM-DD — based on CRM-to-Invoice pattern. API docs and tests completed. Navigation updated.`

---

## **What You Must Remember**

* Your job is to **build features, not just checkboxes**.
* You must **leverage and extend** existing workflows, not duplicate work.
* **API documentation**, **navigation updates**, and **workflow tests** are mandatory for every task.
* Documentation is part of your job—**keep all docs, navigation, and references up to date**.

---

**Happy building, Agent!**
*(If you are reading this as a human developer, these principles apply to you too!)*

---
