from odoo import models, fields, _

class RmWithCategoryReport(models.Model):
    _name = 'hop.rm.with.category.report'

    function_id = fields.Many2one('hop.function',string="Function", ondelete='cascade')
    recipe_id = fields.Many2one('product.product', string='Itam Name')
    product_id = fields.Many2one('product.product', string='Raw Material')
    categ_id = fields.Many2one('product.category', string='Category')
    name=fields.Text('Raw Materials')
    uom = fields.Many2one('uom.uom',string="Uom")
    weight = fields.Float(string="Quantity",digits='Stock Weight')
    req_weight = fields.Float(string="Change in Quantity",digits='Stock Weight')
    cost_price = fields.Float(string="Cost Price")
    item_cost = fields.Float(string="Item Cost")
    vender_id = fields.Many2one('res.partner',string="Vendor",domain=[('is_vender','=',True)])
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

