from odoo import api, models, fields

class IssueReturn(models.TransientModel):
    _name='hop.issue.return'

    ir_line_ids = fields.One2many('hop.issue.return.line','ir_id',string="Issue Return Line")

    def action_save(self):
        in_fun  = self.env[self.env.context.get('active_model')].browse(self.env.context['active_ids'])
        print(self.env.context)
        list_line=[]
        for line in self.ir_line_ids:
            list_line.append(
                (0,0,{
                    'product_id':line.product_id.id,
                    'qty':line.qty,
                    'uom_id':line.uom_id.id,
                    'type':self.env.context.get('type',False),
                    'cost' : line.qty * line.product_id.standard_price
                })
            )
        in_fun.inventory_line_ids = list_line
    

class IssueReturnLine(models.TransientModel):
    _name='hop.issue.return.line'

    ir_id = fields.Many2one('hop.issue.return',string="Issue Return")
    product_id = fields.Many2one('product.product',string="Product")
    qty = fields.Float(string="Qty")
    uom_id = fields.Many2one('uom.uom',string="Uom")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id