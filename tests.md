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

* [x] **Required Field Validation:**
  When updating a user, if any required field is missing, a relevant validation error must be shown clearly on the screen.

#### **Remove All `hx-post` Usage**

* [x] **Audit All Templates for `hx-post`:**
  Check every Django template (especially supplier and user-related) to ensure `hx-post` is not used anywhere.
* [x] **Replace `hx-post` With Standard Django Forms/Buttons:**
  All actions previously using `hx-post` must be replaced with proper HTML forms and Django POST endpoints.
* [x] **Automated/Manual Check:**
  Implement a test or process to ensure no `hx-post` remains in the codebase.

#### **Supplier Add/Edit: Bank Selection via AJAX**

* [x] **Bank Field Uses AJAX Search:**
  The Add and Edit Supplier forms must allow users to search all existing banks with an AJAX-powered dropdown/search.
* [x] **Allow New Bank Entry:**
  If the desired bank is not found, users can type a new name and it will be saved as a new Bank record.
* [x] **Bank Field Usability Test:**
  Tests confirm that both searching and creating/selecting a new bank function as intended.

#### **General UI & Form Handling**

* [x] **Inline Action Layouts:**
  All supplier and user actions (e.g., edit, verify, discontinue) are laid out inline using Bootstrap flex utilities for proper alignment.
* [x] **Filter Form & Add Button Alignment:**
  In supplier list views, the filter form should be left-aligned, and the “Add Supplier” button should be right-aligned on the same row.

#### **Error & Success Feedback**

* [x] **Display Field-Level Validation Errors:**
  All form errors (e.g., missing required fields) must display at the relevant field in the UI.
* [x] **Show Success Messages:**
  Actions like adding, editing, or reactivating suppliers must display a clear success message.

---
### 📝 **Product Detail & Enhancement Checklist**

#### **Product Detail Page & Specs**

* [x] Product **Detail Page** exists for each product and is accessible from the product list.
* [x] Product detail page displays:
  * [x] **Product Name, SKU/Code**
  * [x] **Product Description** (main description field)
  * [x] **Product Photos** (gallery-style image viewer)
  * [x] **Amount of Inventory Present** (for this product)
  * [x] **Inventory per Warehouse** (if multi-location, shows quantity by warehouse)
  * [x] **Specs Section**:
    * [x] **Specs** stored as custom JSON key-value pairs.
    * [x] Specs can be grouped/categorized—user can define new categories, e.g., General, Technical, Warranty, Additional, Support, etc.
    * [x] Categories and spec keys are not fixed—user can add/remove/edit categories and keys as needed.

#### **Product Form Enhancements**

* [x] Product **Create/Edit Form**:
  * [x] **Specs** input allows adding/editing categories and custom fields as JSON (dynamic UI—add category, add field).
  * [x] Field for **main description**.
  * [x] **Photo upload** field(s) (multiple images, drag-and-drop or file picker).
  * [x] **Category assignment** (main category + optional subcategories if taxonomy is needed).
  * [x] **Warehouse selection** for initial inventory and ongoing adjustment.
  * [x] Form validation for required fields and specs completeness.

#### **Product Page Ecommerce Layout**

* [x] Product detail page layout resembles modern ecommerce style:
  * [x] **Image gallery** at top or side
  * [x] Main info (name, SKU, short description) prominent
  * [x] Specs displayed as **accordion** or **tabbed** sections by category
  * [x] Inventory numbers and per-warehouse info displayed clearly
  * [x] **Requisition button** (visible if user has permission) to create a purchase/stock requisition from this page

#### **Requisition Integration**

* [x] If user has **requisition permission**:
  * [x] **"Request/Requisition Product"** button is visible.
  * [x] Clicking opens a form/modal to create a requisition (quantity, warehouse, comments).
  * [x] Successful requisition shows confirmation and links back to product or requisition tracking.

#### **Product Search/List Enhancements**

* [x] Product list supports:
  * [x] **Image thumbnails**
  * [x] **Inventory column**
  * [x] **Quick view/preview** action (modal or inline)
  * [x] Search/filter by category, spec value, inventory level, etc.

---
