from odoo import api, models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning

class InhouseBillWiz(models.TransientModel):
    _name='hop.in.house.bill.wiz'

    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    vender_ids = fields.Many2many('res.partner','vender_ids_in_house_ref', string='Order' )
    vender_id = fields.Many2one('res.partner',string="Vendor")
    order_ids = fields.Many2many('purchase.order','order_ids_in_house_ref', string='Order' )
    purchase_order_ids = fields.Many2many('purchase.order','hop_order_ids_in_house_ref', string='Purchase Order')
    date_wish_po = fields.Many2many('purchase.order','date_wish_po_in_house_ref', string=' Date Wish Order' )

    @api.onchange('from_date','to_date')
    def _onchange_from_date(self):
        if self.from_date and self.to_date:
            records = self.env['purchase.order'].search([('date','>=',self.from_date),('date','<=',self.to_date)])
            self.vender_ids = [(6,0, records.mapped('partner_id').ids)]
            pending_po = []
            for order in records:
                res = self.env['account.move.line'].search([('purchase_id','=',order.id),('move_id.state','!=','cancel')])
                if not res:
                    pending_po.append(order.id)
            self.date_wish_po = [(6,0, pending_po)]
        else:
            self.vender_ids = False
            self.date_wish_po = False
    @api.onchange('vender_id')
    def _onchange_vender_id(self):
        main_list=[] 
        if self.vender_id:
            records = self.env['account.move'].search([('partner_id','=',self.vender_id.id),('state','!=','cancel')])
            for record in records:
                for pur in record.invoice_line_ids.mapped('purchase_id').ids:
                    main_list.append(pur)
        self.purchase_order_ids = [(6,0, main_list)]

    def action_confirm(self):
    

        line_list=[]

        for line in self.order_ids:
            service_pr = self.env.ref('ct_function_v15.product1').id
            product_rec = self.env['product.product'].search([('product_tmpl_id','=',service_pr)])
            purchase_order = self.env['purchase.order'].search([('id','=',line.id)])

            line_list.append((0,0, {'purchase_id':purchase_order.id,
                                            'product_id': product_rec.id,
                                            'quantity': 1, 
                                            'price_unit': purchase_order.amount_total,
                                            'fun_date':purchase_order.date
                                }))
            # if line.product_uom_qty -line.qty_to_invoice > 0:
        
        if line_list:
     
            rec_id = self.env['account.move'].create(
                {
                    'partner_id': self.vender_id.id,
                    'po_type':'in_house',
                    'invoice_line_ids' : line_list,
                    'move_type':'in_invoice',
                    
                }) 
            
            return {
            'name': 'Your Form View',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': rec_id.id,
         
        }
    