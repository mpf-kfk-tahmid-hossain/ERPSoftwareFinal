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
