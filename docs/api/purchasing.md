# Purchasing API

## Create Quotation Request
- **URL:** `/purchasing/quotations/add/`
- **Method:** `POST`
- **Auth:** `add_quotationrequest`
- **Payload:** `number`, `supplier`, `product`, `quantity`, `ean`, `serial_list`
- **Response:** Redirect to new PO form

## POS Scan
- **URL:** `/pos/scan/`
- **Method:** `POST`
- **Auth:** `view_product`
- **Payload:** `code` (EAN or serial)
- **Response:** HTML page with product name or error message

## Supplier Management
- **List Suppliers**
  - **URL:** `/purchasing/suppliers/`
  - **Method:** `GET`
  - **Auth:** `view_supplier`
  - **Response:** HTML table of suppliers

- **Create Supplier**
  - **URL:** `/purchasing/suppliers/add/`
  - **Method:** `POST`
  - **Auth:** `add_supplier`
  - **Payload:** `name`, `contact_person`, `phone`, `email`, `trade_license_number`, `trn`, `iban`, `bank_name` (existing or new), `swift_code`, `address`
  - **Notes:** `bank_name` is entered via a text field with suggestions from existing banks. The combination of bank name and SWIFT code must be unique and each supplier IBAN must be unique.
  - **Response:** Redirect to supplier detail page and sends OTP email

- **Verify Supplier**
  - **URL:** `/purchasing/suppliers/<id>/verify/`
  - **Method:** `POST`
  - **Auth:** `change_supplier`
  - **Payload:** `otp`
  - **Response:** Redirect to supplier detail

- **Toggle Connection**
  - **URL:** `/purchasing/suppliers/<id>/toggle/`
  - **Method:** `POST`
  - **Auth:** `can_discontinue_supplier`
  - **Response:** Redirect to supplier detail with updated status

- **Update Supplier**
  - **URL:** `/purchasing/suppliers/<id>/edit/`
  - **Method:** `POST`
  - **Auth:** `change_supplier`
  - **Payload:** same as create supplier
  - **Notes:** Changing phone or email marks supplier unverified and sends OTP
  - **Response:** Redirect to supplier detail

- **Request OTP**
  - **URL:** `/purchasing/suppliers/<id>/request-otp/`
  - **Method:** `POST`
  - **Auth:** `change_supplier`
  - **Response:** Partial HTML modal prompting for OTP entry
