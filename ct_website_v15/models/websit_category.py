from odoo import api, models, fields

class websitcategory(models.Model):
    _name = "hop.websit.category"

    name = fields.Char(string="Name")
