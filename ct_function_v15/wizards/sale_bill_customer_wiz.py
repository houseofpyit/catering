from odoo import api, models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning

class SaleOrderWizard(models.TransientModel):
    _name='hop.multi.saleorder.wiz'

    customer_id = fields.Many2one('res.partner',string="Vendor")
    order_ids = fields.Many2many('sale.order','order_ids_saleorder_ref', string='Order' )
    sale_order_ids = fields.Many2many('sale.order','hop_order_ids_saleorder_ref', string='sale Order')
 
    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        main_list=[] 
        if self.customer_id:
            records = self.env['account.move'].search([('partner_id','=',self.customer_id.id),('state','!=','cancel')])
            for record in records:
                for pur in record.invoice_line_ids.mapped('sale_id').ids:
                    main_list.append(pur)
        self.sale_order_ids = [(6,0, main_list)]

    def action_confirm(self):
    

        line_list=[]

        for order in self.order_ids:
            for line in order.order_line:
                line_list.append((0,0, {'sale_id':order.id,
                                                'product_id': line.product_id.id,
                                                'name':line.name,
                                                'quantity': line.product_uom_qty, 
                                                'product_uom_id':line.product_uom.id,
                                                'price_unit': line.price_unit,
                                                'fun_date':order.fun_date,
                                                'tax_ids':[(6,0, line.tax_id.ids)]
                                    }))
        
        if line_list:
     
            rec_id = self.env['account.move'].create(
                {
                    'partner_id': self.customer_id.id,
                    'invoice_line_ids' : line_list,
                    'move_type':'out_invoice',
                    
                }) 
            
            return {
            'name': 'Your Form View',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': rec_id.id,
         
        }
    