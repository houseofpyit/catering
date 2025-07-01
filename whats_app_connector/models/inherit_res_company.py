from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError,RedirectWarning


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    whatsapp_user_id = fields.Char(string="Whatsapp User ID")
    whatsapp_pwd = fields.Char(string="Whatsapp Password")