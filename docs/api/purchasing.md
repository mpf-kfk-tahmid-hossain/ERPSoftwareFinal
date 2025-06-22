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
