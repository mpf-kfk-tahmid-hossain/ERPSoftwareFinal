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

  * For each workflow task, ensure the full user flow: backend (Django), frontend (HTMX + custom HTML forms), and database logic.
  * **Do not use Django’s built-in forms or ModelForm.**
    Write custom HTML forms for all data entry and validation.
  * Use **HTMX** for frontend interactivity (form submission, partial updates, inline editing, etc.).
  * Where possible, **reuse or extend** existing workflows/components for consistency and efficiency.

* **Update Navigation**

  * **Always update the Navigation** (sidebar, menu, dashboard links, etc.) whenever you add, modify, or remove a workflow, module, or major feature.
  * Navigation should reflect all current workflows and entry points—**no orphaned or missing links**.
  * Use established navigation patterns; new flows must be accessible from appropriate places.

* **Track Progress**

  * When a task is complete, **mark it as implemented** in `workflow.md` with a short note.
  * If you extend, modify, or reuse a workflow, **reference the original workflow** in your implementation note.

* **Tech Stack Guidelines**

  * **Backend:** Django (Python) for all API, business logic, and data access.
  * **Frontend:** **Django templates with HTMX** for interactivity and **custom HTML forms** (not Django’s built-in forms).
  * **Styling:** Use [Bootstrap CDN](https://getbootstrap.com/docs/5.3/getting-started/introduction/):
    `<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">`
  * UI must be clean, responsive, and easy to use—no “raw” forms or clunky layouts.

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
  * UI tests should simulate real user actions (HTMX interaction and form submission).
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
4. Create a custom HTML form for creating sales orders in a Django template (use Bootstrap for styling).
5. Use **HTMX** for dynamic/partial UI updates (e.g., inline add/edit, partial reloads).
6. **Add or update the sales order entry in the main navigation, so users can access it.**
7. Document all relevant API endpoints in `/docs/api/`.
8. Update `workflow.md` with the completed flow, referencing permissions and business logic.

   * **Note the navigation change in your documentation.**
9. Write and run tests for both backend and frontend covering the workflow.
10. Mark the task in `workflow.md` as `[x] Implemented by Agent on YYYY-MM-DD — based on CRM-to-Invoice pattern. API docs and tests completed. Navigation updated.`

---

## **What You Must Remember**

* Your job is to **build features, not just checkboxes**.
* You must **leverage and extend** existing workflows, not duplicate work.
* **API documentation**, **navigation updates**, and **workflow tests** are mandatory for every task.
* Documentation is part of your job—**keep all docs, navigation, and references up to date**.

---


# Style Guide: Django + HTMX + Bootstrap + Custom HTML Forms

---

## **1. General Principles**

* **Clarity over cleverness:** Write code and markup that is immediately understandable by your teammates.
* **DRY, but not at the expense of readability:** Reuse code/components, but avoid abstraction until patterns are obvious.
* **Explicit is better than implicit:** Be clear about permissions, logic, and intentions in both code and templates.
* **Security by default:** Validate/clean all input, never trust user data, and always enforce permission checks.
* **Consistency is king:** Use the same naming, formatting, and conventions throughout the codebase.

---

## **2. Project & App Structure**

* **Organize Django apps by domain/business context** (e.g., `sales`, `inventory`, `users`).
* **Separate templates per app** in `/templates/{app_name}/`.
* **Static files** (CSS, JS) go in `/static/{app_name}/`.
* **Custom template tags/filters** should live in `{app_name}/templatetags/`.

---

## **3. Models**

* **Use singular class names:** `Customer`, not `Customers`.
* **Add `verbose_name` and `help_text` for all fields** for admin and self-documenting code.
* **Always use explicit `on_delete` in ForeignKey/OneToOne.**
* **Add meaningful `__str__` methods.**
* **Keep model logic (“fat models, skinny views”):** Put business logic methods on the model.

---

## **4. Views & Business Logic**

* **Prefer Class-Based Views for standard CRUD** (but use Function-Based Views for custom workflows).
* **No fat views:** All non-trivial logic should go into services or the model.
* **Every view must check permissions.**
  Use decorators or mixins—never assume user permissions!
* **Partial updates via HTMX:** Return only what’s needed (`hx-target`, `hx-swap`).
* **Handle all POST/PUT actions with CSRF protection.**
* **Return clear success/error messages, especially for AJAX/HTMX.**

---

## **5. Templates**

* **Always use Bootstrap classes for styling.**
  Use utility classes for spacing, color, etc.—no inline styles.
* **Organize base templates:**

  * `base.html`: Global layout, CSS/JS includes, nav/sidebar.
  * App-level bases: `sales/base_sales.html` (extends `base.html`).
* **Break forms into partials** (e.g., `_form.html`), so you can reuse for create/edit.
* **Keep HTML valid and accessible** (labels, aria attributes, required fields).
* **Use Django template language for logic, but keep it minimal.**
* **Keep forms clean:**

  * No Django `{{ form.as_p }}`.
  * Use `<form>` + hand-written `<input>`, `<select>`, `<textarea>`, etc.
  * Bootstrap classes for fields and error feedback.
* **HTMX snippets** should be minimal, self-contained, and not depend on unrelated JS.

---

## **6. Forms (Custom HTML Only!)**

* **Manual HTML:**

  * Always write out your forms manually.
  * Use `name` attributes matching your backend view.
  * Add `required`, `minlength`, `maxlength` where possible.
* **Validation:**

  * Frontend (HTML5 validation) for instant feedback.
  * Backend: Always validate in the view, never trust the browser!
  * Show errors inline, use Bootstrap’s `is-invalid`/`invalid-feedback`.
* **CSRF tokens:**

  * Always include `{% csrf_token %}` in POST forms.
* **Use proper field types:** (`type="email"`, `type="date"`, etc.)

---

## **7. HTMX Integration**

* **Progressive enhancement:** The page should work without HTMX, but be better with it.
* **Keep HTMX targets small:**

  * Only swap the part of the page that needs updating.
* **Clear indicators for loading/success/error:**

  * Use Bootstrap spinners, alerts, or toasts.
* **Return only what is needed for the swap.**
* **Never mix unrelated logic in HTMX endpoints.**

  * One responsibility per endpoint/snippet.
* **Use hx-headers for custom feedback/messages if needed.**

---

## **8. Navigation**

* **Sidebar/Menu must be updated for every new module or flow.**
* **Group items logically by domain and role.**
* **No “dead” links:** Remove or disable links to unimplemented features.
* **Use icons sparingly for clarity.**

---

## **9. Permissions & Security**

* **All views must enforce permissions.**
* **Never expose unauthorized data in API or templates.**
* **Document which roles can access each view/workflow.**
* **Always sanitize user input/output.**

---

## **10. Documentation & Comments**

* **Document everything:**

  * What workflows are implemented,
  * what each view does,
  * what parameters are accepted.
* **Docstrings for all models, views, and custom utility functions.**
* **Inline comments for non-obvious logic.**
* **Every workflow must be documented in `workflow.md`** (steps, permissions, API endpoints, navigation).
* **Update navigation and API docs with every change.**

---

## **11. Testing**

* **Backend:** Django TestCase for every CRUD/API endpoint, especially permission tests.
* **Frontend:**

  * Use Django’s LiveServerTestCase or Selenium/Cypress if needed for E2E.
  * Focus on user flows, not just form submission.
* **Mock user roles/permissions in tests.**
* **Tests should run on CI—required for merge.**

---

## **12. Code Formatting & Naming**

* **Use `snake_case` for variables, functions, templates.**
* **Use `PascalCase` for class names.**
* **Template names:** `{app}/{object}_{action}.html` (`sales/order_create.html`).
* **Static files:** `{app}/js/{feature}.js`, `{app}/css/{feature}.css` if custom.
* **No magic numbers/strings:**

  * Use constants or enums (e.g., for status codes, permissions).

---

## **13. Example Snippet: Custom Form + HTMX**

```html
<form hx-post="{% url 'sales_order_create' %}" hx-target="#order-list" class="needs-validation" novalidate>
  {% csrf_token %}
  <div class="mb-3">
    <label for="customer" class="form-label">Customer</label>
    <input type="text" class="form-control" id="customer" name="customer" required>
    <div class="invalid-feedback">Please enter a customer name.</div>
  </div>
  <!-- More fields here... -->
  <button type="submit" class="btn btn-primary">Create Order</button>
</form>
```

```python
# In your Django view
def sales_order_create(request):
    if request.method == "POST":
        customer = request.POST.get("customer")
        # Validate, check perms, save...
        # Return partial HTML (HTMX) or errors with 400 code if invalid
```

---

## **14. Additional Tips**

* **Keep template logic simple**—move complexity to Python.
* **Always prefer reusing partials and components over copy-pasting markup.**
* **All features must be accessible via navigation (no hidden URLs).**
* **Adopt a “show, don’t tell” demo-first mindset: after each feature, ensure anyone can find and use it via the UI.**

---

## **15. Code Reviews**

* **Every PR must be reviewed for clarity, security, and test coverage.**
* **Code must follow the style guide or justify deviations in the PR description.**
* **Docs and navigation updates are not optional.**

**Happy building, Agent!**
*(If you are reading this as a human developer, these principles apply to you too!)*

---
