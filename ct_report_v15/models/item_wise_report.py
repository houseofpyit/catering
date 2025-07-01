from odoo import models, fields, _
class HopItemWiseReport(models.Model):
    _name = "hop.item.wise.report"

    function_id = fields.Many2one('hop.function',string="Function")
    category_id = fields.Many2one('hop.recipes.category',string="Category")
    item_id = fields.Many2one('hop.recipes',string="Item Name")
    no_of_pax = fields.Integer(string="No Of Pax")
    per_qty = fields.Float(string="Per Head Qty")
    qty = fields.Float(string="Qty")
    uom = fields.Many2one('uom.uom',string="Uom")
    insider_id = fields.Many2one('res.partner',string="In-House",domain=[('is_vender','=',True)] )
    out_sider_id = fields.Many2one('res.partner',string="Out-Source",domain=[('is_vender','=',True)])
    cost = fields.Float(string="Cost")
    rate = fields.Float(string="Rate")
    instruction = fields.Char(string="Instruction")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)