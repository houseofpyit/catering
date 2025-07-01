from odoo import api, models, fields

class CtHospitalityShift(models.Model):
    _name = "ct.hospitality.shift"
    _inherit = ['mail.thread']
    _description = "Hospitality Shift"

    name = fields.Char(string="Hospitality Shift",tracking=True)    