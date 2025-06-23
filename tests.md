### 📝 **Supplier Module Enhancements Checklist**

#### **Supplier Forms**

* [ ] `SupplierForm` includes a **description** field for a brief company summary.
* [ ] Add `UpdateSupplierInformationForm` to allow supplier data updates.

#### **Disconnection & Permissions**

* [ ] Add "Discontinue Supplier" action/button in `SupplierDetailView`.
* [ ] Permission check: Only users with `can_discontinue_supplier` can discontinue/reactivate.
* [ ] Discontinued suppliers can be brought back (reactivated).

#### **Supplier Verification**

* [ ] If **email** or **phone number** is changed:

  * [ ] Set supplier as **unverified**.
  * [ ] Trigger verification workflow.

#### **OTP Verification**

* [ ] `SupplierDetailView` includes a **"Request OTP"** button.

  * [ ] On click, show a **modal** for OTP input.
  * [ ] Modal has:

    * [ ] OTP field
    * [ ] **Verify** button
    * [ ] **Cancel** button to close modal without verifying

#### **Supplier List View**

* [ ] Use `ExistingListView` for `SupplierListView`.
* [ ] Add **Search** functionality (by name, contact, etc).
* [ ] Add **Filter** options (by verification status, discontinued status, etc).
* [ ] Include **Pagination** (page navigation).
* [ ] Enable **Sorting** (by name, date added, etc).

---
