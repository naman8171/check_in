from odoo import models
import base64
import io

try:
    from PyPDF2 import PdfReader, PdfWriter
    NEW_VERSION = True
except ImportError:
    from PyPDF2 import PdfFileReader, PdfFileWriter
    NEW_VERSION = False


class ReportMerge(models.AbstractModel):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):

        # Only apply on final PDF generation
        if not res_ids:
            return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)

        pdf_content, content_type = super()._render_qweb_pdf(
            report_ref, res_ids=res_ids, data=data
        )

        # Apply merge ONLY to your specific report
        if report_ref != 'inom_technical_dossier.technical_dossier_report_template':
            return pdf_content, content_type

        params = self.env['ir.config_parameter'].sudo()
        first_pdf = params.get_param('inom_technical_dossier.first_pdf')
        second_pdf = params.get_param('inom_technical_dossier.second_pdf')
        last_pdf = params.get_param('inom_technical_dossier.last_pdf')

        if NEW_VERSION:
            writer = PdfWriter()
        else:
            writer = PdfFileWriter()

        # FIRST PDF
        if first_pdf:
            stream = io.BytesIO(base64.b64decode(first_pdf))
            reader = PdfReader(stream) if NEW_VERSION else PdfFileReader(stream)
            pages = reader.pages if NEW_VERSION else range(reader.getNumPages())
            for page in (pages if NEW_VERSION else [reader.getPage(i) for i in pages]):
                writer.add_page(page) if NEW_VERSION else writer.addPage(page)

        # SECOND PDF
        if second_pdf:
            stream = io.BytesIO(base64.b64decode(second_pdf))
            reader = PdfReader(stream) if NEW_VERSION else PdfFileReader(stream)
            pages = reader.pages if NEW_VERSION else range(reader.getNumPages())
            for page in (pages if NEW_VERSION else [reader.getPage(i) for i in pages]):
                writer.add_page(page) if NEW_VERSION else writer.addPage(page)

        # MAIN REPORT
        stream = io.BytesIO(pdf_content)
        reader = PdfReader(stream) if NEW_VERSION else PdfFileReader(stream)
        pages = reader.pages if NEW_VERSION else range(reader.getNumPages())
        for page in (pages if NEW_VERSION else [reader.getPage(i) for i in pages]):
            writer.add_page(page) if NEW_VERSION else writer.addPage(page)

        # LAST PDF
        if last_pdf:
            stream = io.BytesIO(base64.b64decode(last_pdf))
            reader = PdfReader(stream) if NEW_VERSION else PdfFileReader(stream)
            pages = reader.pages if NEW_VERSION else range(reader.getNumPages())
            for page in (pages if NEW_VERSION else [reader.getPage(i) for i in pages]):
                writer.add_page(page) if NEW_VERSION else writer.addPage(page)

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)

        return output.read(), content_type