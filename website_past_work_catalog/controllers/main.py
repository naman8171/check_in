import csv
import io
import logging
from urllib import error, request

from odoo import http
from odoo.http import request as odoo_request

_logger = logging.getLogger(__name__)


class WebsitePastWorkController(http.Controller):
    EXPECTED_HEADERS = {
        "name",
        "short_description",
        "description",
        "sector",
        "work_type",
        "image_url",
        "pdf_url",
    }

    def _load_csv_rows(self):
        spreadsheet_url = (
            odoo_request.env["ir.config_parameter"].sudo().get_param(
                "website_past_work_catalog.spreadsheet_url"
            )
            or ""
        ).strip()
        if not spreadsheet_url:
            return []

        try:
            with request.urlopen(spreadsheet_url, timeout=12) as response:
                content = response.read().decode("utf-8-sig")
        except (error.URLError, ValueError, TimeoutError) as exc:
            _logger.warning("Could not load past work spreadsheet: %s", exc)
            return []

        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            return []

        normalized_headers = {header.strip().lower() for header in reader.fieldnames if header}
        if not self.EXPECTED_HEADERS.issubset(normalized_headers):
            _logger.warning(
                "Past work spreadsheet missing expected columns. Found: %s",
                sorted(normalized_headers),
            )

        rows = []
        for row in reader:
            normalized = {str(k).strip().lower(): (v or "").strip() for k, v in row.items() if k}
            if not normalized.get("name"):
                continue
            rows.append(
                {
                    "name": normalized.get("name", ""),
                    "short_description": normalized.get("short_description", ""),
                    "description": normalized.get("description", ""),
                    "sector": normalized.get("sector", "Uncategorised"),
                    "work_type": normalized.get("work_type", "Uncategorised"),
                    "image_url": normalized.get("image_url", ""),
                    "pdf_url": normalized.get("pdf_url", ""),
                }
            )
        return rows

    @http.route("/past-work", type="http", auth="public", website=True, sitemap=True)
    def past_work_page(self, **kwargs):
        return odoo_request.render("website_past_work_catalog.past_work_catalog_page")

    @http.route("/past-work/data", type="json", auth="public", website=True)
    def past_work_data(self):
        rows = self._load_csv_rows()
        sectors = sorted({row["sector"] for row in rows if row["sector"]})
        work_types = sorted({row["work_type"] for row in rows if row["work_type"]})
        return {
            "items": rows,
            "filters": {"sectors": sectors, "work_types": work_types},
        }
