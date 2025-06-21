# Inventory API

## List Warehouses
- **URL:** `/inventory/warehouses/`
- **Method:** `GET`
- **Auth:** Logged in users with `view_warehouse`
- **Response:** HTML table of warehouses for the user's company

## Add Warehouse
- **URL:** `/inventory/warehouses/add/`
- **Method:** `POST`
- **Auth:** `add_warehouse`
- **Payload:** `name`, `location`
- **Response:** Redirect to warehouse list

## List Categories
- **URL:** `/inventory/categories/`
- **Method:** `GET`
- **Auth:** `view_productcategory`

## Add Category
- **URL:** `/inventory/categories/add/`
- **Method:** `POST`
- **Auth:** `add_productcategory`
- **Payload:** `name`, `parent` (optional)
- **Response:** Redirect back to the add form
- **Notes:** Category names must be unique per company

### Quick Add Category
- **URL:** `/inventory/categories/quick-add/`
- **Method:** `POST`
- **Auth:** `add_productcategory`
- **Payload:** `name`, `parent` (optional)
- **Response:** HTML `<option>` for the new category (201)

## Category Tree
- **URL:** `/inventory/category-tree/`
- **Method:** `GET`
- **Auth:** `view_productcategory`
- **Response:** HTML tree view of categories

### Rename Category
- **URL:** `/inventory/categories/<id>/rename/`
- **Method:** `POST`
- **Auth:** `change_productcategory`
- **Payload:** `name`
- **Response:** Updated HTML snippet

### Move Category
- **URL:** `/inventory/categories/<id>/move/`
- **Method:** `POST`
- **Auth:** `change_productcategory`
- **Payload:** `parent` (empty for root)
- **Response:** `200 OK` or `400` if invalid (circular)

### Discontinue Category
- **URL:** `/inventory/categories/<id>/discontinue/`
- **Method:** `POST`
- **Auth:** `discontinue_productcategory`
- **Response:** `200 OK`

### Category Children
- **URL:** `/inventory/categories/children/`
- **Method:** `GET`
- **Auth:** `view_productcategory`
- **Params:** `parent` (optional category id), `level` (next level number)
- **Response:** HTML snippet with a select for child categories

### Quick Add Unit
- **URL:** `/inventory/units/quick-add/`
- **Method:** `POST`
- **Auth:** `add_productunit`
- **Payload:** `code`, `name`
- **Response:** HTML `<option>` for the new unit (201)

## List Products
- **URL:** `/inventory/products/`
- **Method:** `GET`
- **Auth:** `view_product`

## Add Product
- **URL:** `/inventory/products/add/`
- **Method:** `POST`
- **Auth:** `add_product`
- **Payload:** `name`, `sku`, `unit`, `category` (opt), `brand`, `barcode`, `description`

## Stock On Hand
- **URL:** `/inventory/stock-on-hand/`
- **Method:** `GET`
- **Auth:** `view_stock_on_hand`
- **Response:** Table of product quantities
