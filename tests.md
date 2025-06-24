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

### 📝 **SKU Types, Company Code, & Category Code Autogeneration Implementation Tasks**

#### **1. SKU Pattern Definition & Documentation**

- [x] Document the final SKU format:
  `[COMPANYCODE]-[CATEGORYCODE]-[SERIAL]`
    - `COMPANYCODE`: 4 alphanumeric chars + minimum 2-digit sequence (auto-increment, grows as needed)
    - `CATEGORYCODE`: 4+ alphanumeric code, always from the **leaf (last-level) category** (auto-generated, unique, editable)
    - `SERIAL`: Zero-padded to 6 digits, expands as needed (no upper bound)
- [x] Place documentation of this pattern in the codebase/readme for all developers/users.

#### **2. Company Code Autogeneration & Migration**

- [x] Implement company creation logic that:
    - Generates a 4-character alphanumeric prefix (e.g., `ACME`, `X9F2`).
    - Appends a numeric sequence starting at `01`, incrementing for new companies using the same prefix (`ACME01`, `ACME02`, ..., `ACME99`, `ACME100`, ...).
    - Grows numeric part as required, with no upper limit.
- [x] Validate that each company receives a unique code system-wide.
- [x] **For all existing companies:**
    - Autogenerate and assign a company code using the above logic.
    - Store this code in the company record.
    - If conflicts, resolve using additional sequence digits.

#### **3. Category Code Autogeneration & Migration**

- [x] On category creation:
    - Auto-generate a unique alphanumeric code (4–8 chars) for each category.
    - Allow admin override (manual edit), but always enforce uniqueness.
    - Ensure code is visible and editable in the category admin page.
- [x] **For all existing categories:**
    - Backfill/auto-generate unique codes for every category.
    - For each product, ensure only the leaf (last-level) category code is used for SKU.
    - Validate and resolve code conflicts, using random/sequence suffixes if needed.

#### **4. SKU Autogeneration Logic & Migration**

- [x] On new product creation, generate SKU:
    - Format: `[COMPANYCODE]-[LEAFCATEGORYCODE]-[SERIAL]`
    - Serial number starts at `000001`, increments by 1 per leaf category per company.
    - Serial is left-padded to 6 digits, grows as needed.
- [x] Ensure SKU is unique within the company.
- [x] **For all existing products:**
    - Migrate to new SKU format by:
        - Linking each to its company code and leaf category code.
        - Assigning a unique serial per leaf category per company (based on created/ID order).
        - Logging all original SKUs for reference in a legacy SKU field.

#### **5. Product Form Handling**

- [x] Show the autogenerated SKU in the product form as read-only by default.
- [x] Provide an option for custom SKU entry (toggle/radio).
- [x] If custom SKU is entered, validate for uniqueness within the company and disable autogeneration for that product.

#### **6. Legacy/Imported SKU Support & Migration**

- [x] Allow manual entry of custom/legacy SKUs during bulk imports or product edits.
- [x] Validate all custom SKUs for uniqueness within the company.
- [x] Migrate all legacy SKUs to a new field (`legacy_sku`) for record-keeping; do not lose any historical reference.

#### **7. Serial Number Tracking (Serial-Tracked Products)**

- [x] Ensure SKU is assigned to the **product type**, not each serial-tracked unit.
- [x] Implement logic to associate multiple serial numbers (unique per unit) with a single SKU.

#### **8. Admin/Settings**

- [x] Add option in company/category admin/settings to view or regenerate company/category codes (admin-only, with audit log).
- [x] Place clear help text/tooltips for SKU pattern and code logic in admin and product forms.

#### **9. Testing & QA**

- [x] Write tests to verify:
    - Company code autogeneration (sequence, uniqueness, length expansion)
    - Category code autogeneration (uniqueness, handling for edge/leaf categories)
    - SKU autogeneration (format, serial padding/expansion, uniqueness)
    - Custom SKU override/entry (validity, uniqueness)
    - Serial tracking (SKUs for product type, serials for unique units)
    - Bulk import, migration, and edge cases (legacy data, high sequence numbers, long serials, etc)
- [x] For migration, run scripts/tests to ensure **every company, category, and product** receives a valid, unique code and SKU according to new rules.

---

**Agent Instructions:**  
- Review and confirm each task before implementation.
- Ensure all code, forms, and data migration scripts reflect the dynamic company code, leaf category code, and SKU logic.
- Validate ALL existing companies, categories, and products—**no record left unmigrated**.
- Mark each completed task `[x]` and link to migration results or documentation where possible.

### 📝 **Product Image Carousel, Modal Handling, and Modular Purchase Requisition Form – AI Implementation Tasks**

#### **1. Product Image Gallery/Carousel**

- [ ] Implement a **product image gallery** on the product detail page:
    - Main image with left/right navigation (carousel).
    - Thumbnail navigation below/side (click or scroll to select main image).
    - Responsive: adapts to mobile and desktop.
- [ ] On product list (grid/table), enable **quick view** via modal:
    - When opening modal, show product image carousel with thumbnails.
    - Ensure modal **can always be closed**—fix any issues where modal fails to close (e.g., overlay click, “X” icon, or Escape key).

#### **2. Image Add/Delete in Carousel (With Permissions)**

- [ ] In the image carousel (detail page and modal):
    - If the user has permission (`can_edit_product_images`):
        - Show an **Add Image** icon/button in the carousel.
        - Show a **Delete** (trash/bin) icon on each image.
        - Add confirmation step for delete.
    - Ensure all changes (add/delete) are reflected instantly (via AJAX/HTMX or frontend reload).

#### **3. Modular, Multi-Type Purchase Requisition Form**

- [ ] Update purchase requisition form to support **multiple request types**:
    - Product (inventory item)
    - Office supply
    - Service (e.g., “Renovate Signboard”, “Annual AC maintenance”)
    - Other (allow free-text “type” for any unlisted category)
- [ ] Allow **adding multiple line items** per requisition:
    - Each line can be any type: product, office supply, service, or custom.
    - Fields per line:
        - **Type** (dropdown: Product / Office Supply / Service / Other)
        - **Description** (dynamic: product auto-fills, service is free-text)
        - **Quantity** (optional/required based on type)
        - **Unit/Service Unit** (optional for services)
        - **Price Estimate** (optional)
        - **Attachment** (for service docs/quotes, optional)
- [ ] Modular, scalable design—easy to add new request types in future.

#### **4. General & Usability**

- [ ] On requisition form, show running summary and total.
- [ ] Add/remove lines easily (dynamic UI).
- [ ] Add help text/tooltips so users know they can request *products, services, or anything needed*.
- [ ] Validate permissions for add/delete actions, both frontend and backend.
- [ ] Test on desktop/mobile, with at least 20+ images per product, multiple request lines per requisition.

---

**AI Developer Instructions:**
- Use modern, user-friendly UI/UX for carousel and forms (consider libraries: Swiper.js, Bootstrap carousel, Slick, etc).
- Use proper permission checks for image editing.
- Ensure code is modular and maintainable (future proof).
- Mark each task `[x]` when completed; link to screenshots or code/PR.

