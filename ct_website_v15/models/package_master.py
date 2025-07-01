from odoo import api, models, fields

class HopPackageMaster(models.Model):
    _name = "hop.package.master"
    _description = "Package"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name",tracking=True)

    package_line_ids = fields.One2many('hop.package.line','package_id',string="Package Line",tracking=True)

class HopPackageLine(models.Model):
    _name="hop.package.line"

    package_id = fields.Many2one('hop.package.master',string="Package",tracking=True)

    category_id = fields.Many2one('hop.websit.category',string="Category",tracking=True)
    item = fields.Char(string="Item Name",tracking=True)
    qty = fields.Char(string="Qty",tracking=True)