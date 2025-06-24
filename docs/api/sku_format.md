# SKU Format

The system uses the following pattern for automatically generated SKUs:

```
[COMPANYCODE]-[CATEGORYCODE]-[SERIAL]
```

- **COMPANYCODE**: A company identifier consisting of a four-character alphanumeric prefix and a numeric sequence (minimum two digits) which grows as new companies are created.
- **CATEGORYCODE**: 4+ character alphanumeric code generated for the leaf product category. Administrators may edit this code but it must remain unique per category.
- **SERIAL**: A numeric sequence padded to six digits for each company/category combination. The serial expands as needed beyond six digits.

Example: `ACME01-ELEC-000001`.
