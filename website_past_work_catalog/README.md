# Website Past Work Catalog

Adds a dynamic `/past-work` public page that reads project data from a spreadsheet CSV URL.

## Spreadsheet columns

Use these headers in the CSV:

- `name`
- `short_description`
- `description`
- `sector`
- `work_type`
- `image_url`
- `pdf_url`

## Configure

1. Install module `website_past_work_catalog`.
2. Go to Website settings and set **Past Work Spreadsheet CSV URL**.
3. Open `/past-work`.

The page loads projects dynamically and supports simultaneous filtering by Sector and Type of Work.
