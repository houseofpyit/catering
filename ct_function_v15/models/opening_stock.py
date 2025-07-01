from odoo import api, models, fields, _
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from datetime import datetime, date ,timedelta
from odoo.tools import html_escape

class HopOpeningStock(models.Model):
    _name = "hop.opening.stock"

    product_id = fields.Many2one('product.product', string='Product')
    date = fields.Date(string="Date",default=fields.Date.context_today)
    qty = fields.Float(string="Qty")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
    
