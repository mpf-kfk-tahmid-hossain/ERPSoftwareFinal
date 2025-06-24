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
  - **Notes:** `bank_name` is chosen using a Select2 dropdown that searches existing banks. Typing a new name will create a new bank record. The combination of bank name and SWIFT code must be unique and each supplier IBAN must be unique.
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

## Purchase Requisitions
- **List Requisitions**
  - **URL:** `/purchasing/requisitions/`
  - **Method:** `GET`
  - **Auth:** `view_purchaserequisition`
  - **Response:** HTML table of requisitions
- **Create Requisition**
  - **URL:** `/purchasing/requisitions/add/`
  - **Method:** `POST`
  - **Auth:** `add_purchaserequisition`
  - **Payload:** `number`, `product`, `quantity`, `specification`, `justification`
  - **Response:** Redirect to requisition detail
- **Approve/Rejection**
  - **URL:** `/purchasing/requisitions/<id>/approve/`
  - **Method:** `POST`
  - **Auth:** `approve_purchaserequisition`
  - **Payload:** `action` (`approve` or `reject`), `comment`
  - **Response:** Redirect to requisition detail

## Quotation Comparison & Selection
- **URL:** `/purchasing/quotations/compare/?product=<id>`
- **Method:** `GET`
- **Auth:** `add_purchaseorder`
- **Response:** HTML table of quotation lines with select buttons
- **Select Quotation**
  - **URL:** `/purchasing/quotations/<line_id>/select/`
  - **Method:** `POST`
  - **Auth:** `add_purchaseorder`
  - **Response:** Redirect to PO detail

## Purchase Order Acknowledgment
- **URL:** `/purchasing/purchase-orders/<id>/ack/`
- **Method:** `POST`
- **Auth:** `ack_purchaseorder`
- **Response:** Redirect to PO detail

## Supplier Invoices
- **List Invoices**
  - **URL:** `/purchasing/invoices/`
  - **Method:** `GET`
  - **Auth:** `view_supplierinvoice`
- **Upload Invoice**
  - **URL:** `/purchasing/invoices/add/`
  - **Method:** `POST`
  - **Auth:** `add_supplierinvoice`
  - **Payload:** `number`, `po`, `amount`, `file`
- **Three-Way Match**
  - **URL:** `/purchasing/invoices/<id>/match/`
  - **Method:** `GET`
  - **Auth:** `view_supplierinvoice`

## Payments
- **List Payments**
  - **URL:** `/purchasing/payments/`
  - **Method:** `GET`
  - **Auth:** `view_payment`
- **Create Payment**
  - **URL:** `/purchasing/payments/add/`
  - **Method:** `POST`
  - **Auth:** `add_payment`
  - **Payload:** `po`, `amount`, `method`
- **Approve Payment**
  - **URL:** `/purchasing/payments/<id>/approve/`
  - **Method:** `POST`
  - **Auth:** `approve_payment`
  - **Payload:** `action` (`approve`/`reject`), `comment`

## Supplier Evaluation
- **URL:** `/purchasing/suppliers/<id>/evaluate/`
- **Method:** `POST`
- **Auth:** `add_supplierevaluation`
- **Payload:** `score`, `comments`
- **Response:** Redirect to supplier detail
