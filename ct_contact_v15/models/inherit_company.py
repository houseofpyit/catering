from odoo import api, models, fields
from datetime import datetime, date ,timedelta


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    acc_name = fields.Char("Account Name")
    bank_name = fields.Char("Bank Name")
    acc_no = fields.Char("Account NO")
    ifsc_code = fields.Char("NEFT/IFSC CODE")
    branch = fields.Char("Branch")

    payment_condition = fields.Html("Payment Condition")

    pan_no = fields.Char("Pan No.")
    fssai_no = fields.Char("FSSAI No.")
    location = fields.Char("Location")
    manager_name_id = fields.Many2one('res.partner',string="Manager Name",domain=lambda self: "[('ct_category_id', '=', %s)]" % self.env.ref('ct_contact_v15.manager_category').id ,tracking=True)

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    is_date = fields.Boolean(string="Date", default=False)
    parent_company_id = fields.Many2one('res.company',string="Parent Company")
    children_company_id = fields.Many2one('res.company',string="Children Company")
    watermark_image = fields.Binary(string="Menu Print Watermark Image (Width=745,Height=1145)")
    watermark_image_name_tag = fields.Binary(string="Name Tag Print Watermark Image")

