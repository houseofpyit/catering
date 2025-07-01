from odoo import api, models, fields


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    terms_condition = fields.Html("Terms & Condition")