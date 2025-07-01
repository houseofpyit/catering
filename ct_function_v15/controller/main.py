import logging
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
from odoo import http
from odoo.http import request
from odoo.http import content_disposition
import ast
from PyPDF2 import PdfFileReader, PdfFileMerger
from datetime import datetime, date ,timedelta
import zipfile
_logger = logging.getLogger(__name__)

class Binary(http.Controller):
    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self, tab_id, **kw):
        new_tab = ast.literal_eval(tab_id)
        attachment_ids = request.env['ir.attachment'].search([('id', 'in', new_tab)])
        file_dict = {}
        for attachment_id in attachment_ids:
            file_store = attachment_id.store_fname
            if file_store:
                file_name = attachment_id.name
                file_path = attachment_id._full_path(file_store)
                file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)

        # Create an in-memory PDF file
        bitIO = BytesIO()
        pdfMerge = PdfFileMerger()
        
        for filename in file_dict.values():
            pdfFile = open(filename['path'], 'rb')
            pdfReader = PdfFileReader(pdfFile)
            pdfMerge.append(pdfReader)
            pdfFile.close()
        
        pdfMerge.write(bitIO)  # Write the merged PDF to the BytesIO buffer
        
        return request.make_response(bitIO.getvalue(),
                                     headers=[('Content-Type', 'application/pdf'),
                                              ('Content-Disposition', content_disposition('MenuAndQuotation.pdf'))])

    @http.route('/web/binary/download_document_zip', type='http', auth="public")
    def download_document_zip(self, tab_id, **kw):
        new_tab = ast.literal_eval(tab_id)
        attachment_ids = request.env['ir.attachment'].search([('id', 'in', [int(value) for value in new_tab[0].split(',')])])
        file_dict = {}
        for attachment_id in attachment_ids:
            file_store = attachment_id.store_fname
            if file_store:
                file_name = attachment_id.name
                file_path = attachment_id._full_path(file_store)
                file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)
        zip_filename = "%s.zip" % new_tab[1]
        bitIO = BytesIO()
        zip_file = zipfile.ZipFile(bitIO, "w", zipfile.ZIP_DEFLATED)
        for file_info in file_dict.values():
            zip_file.write(file_info["path"], file_info["name"])
        zip_file.close()
        return request.make_response(bitIO.getvalue(),
                                     headers=[('Content-Type', 'application/x-zip-compressed'),
                                              ('Content-Disposition', content_disposition(zip_filename))])