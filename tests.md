### 📝 **Supplier Module Enhancements Checklist**

#### **Supplier Forms**

* [x] `SupplierForm` includes a **description** field for a brief company summary.
* [x] Add `UpdateSupplierInformationForm` to allow supplier data updates.

#### **Disconnection & Permissions**

* [x] Add "Discontinue Supplier" action/button in `SupplierDetailView`.
* [x] Permission check: Only users with `can_discontinue_supplier` can discontinue/reactivate.
* [x] Discontinued suppliers can be brought back (reactivated).

#### **Supplier Verification**

* [x] If **email** or **phone number** is changed:

  * [x] Set supplier as **unverified**.
  * [x] Trigger verification workflow.

#### **OTP Verification**

* [x] `SupplierDetailView` includes a **"Request OTP"** button.

  * [x] On click, show a **modal** for OTP input.
  * [x] Modal has:

    * [x] OTP field
    * [x] **Verify** button
    * [x] **Cancel** button to close modal without verifying

#### **Supplier List View**

* [x] Use `ExistingListView` for `SupplierListView`.
* [x] Add **Search** functionality (by name, contact, etc).
* [x] Add **Filter** options (by verification status, discontinued status, etc).
* [x] Include **Pagination** (page navigation).
* [x] Enable **Sorting** (by name, date added, etc).

---

### 📝 **Supplier Module & User Form Enhancement Checklist**

#### **User Update Validation**

* [ ] **Required Field Validation:**
  When updating a user, if any required field is missing, a relevant validation error must be shown clearly on the screen.

#### **Remove All `hx-post` Usage**

* [ ] **Audit All Templates for `hx-post`:**
  Check every Django template (especially supplier and user-related) to ensure `hx-post` is not used anywhere.
* [ ] **Replace `hx-post` With Standard Django Forms/Buttons:**
  All actions previously using `hx-post` must be replaced with proper HTML forms and Django POST endpoints.
* [ ] **Automated/Manual Check:**
  Implement a test or process to ensure no `hx-post` remains in the codebase.

#### **Supplier Add/Edit: Bank Selection via AJAX**

* [ ] **Bank Field Uses AJAX Search:**
  The Add and Edit Supplier forms must allow users to search all existing banks with an AJAX-powered dropdown/search.
* [ ] **Allow New Bank Entry:**
  If the desired bank is not found, users can type a new name and it will be saved as a new Bank record.
* [ ] **Bank Field Usability Test:**
  Tests confirm that both searching and creating/selecting a new bank function as intended.

#### **General UI & Form Handling**

* [ ] **Inline Action Layouts:**
  All supplier and user actions (e.g., edit, verify, discontinue) are laid out inline using Bootstrap flex utilities for proper alignment.
* [ ] **Filter Form & Add Button Alignment:**
  In supplier list views, the filter form should be left-aligned, and the “Add Supplier” button should be right-aligned on the same row.

#### **Error & Success Feedback**

* [ ] **Display Field-Level Validation Errors:**
  All form errors (e.g., missing required fields) must display at the relevant field in the UI.
* [ ] **Show Success Messages:**
  Actions like adding, editing, or reactivating suppliers must display a clear success message.

---