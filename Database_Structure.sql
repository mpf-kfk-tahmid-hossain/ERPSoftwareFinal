CREATE TABLE "company" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "code" varchar UNIQUE,
  "address" text
);

CREATE TABLE "account_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "tax_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "invoice_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "invoice_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "debit_credit_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "payment_method" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "fiscal_year" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "start_date" date,
  "end_date" date,
  "company_id" integer NOT NULL
);

CREATE TABLE "account" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "code" varchar UNIQUE,
  "account_type_id" integer NOT NULL,
  "parent_id" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "tax" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "rate" decimal,
  "tax_type_id" integer NOT NULL,
  "company_id" integer NOT NULL
);

CREATE TABLE "journal_entry" (
  "id" integer PRIMARY KEY,
  "date" date,
  "reference" varchar,
  "memo" text,
  "company_id" integer NOT NULL,
  "created_by" integer,
  "fiscal_year_id" integer
);

CREATE TABLE "journal_line" (
  "id" integer PRIMARY KEY,
  "journal_entry_id" integer NOT NULL,
  "account_id" integer NOT NULL,
  "amount" decimal,
  "debit_credit_type_id" integer NOT NULL,
  "description" varchar,
  "customer_id" integer,
  "supplier_id" integer
);

CREATE TABLE "invoice" (
  "id" integer PRIMARY KEY,
  "number" varchar UNIQUE,
  "date" date,
  "total" decimal,
  "invoice_type_id" integer NOT NULL,
  "invoice_status_id" integer NOT NULL,
  "customer_id" integer,
  "supplier_id" integer,
  "company_id" integer NOT NULL,
  "sales_order_id" integer,
  "purchase_order_id" integer
);

CREATE TABLE "payment" (
  "id" integer PRIMARY KEY,
  "amount" decimal,
  "date" date,
  "payment_method_id" integer NOT NULL,
  "reference" varchar,
  "invoice_id" integer NOT NULL,
  "customer_id" integer,
  "supplier_id" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "product_unit" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "product_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "stock_movement_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "inventory_adjustment_reason" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "warehouse" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "location" varchar,
  "company_id" integer NOT NULL
);

CREATE TABLE "product_category" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "parent_id" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "product" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "sku" varchar UNIQUE,
  "barcode" varchar,
  "product_type_id" integer NOT NULL,
  "unit_id" integer NOT NULL,
  "brand" varchar,
  "category_id" integer,
  "company_id" integer NOT NULL,
  "description" text
);

CREATE TABLE "stock_lot" (
  "id" integer PRIMARY KEY,
  "batch_number" varchar,
  "expiry_date" date,
  "qty" decimal,
  "product_id" integer NOT NULL,
  "warehouse_id" integer NOT NULL
);

CREATE TABLE "stock_movement" (
  "id" integer PRIMARY KEY,
  "product_id" integer NOT NULL,
  "warehouse_id" integer NOT NULL,
  "from_warehouse_id" integer,
  "to_warehouse_id" integer,
  "user_id" integer,
  "batch_id" integer,
  "quantity" decimal,
  "movement_type_id" integer NOT NULL,
  "date" timestamp,
  "reference" varchar
);

CREATE TABLE "inventory_adjustment" (
  "id" integer PRIMARY KEY,
  "product_id" integer NOT NULL,
  "warehouse_id" integer NOT NULL,
  "user_id" integer,
  "date" timestamp,
  "reason_id" integer NOT NULL,
  "qty" decimal,
  "notes" text
);

CREATE TABLE "users" (
  "id" integer PRIMARY KEY,
  "username" varchar UNIQUE,
  "email" varchar UNIQUE,
  "password" varchar,
  "first_name" varchar,
  "last_name" varchar,
  "is_active" boolean,
  "role" varchar,
  "created_at" timestamp,
  "company_id" integer NOT NULL,
  "department_id" integer,
  "is_staff" boolean,
  "is_superuser" boolean
);

CREATE TABLE "purchase_order_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "rfq_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "goods_receipt_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "supplier" (
  "id" integer PRIMARY KEY,
  "contact_info" text,
  "rating" decimal,
  "company_id" integer NOT NULL
);

CREATE TABLE "purchase_order" (
  "id" integer PRIMARY KEY,
  "order_number" varchar UNIQUE,
  "date" date,
  "status_id" integer NOT NULL,
  "total" decimal,
  "supplier_id" integer NOT NULL,
  "company_id" integer NOT NULL,
  "created_by" integer
);

CREATE TABLE "purchase_order_line" (
  "id" integer PRIMARY KEY,
  "purchase_order_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "batch_id" integer,
  "quantity" decimal,
  "unit_price" decimal,
  "subtotal" decimal
);

CREATE TABLE "rfq" (
  "id" integer PRIMARY KEY,
  "number" varchar UNIQUE,
  "date" date,
  "status_id" integer NOT NULL,
  "supplier_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "user_id" integer
);

CREATE TABLE "goods_receipt" (
  "id" integer PRIMARY KEY,
  "date" date,
  "reference" varchar,
  "qty_received" decimal,
  "status_id" integer NOT NULL,
  "purchase_order_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "warehouse_id" integer NOT NULL,
  "batch_id" integer
);

CREATE TABLE "customer_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "sales_order_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "quotation_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "delivery_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "return_order_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "return_order_reason" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "customer" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "contact_info" text,
  "type_id" integer NOT NULL,
  "company_id" integer NOT NULL
);

CREATE TABLE "sales_order" (
  "id" integer PRIMARY KEY,
  "order_number" varchar UNIQUE,
  "date" date,
  "status_id" integer NOT NULL,
  "total" decimal,
  "customer_id" integer NOT NULL,
  "company_id" integer NOT NULL,
  "created_by" integer
);

CREATE TABLE "sales_order_line" (
  "id" integer PRIMARY KEY,
  "sales_order_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "batch_id" integer,
  "quantity" decimal,
  "unit_price" decimal,
  "subtotal" decimal
);

CREATE TABLE "quotation" (
  "id" integer PRIMARY KEY,
  "number" varchar UNIQUE,
  "date" date,
  "status_id" integer NOT NULL,
  "validity" date,
  "customer_id" integer NOT NULL,
  "user_id" integer
);

CREATE TABLE "delivery" (
  "id" integer PRIMARY KEY,
  "shipment_number" varchar UNIQUE,
  "date" date,
  "status_id" integer NOT NULL,
  "sales_order_id" integer NOT NULL,
  "warehouse_id" integer NOT NULL,
  "user_id" integer
);

CREATE TABLE "return_order" (
  "id" integer PRIMARY KEY,
  "return_number" varchar UNIQUE,
  "date" date,
  "reason_id" integer NOT NULL,
  "status_id" integer NOT NULL,
  "sales_order_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "customer_id" integer NOT NULL,
  "warehouse_id" integer NOT NULL,
  "batch_id" integer
);

CREATE TABLE "lead_source" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "lead_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "opportunity_stage" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "activity_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "support_ticket_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "support_ticket_priority" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "lead" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "contact_info" text,
  "source_id" integer NOT NULL,
  "status_id" integer NOT NULL,
  "expected_value" decimal,
  "customer_id" integer,
  "assigned_to" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "opportunity" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "stage_id" integer NOT NULL,
  "value" decimal,
  "close_date" date,
  "lead_id" integer NOT NULL,
  "customer_id" integer,
  "assigned_to" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "activity" (
  "id" integer PRIMARY KEY,
  "activity_type_id" integer NOT NULL,
  "date" timestamp,
  "notes" text,
  "lead_id" integer,
  "opportunity_id" integer,
  "customer_id" integer,
  "user_id" integer
);

CREATE TABLE "support_ticket" (
  "id" integer PRIMARY KEY,
  "number" varchar UNIQUE,
  "status_id" integer NOT NULL,
  "description" text,
  "priority_id" integer NOT NULL,
  "customer_id" integer NOT NULL,
  "user_id" integer,
  "product_id" integer
);

CREATE TABLE "employee_position" (
  "id" integer PRIMARY KEY,
  "name" varchar UNIQUE
);

CREATE TABLE "attendance_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "leave_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "leave_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "recruitment_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "department" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "parent_id" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "employee" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "emp_code" varchar UNIQUE,
  "join_date" date,
  "contact_info" text,
  "department_id" integer,
  "position_id" integer,
  "salary" decimal,
  "company_id" integer NOT NULL,
  "manager_id" integer
);

CREATE TABLE "attendance" (
  "id" integer PRIMARY KEY,
  "date" date,
  "check_in" time,
  "check_out" time,
  "status_id" integer NOT NULL,
  "employee_id" integer NOT NULL,
  "entered_by" integer
);

CREATE TABLE "leave_request" (
  "id" integer PRIMARY KEY,
  "type_id" integer NOT NULL,
  "start_date" date,
  "end_date" date,
  "status_id" integer NOT NULL,
  "employee_id" integer NOT NULL,
  "approved_by" integer
);

CREATE TABLE "payroll" (
  "id" integer PRIMARY KEY,
  "period" varchar,
  "gross" decimal,
  "deductions" decimal,
  "net" decimal,
  "employee_id" integer NOT NULL,
  "company_id" integer NOT NULL
);

CREATE TABLE "recruitment" (
  "id" integer PRIMARY KEY,
  "position_id" integer NOT NULL,
  "status_id" integer NOT NULL,
  "applicant_name" varchar,
  "application_date" date,
  "department_id" integer,
  "employee_id" integer
);

CREATE TABLE "bom_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "work_order_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "production_batch_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "quality_check_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "quality_check_result" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "bom" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "version" varchar,
  "status_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "company_id" integer NOT NULL
);

CREATE TABLE "bom_line" (
  "id" integer PRIMARY KEY,
  "bom_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "quantity" decimal,
  "uom_id" integer NOT NULL
);

CREATE TABLE "work_order" (
  "id" integer PRIMARY KEY,
  "number" varchar UNIQUE,
  "status_id" integer NOT NULL,
  "planned_date" date,
  "qty" decimal,
  "bom_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "company_id" integer NOT NULL,
  "created_by" integer
);

CREATE TABLE "production_batch" (
  "id" integer PRIMARY KEY,
  "batch_number" varchar UNIQUE,
  "status_id" integer NOT NULL,
  "qty" decimal,
  "product_id" integer NOT NULL,
  "work_order_id" integer NOT NULL
);

CREATE TABLE "work_order_operation" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "sequence" integer,
  "workstation" varchar,
  "work_order_id" integer NOT NULL,
  "product_id" integer NOT NULL,
  "operator_id" integer
);

CREATE TABLE "quality_check" (
  "id" integer PRIMARY KEY,
  "type_id" integer NOT NULL,
  "result_id" integer NOT NULL,
  "notes" text,
  "date" timestamp,
  "product_id" integer NOT NULL,
  "work_order_id" integer NOT NULL,
  "user_id" integer
);

CREATE TABLE "shipment_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "logistics_partner" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "contact_info" text,
  "company_id" integer NOT NULL
);

CREATE TABLE "shipment" (
  "id" integer PRIMARY KEY,
  "number" varchar UNIQUE,
  "status_id" integer NOT NULL,
  "dispatch_date" date,
  "delivery_date" date,
  "logistics_partner_id" integer NOT NULL,
  "sales_order_id" integer,
  "purchase_order_id" integer,
  "warehouse_id" integer NOT NULL
);

CREATE TABLE "delivery_route" (
  "id" integer PRIMARY KEY,
  "route_name" varchar,
  "sequence" integer,
  "shipment_id" integer NOT NULL,
  "logistics_partner_id" integer NOT NULL
);

CREATE TABLE "demand_forecast" (
  "id" integer PRIMARY KEY,
  "product_id" integer NOT NULL,
  "period" varchar,
  "forecast_qty" decimal,
  "warehouse_id" integer NOT NULL,
  "company_id" integer NOT NULL
);

CREATE TABLE "project_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "task_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "task_priority" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "project" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "code" varchar UNIQUE,
  "start_date" date,
  "end_date" date,
  "status_id" integer NOT NULL,
  "customer_id" integer,
  "company_id" integer NOT NULL,
  "manager_employee_id" integer,
  "manager_user_id" integer
);

CREATE TABLE "task" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "description" text,
  "status_id" integer NOT NULL,
  "due_date" date,
  "priority_id" integer NOT NULL,
  "project_id" integer NOT NULL,
  "assigned_to_employee_id" integer,
  "assigned_to_user_id" integer,
  "parent_task_id" integer
);

CREATE TABLE "timesheet" (
  "id" integer PRIMARY KEY,
  "date" date,
  "hours" decimal,
  "notes" text,
  "task_id" integer NOT NULL,
  "employee_id" integer,
  "project_id" integer NOT NULL
);

CREATE TABLE "expense" (
  "id" integer PRIMARY KEY,
  "description" text,
  "amount" decimal,
  "date" date,
  "project_id" integer NOT NULL,
  "employee_id" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "asset_category" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "depreciation_rate" decimal,
  "company_id" integer NOT NULL,
  "parent_id" integer
);

CREATE TABLE "asset" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "serial_no" varchar UNIQUE,
  "purchase_date" date,
  "value" decimal,
  "location" varchar,
  "category_id" integer NOT NULL,
  "company_id" integer NOT NULL,
  "assigned_to_employee_id" integer,
  "assigned_to_department_id" integer
);

CREATE TABLE "maintenance_schedule" (
  "id" integer PRIMARY KEY,
  "asset_id" integer NOT NULL,
  "schedule_date" date,
  "type" varchar,
  "notes" text,
  "responsible_user_id" integer
);

CREATE TABLE "asset_transfer" (
  "id" integer PRIMARY KEY,
  "asset_id" integer NOT NULL,
  "date" date,
  "from_location" varchar,
  "to_location" varchar,
  "user_id" integer,
  "department_id" integer
);

CREATE TABLE "report_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "report" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "type_id" integer NOT NULL,
  "created_on" timestamp,
  "filters" jsonb,
  "user_id" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "kpi" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "value" decimal,
  "target" decimal,
  "date" date,
  "company_id" integer NOT NULL,
  "department_id" integer,
  "user_id" integer
);

CREATE TABLE "dashboard" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "layout_config" jsonb,
  "user_id" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "document_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "folder" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "parent_id" integer,
  "company_id" integer NOT NULL
);

CREATE TABLE "document" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "file" varchar,
  "version" varchar,
  "upload_date" timestamp,
  "status_id" integer NOT NULL,
  "uploaded_by" integer,
  "folder_id" integer,
  "content_type_id" integer,
  "object_id" integer
);

CREATE TABLE "django_content_type" (
  "id" integer PRIMARY KEY,
  "app_label" varchar,
  "model" varchar
);

CREATE TABLE "audit_action_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "compliance_check_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "compliance_result_type" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "audit_log" (
  "id" integer PRIMARY KEY,
  "action_type_id" integer NOT NULL,
  "timestamp" timestamp,
  "user_id" integer,
  "company_id" integer NOT NULL,
  "changes" jsonb,
  "remarks" text,
  "content_type_id" integer,
  "object_id" integer
);

CREATE TABLE "compliance_check" (
  "id" integer PRIMARY KEY,
  "check_type_id" integer NOT NULL,
  "result_type_id" integer NOT NULL,
  "checked_on" timestamp,
  "user_id" integer,
  "department_id" integer,
  "company_id" integer NOT NULL,
  "content_type_id" integer,
  "object_id" integer
);

CREATE TABLE "api_key_permission" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "integration_status" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "sync_direction" (
  "id" integer PRIMARY KEY,
  "code" varchar UNIQUE,
  "name" varchar
);

CREATE TABLE "api_key" (
  "id" integer PRIMARY KEY,
  "key" varchar UNIQUE,
  "issued_to" integer NOT NULL,
  "company_id" integer NOT NULL,
  "expiry_date" timestamp,
  "created_at" timestamp
);

CREATE TABLE "api_key_permission_link" (
  "id" integer PRIMARY KEY,
  "api_key_id" integer NOT NULL,
  "permission_id" integer NOT NULL
);

CREATE TABLE "integration_config" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "endpoint" varchar,
  "status_id" integer NOT NULL,
  "config" jsonb,
  "company_id" integer NOT NULL,
  "user_id" integer,
  "created_at" timestamp
);

CREATE TABLE "external_sync_log" (
  "id" integer PRIMARY KEY,
  "integration_id" integer NOT NULL,
  "user_id" integer,
  "company_id" integer NOT NULL,
  "sync_time" timestamp,
  "status_id" integer NOT NULL,
  "direction_id" integer NOT NULL,
  "data_snapshot" jsonb
);

CREATE TABLE "role" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "description" text,
  "company_id" integer NOT NULL
);

CREATE TABLE "permission" (
  "id" integer PRIMARY KEY,
  "codename" varchar UNIQUE,
  "description" text
);

CREATE TABLE "user_role" (
  "id" integer PRIMARY KEY,
  "user_id" integer NOT NULL,
  "role_id" integer NOT NULL,
  "company_id" integer NOT NULL,
  "start_date" date,
  "end_date" date
);

CREATE TABLE "role_permission_link" (
  "id" integer PRIMARY KEY,
  "role_id" integer NOT NULL,
  "permission_id" integer NOT NULL
);

CREATE TABLE "session" (
  "id" integer PRIMARY KEY,
  "session_key" varchar UNIQUE,
  "user_id" integer NOT NULL,
  "login_time" timestamp,
  "expiry" timestamp
);

CREATE TABLE "audit_trail" (
  "id" integer PRIMARY KEY,
  "action_type_id" integer NOT NULL,
  "timestamp" timestamp,
  "remarks" text,
  "user_id" integer,
  "company_id" integer,
  "content_type_id" integer,
  "object_id" integer
);

COMMENT ON TABLE "django_content_type" IS 'This table is auto-managed by Django and is used for generic relationships (GenericForeignKey). Each row identifies a model in the project by app label and model name.';

ALTER TABLE "fiscal_year" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "account" ADD FOREIGN KEY ("account_type_id") REFERENCES "account_type" ("id");

ALTER TABLE "account" ADD FOREIGN KEY ("parent_id") REFERENCES "account" ("id");

ALTER TABLE "account" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "tax" ADD FOREIGN KEY ("tax_type_id") REFERENCES "tax_type" ("id");

ALTER TABLE "tax" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "journal_entry" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "journal_entry" ADD FOREIGN KEY ("fiscal_year_id") REFERENCES "fiscal_year" ("id");

ALTER TABLE "journal_line" ADD FOREIGN KEY ("journal_entry_id") REFERENCES "journal_entry" ("id");

ALTER TABLE "journal_line" ADD FOREIGN KEY ("account_id") REFERENCES "account" ("id");

ALTER TABLE "journal_line" ADD FOREIGN KEY ("debit_credit_type_id") REFERENCES "debit_credit_type" ("id");

ALTER TABLE "journal_line" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "journal_line" ADD FOREIGN KEY ("supplier_id") REFERENCES "supplier" ("id");

ALTER TABLE "invoice" ADD FOREIGN KEY ("invoice_type_id") REFERENCES "invoice_type" ("id");

ALTER TABLE "invoice" ADD FOREIGN KEY ("invoice_status_id") REFERENCES "invoice_status" ("id");

ALTER TABLE "invoice" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "invoice" ADD FOREIGN KEY ("supplier_id") REFERENCES "supplier" ("id");

ALTER TABLE "invoice" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "invoice" ADD FOREIGN KEY ("sales_order_id") REFERENCES "sales_order" ("id");

ALTER TABLE "invoice" ADD FOREIGN KEY ("purchase_order_id") REFERENCES "purchase_order" ("id");

ALTER TABLE "payment" ADD FOREIGN KEY ("payment_method_id") REFERENCES "payment_method" ("id");

ALTER TABLE "payment" ADD FOREIGN KEY ("invoice_id") REFERENCES "invoice" ("id");

ALTER TABLE "payment" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "payment" ADD FOREIGN KEY ("supplier_id") REFERENCES "supplier" ("id");

ALTER TABLE "payment" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "warehouse" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "product_category" ADD FOREIGN KEY ("parent_id") REFERENCES "product_category" ("id");

ALTER TABLE "product_category" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "product" ADD FOREIGN KEY ("product_type_id") REFERENCES "product_type" ("id");

ALTER TABLE "product" ADD FOREIGN KEY ("unit_id") REFERENCES "product_unit" ("id");

ALTER TABLE "product" ADD FOREIGN KEY ("category_id") REFERENCES "product_category" ("id");

ALTER TABLE "product" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "stock_lot" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "stock_lot" ADD FOREIGN KEY ("warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "stock_movement" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "stock_movement" ADD FOREIGN KEY ("warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "stock_movement" ADD FOREIGN KEY ("from_warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "stock_movement" ADD FOREIGN KEY ("to_warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "stock_movement" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "stock_movement" ADD FOREIGN KEY ("batch_id") REFERENCES "stock_lot" ("id");

ALTER TABLE "stock_movement" ADD FOREIGN KEY ("movement_type_id") REFERENCES "stock_movement_type" ("id");

ALTER TABLE "inventory_adjustment" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "inventory_adjustment" ADD FOREIGN KEY ("warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "inventory_adjustment" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "inventory_adjustment" ADD FOREIGN KEY ("reason_id") REFERENCES "inventory_adjustment_reason" ("id");

ALTER TABLE "payment" ADD FOREIGN KEY ("supplier_id") REFERENCES "company" ("id");

ALTER TABLE "supplier" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "purchase_order" ADD FOREIGN KEY ("status_id") REFERENCES "purchase_order_status" ("id");

ALTER TABLE "purchase_order" ADD FOREIGN KEY ("supplier_id") REFERENCES "supplier" ("id");

ALTER TABLE "purchase_order" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "purchase_order" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "purchase_order_line" ADD FOREIGN KEY ("purchase_order_id") REFERENCES "purchase_order" ("id");

ALTER TABLE "purchase_order_line" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "purchase_order_line" ADD FOREIGN KEY ("batch_id") REFERENCES "stock_lot" ("id");

ALTER TABLE "rfq" ADD FOREIGN KEY ("status_id") REFERENCES "rfq_status" ("id");

ALTER TABLE "rfq" ADD FOREIGN KEY ("supplier_id") REFERENCES "supplier" ("id");

ALTER TABLE "rfq" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "rfq" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "goods_receipt" ADD FOREIGN KEY ("status_id") REFERENCES "goods_receipt_status" ("id");

ALTER TABLE "goods_receipt" ADD FOREIGN KEY ("purchase_order_id") REFERENCES "purchase_order" ("id");

ALTER TABLE "goods_receipt" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "goods_receipt" ADD FOREIGN KEY ("warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "goods_receipt" ADD FOREIGN KEY ("batch_id") REFERENCES "stock_lot" ("id");

ALTER TABLE "customer" ADD FOREIGN KEY ("type_id") REFERENCES "customer_type" ("id");

ALTER TABLE "customer" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "sales_order" ADD FOREIGN KEY ("status_id") REFERENCES "sales_order_status" ("id");

ALTER TABLE "sales_order" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "sales_order" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "sales_order" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "sales_order_line" ADD FOREIGN KEY ("sales_order_id") REFERENCES "sales_order" ("id");

ALTER TABLE "sales_order_line" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "sales_order_line" ADD FOREIGN KEY ("batch_id") REFERENCES "stock_lot" ("id");

ALTER TABLE "quotation" ADD FOREIGN KEY ("status_id") REFERENCES "quotation_status" ("id");

ALTER TABLE "quotation" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "quotation" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "delivery" ADD FOREIGN KEY ("status_id") REFERENCES "delivery_status" ("id");

ALTER TABLE "delivery" ADD FOREIGN KEY ("sales_order_id") REFERENCES "sales_order" ("id");

ALTER TABLE "delivery" ADD FOREIGN KEY ("warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "delivery" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "return_order" ADD FOREIGN KEY ("reason_id") REFERENCES "return_order_reason" ("id");

ALTER TABLE "return_order" ADD FOREIGN KEY ("status_id") REFERENCES "return_order_status" ("id");

ALTER TABLE "return_order" ADD FOREIGN KEY ("sales_order_id") REFERENCES "sales_order" ("id");

ALTER TABLE "return_order" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "return_order" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "return_order" ADD FOREIGN KEY ("warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "return_order" ADD FOREIGN KEY ("batch_id") REFERENCES "stock_lot" ("id");

ALTER TABLE "lead" ADD FOREIGN KEY ("source_id") REFERENCES "lead_source" ("id");

ALTER TABLE "lead" ADD FOREIGN KEY ("status_id") REFERENCES "lead_status" ("id");

ALTER TABLE "lead" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "lead" ADD FOREIGN KEY ("assigned_to") REFERENCES "users" ("id");

ALTER TABLE "lead" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "opportunity" ADD FOREIGN KEY ("stage_id") REFERENCES "opportunity_stage" ("id");

ALTER TABLE "opportunity" ADD FOREIGN KEY ("lead_id") REFERENCES "lead" ("id");

ALTER TABLE "opportunity" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "opportunity" ADD FOREIGN KEY ("assigned_to") REFERENCES "users" ("id");

ALTER TABLE "opportunity" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "activity" ADD FOREIGN KEY ("activity_type_id") REFERENCES "activity_type" ("id");

ALTER TABLE "activity" ADD FOREIGN KEY ("lead_id") REFERENCES "lead" ("id");

ALTER TABLE "activity" ADD FOREIGN KEY ("opportunity_id") REFERENCES "opportunity" ("id");

ALTER TABLE "activity" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "activity" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "support_ticket" ADD FOREIGN KEY ("status_id") REFERENCES "support_ticket_status" ("id");

ALTER TABLE "support_ticket" ADD FOREIGN KEY ("priority_id") REFERENCES "support_ticket_priority" ("id");

ALTER TABLE "support_ticket" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "support_ticket" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "support_ticket" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "department" ADD FOREIGN KEY ("parent_id") REFERENCES "department" ("id");

ALTER TABLE "department" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "employee" ADD FOREIGN KEY ("department_id") REFERENCES "department" ("id");

ALTER TABLE "employee" ADD FOREIGN KEY ("position_id") REFERENCES "employee_position" ("id");

ALTER TABLE "employee" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "employee" ADD FOREIGN KEY ("manager_id") REFERENCES "employee" ("id");

ALTER TABLE "attendance" ADD FOREIGN KEY ("status_id") REFERENCES "attendance_status" ("id");

ALTER TABLE "attendance" ADD FOREIGN KEY ("employee_id") REFERENCES "employee" ("id");

ALTER TABLE "attendance" ADD FOREIGN KEY ("entered_by") REFERENCES "users" ("id");

ALTER TABLE "leave_request" ADD FOREIGN KEY ("type_id") REFERENCES "leave_type" ("id");

ALTER TABLE "leave_request" ADD FOREIGN KEY ("status_id") REFERENCES "leave_status" ("id");

ALTER TABLE "leave_request" ADD FOREIGN KEY ("employee_id") REFERENCES "employee" ("id");

ALTER TABLE "leave_request" ADD FOREIGN KEY ("approved_by") REFERENCES "users" ("id");

ALTER TABLE "payroll" ADD FOREIGN KEY ("employee_id") REFERENCES "employee" ("id");

ALTER TABLE "payroll" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "recruitment" ADD FOREIGN KEY ("position_id") REFERENCES "employee_position" ("id");

ALTER TABLE "recruitment" ADD FOREIGN KEY ("status_id") REFERENCES "recruitment_status" ("id");

ALTER TABLE "recruitment" ADD FOREIGN KEY ("department_id") REFERENCES "department" ("id");

ALTER TABLE "recruitment" ADD FOREIGN KEY ("employee_id") REFERENCES "employee" ("id");

ALTER TABLE "bom" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "bom" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "bom_line" ADD FOREIGN KEY ("bom_id") REFERENCES "bom" ("id");

ALTER TABLE "bom_line" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "bom_line" ADD FOREIGN KEY ("uom_id") REFERENCES "product_unit" ("id");

ALTER TABLE "work_order" ADD FOREIGN KEY ("status_id") REFERENCES "work_order_status" ("id");

ALTER TABLE "work_order" ADD FOREIGN KEY ("bom_id") REFERENCES "bom" ("id");

ALTER TABLE "work_order" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "work_order" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "work_order" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "production_batch" ADD FOREIGN KEY ("status_id") REFERENCES "production_batch_status" ("id");

ALTER TABLE "production_batch" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "production_batch" ADD FOREIGN KEY ("work_order_id") REFERENCES "work_order" ("id");

ALTER TABLE "work_order_operation" ADD FOREIGN KEY ("work_order_id") REFERENCES "work_order" ("id");

ALTER TABLE "work_order_operation" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "work_order_operation" ADD FOREIGN KEY ("operator_id") REFERENCES "users" ("id");

ALTER TABLE "quality_check" ADD FOREIGN KEY ("type_id") REFERENCES "quality_check_type" ("id");

ALTER TABLE "quality_check" ADD FOREIGN KEY ("result_id") REFERENCES "quality_check_result" ("id");

ALTER TABLE "quality_check" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "quality_check" ADD FOREIGN KEY ("work_order_id") REFERENCES "work_order" ("id");

ALTER TABLE "quality_check" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "bom" ADD FOREIGN KEY ("status_id") REFERENCES "bom_status" ("id");

ALTER TABLE "logistics_partner" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "shipment" ADD FOREIGN KEY ("status_id") REFERENCES "shipment_status" ("id");

ALTER TABLE "shipment" ADD FOREIGN KEY ("logistics_partner_id") REFERENCES "logistics_partner" ("id");

ALTER TABLE "shipment" ADD FOREIGN KEY ("sales_order_id") REFERENCES "sales_order" ("id");

ALTER TABLE "shipment" ADD FOREIGN KEY ("purchase_order_id") REFERENCES "purchase_order" ("id");

ALTER TABLE "shipment" ADD FOREIGN KEY ("warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "delivery_route" ADD FOREIGN KEY ("shipment_id") REFERENCES "shipment" ("id");

ALTER TABLE "delivery_route" ADD FOREIGN KEY ("logistics_partner_id") REFERENCES "logistics_partner" ("id");

ALTER TABLE "demand_forecast" ADD FOREIGN KEY ("product_id") REFERENCES "product" ("id");

ALTER TABLE "demand_forecast" ADD FOREIGN KEY ("warehouse_id") REFERENCES "warehouse" ("id");

ALTER TABLE "demand_forecast" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "project" ADD FOREIGN KEY ("status_id") REFERENCES "project_status" ("id");

ALTER TABLE "project" ADD FOREIGN KEY ("customer_id") REFERENCES "customer" ("id");

ALTER TABLE "project" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "project" ADD FOREIGN KEY ("manager_employee_id") REFERENCES "employee" ("id");

ALTER TABLE "project" ADD FOREIGN KEY ("manager_user_id") REFERENCES "users" ("id");

ALTER TABLE "task" ADD FOREIGN KEY ("status_id") REFERENCES "task_status" ("id");

ALTER TABLE "task" ADD FOREIGN KEY ("priority_id") REFERENCES "task_priority" ("id");

ALTER TABLE "task" ADD FOREIGN KEY ("project_id") REFERENCES "project" ("id");

ALTER TABLE "task" ADD FOREIGN KEY ("assigned_to_employee_id") REFERENCES "employee" ("id");

ALTER TABLE "task" ADD FOREIGN KEY ("assigned_to_user_id") REFERENCES "users" ("id");

ALTER TABLE "task" ADD FOREIGN KEY ("parent_task_id") REFERENCES "task" ("id");

ALTER TABLE "timesheet" ADD FOREIGN KEY ("task_id") REFERENCES "task" ("id");

ALTER TABLE "timesheet" ADD FOREIGN KEY ("employee_id") REFERENCES "employee" ("id");

ALTER TABLE "timesheet" ADD FOREIGN KEY ("project_id") REFERENCES "project" ("id");

ALTER TABLE "expense" ADD FOREIGN KEY ("project_id") REFERENCES "project" ("id");

ALTER TABLE "expense" ADD FOREIGN KEY ("employee_id") REFERENCES "employee" ("id");

ALTER TABLE "expense" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "asset_category" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "asset_category" ADD FOREIGN KEY ("parent_id") REFERENCES "asset_category" ("id");

ALTER TABLE "asset" ADD FOREIGN KEY ("category_id") REFERENCES "asset_category" ("id");

ALTER TABLE "asset" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "asset" ADD FOREIGN KEY ("assigned_to_employee_id") REFERENCES "employee" ("id");

ALTER TABLE "asset" ADD FOREIGN KEY ("assigned_to_department_id") REFERENCES "department" ("id");

ALTER TABLE "maintenance_schedule" ADD FOREIGN KEY ("asset_id") REFERENCES "asset" ("id");

ALTER TABLE "maintenance_schedule" ADD FOREIGN KEY ("responsible_user_id") REFERENCES "users" ("id");

ALTER TABLE "asset_transfer" ADD FOREIGN KEY ("asset_id") REFERENCES "asset" ("id");

ALTER TABLE "asset_transfer" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "asset_transfer" ADD FOREIGN KEY ("department_id") REFERENCES "department" ("id");

ALTER TABLE "report" ADD FOREIGN KEY ("type_id") REFERENCES "report_type" ("id");

ALTER TABLE "report" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "report" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "kpi" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "kpi" ADD FOREIGN KEY ("department_id") REFERENCES "department" ("id");

ALTER TABLE "kpi" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "dashboard" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "dashboard" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "folder" ADD FOREIGN KEY ("parent_id") REFERENCES "folder" ("id");

ALTER TABLE "folder" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "document" ADD FOREIGN KEY ("status_id") REFERENCES "document_status" ("id");

ALTER TABLE "document" ADD FOREIGN KEY ("uploaded_by") REFERENCES "users" ("id");

ALTER TABLE "document" ADD FOREIGN KEY ("folder_id") REFERENCES "folder" ("id");

ALTER TABLE "document" ADD FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id");

ALTER TABLE "audit_log" ADD FOREIGN KEY ("action_type_id") REFERENCES "audit_action_type" ("id");

ALTER TABLE "audit_log" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "audit_log" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "audit_log" ADD FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id");

ALTER TABLE "compliance_check" ADD FOREIGN KEY ("check_type_id") REFERENCES "compliance_check_type" ("id");

ALTER TABLE "compliance_check" ADD FOREIGN KEY ("result_type_id") REFERENCES "compliance_result_type" ("id");

ALTER TABLE "compliance_check" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "compliance_check" ADD FOREIGN KEY ("department_id") REFERENCES "department" ("id");

ALTER TABLE "compliance_check" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "compliance_check" ADD FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id");

ALTER TABLE "api_key" ADD FOREIGN KEY ("issued_to") REFERENCES "users" ("id");

ALTER TABLE "api_key" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "api_key_permission_link" ADD FOREIGN KEY ("api_key_id") REFERENCES "api_key" ("id");

ALTER TABLE "api_key_permission_link" ADD FOREIGN KEY ("permission_id") REFERENCES "api_key_permission" ("id");

ALTER TABLE "integration_config" ADD FOREIGN KEY ("status_id") REFERENCES "integration_status" ("id");

ALTER TABLE "integration_config" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "integration_config" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "external_sync_log" ADD FOREIGN KEY ("integration_id") REFERENCES "integration_config" ("id");

ALTER TABLE "external_sync_log" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "external_sync_log" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "external_sync_log" ADD FOREIGN KEY ("status_id") REFERENCES "integration_status" ("id");

ALTER TABLE "external_sync_log" ADD FOREIGN KEY ("direction_id") REFERENCES "sync_direction" ("id");

ALTER TABLE "user_role" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "user_role" ADD FOREIGN KEY ("role_id") REFERENCES "role" ("id");

ALTER TABLE "user_role" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "role" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "role_permission_link" ADD FOREIGN KEY ("role_id") REFERENCES "role" ("id");

ALTER TABLE "role_permission_link" ADD FOREIGN KEY ("permission_id") REFERENCES "permission" ("id");

ALTER TABLE "session" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "users" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "users" ADD FOREIGN KEY ("department_id") REFERENCES "department" ("id");

ALTER TABLE "audit_trail" ADD FOREIGN KEY ("action_type_id") REFERENCES "audit_action_type" ("id");

ALTER TABLE "audit_trail" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "audit_trail" ADD FOREIGN KEY ("company_id") REFERENCES "company" ("id");

ALTER TABLE "audit_trail" ADD FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id");
