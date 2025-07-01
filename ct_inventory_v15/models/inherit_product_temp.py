from odoo import api, models, fields
from datetime import datetime, date ,timedelta

class ProductTemplate(models.Model):
    _inherit = "product.template"

    utility_type = fields.Selection([('utensils','Utensils'),('disposable','Disposable'),('raw_materials','Raw Materials'),('service','Service')],string="Utility Type",tracking=True)
    is_utensils = fields.Boolean('Is Utensils', store="1")
    is_recipe = fields.Boolean('Is Recipe', store="1")
    utensils_type = fields.Selection([('ground','Ground'),('kitche','Kitchen'),('disposable','Disposable'),('decoration','Decoration')],string="Utensils Type",tracking=True)
    is_funcion = fields.Boolean('Is Function', store="1")
    is_service = fields.Boolean('Is Service', store="1")
    forecasted_purchase = fields.Float(string="Count",compute="compute_forecasted_purchase",readonly=True)
    forecasted_use = fields.Float(string="Count",compute="compute_forecasted_use",readonly=True)
    on_hand = fields.Float(string="Count",compute="compute_on_hand",readonly=True)
    vender_id = fields.Many2one('res.partner',string="Vendor",track_visibility='onchange',domain=[('is_vender','=',True)])
    @api.depends('forecasted_purchase')
    def compute_forecasted_purchase(self):
        for rec in self:
            pur_domain = [('state', '!=', 'cancel'),('partner_id','!=',self.env.ref('ct_inventory_v15.partner_godown').id)]
            purchase = self.env['purchase.order'].search(pur_domain)
            count = 0
            for order in purchase:
                count += sum(
                    line.product_qty
                    for line in order.order_line
                    if line.product_id.id == self.env['product.product'].search([('product_tmpl_id','=',rec.id)]).id
                )
            rec.forecasted_purchase = count + sum(self.env['hop.opening.stock'].search([('product_id','=',self.env['product.product'].search([('product_tmpl_id','=',rec.id)]).id)]).mapped('qty'))

    def open_forecasted_purchase(self):
        pass
        #    return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Forecasted Purchase',
        #     'view_mode': 'tree,form',
        #     'res_model': 'purchase.order',
        #     'domain': [('id','=', self.id)],
        #     'context': "{'create': False}"
        # }
    @api.depends('on_hand')
    def compute_on_hand(self):
        for res in self:
            product = self.env['product.product'].search([('product_tmpl_id','=',res.id)])
            date =  datetime.now()
            pur_domain = [('date', '<=', date), ('state', '!=', 'cancel'),('partner_id','!=',self.env.ref('ct_inventory_v15.partner_godown').id)]

            purchase = self.env['purchase.order'].search(pur_domain)
            pur_qty = 0
            for purchase_order in purchase:
                pur_qty += sum(
                    line.product_qty
                    for line in purchase_order.order_line
                    if line.product_id.id == product.id
                )
            fun_domain = [('date', '<=', date), ('stage', '!=', 'cancel')]
            fun_record = self.env['hop.function'].search(fun_domain)
            rm_record = self.env['hop.recipe.rm'].search([('function_id', 'in', fun_record.ids)])

            # rm_qty = sum(rm.rec_rm_ids.filtered(lambda l: l.product_id.id == product.id).mapped('weight') for rm in rm_record)
            rm_qty = 0
            issue_qty = 0
            return_qty = 0
            for rm in rm_record:
                rm_qty += sum(rm.rec_rm_ids.filtered(lambda l: l.product_id.id == product.id).mapped('weight'))
            for fun in fun_record:
                issue_qty += sum(fun.inventory_line_ids.filtered(lambda l: l.product_id.id == product.id and l.type == 'issue').mapped('qty'))
                return_qty += sum(fun.inventory_line_ids.filtered(lambda l: l.product_id.id == product.id and l.type == 'return').mapped('qty'))
            res.on_hand = pur_qty - rm_qty - issue_qty + return_qty + sum(self.env['hop.opening.stock'].search([('product_id','=',product.id)]).mapped('qty'))

    def open_on_hand(self):
        pass

    @api.depends('forecasted_use')
    def compute_forecasted_use(self):
        for rec in self:
            rec.forecasted_use =  sum(self.env['hop.rec_rm.line'].search([('product_id','=',self.env['product.product'].search([('product_tmpl_id','=',rec.id)]).id)]).mapped('weight'))+ sum(self.env['hop.inventory'].search([('type','=','issue'),('product_id','=',self.env['product.product'].search([('product_tmpl_id','=',rec.id)]).id)]).mapped('qty')) - sum(self.env['hop.inventory'].search([('type','=','return'),('product_id','=',self.env['product.product'].search([('product_tmpl_id','=',rec.id)]).id)]).mapped('qty'))
    def open_forecasted_use(self):
        pass
        #    return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Forecasted Purchase',
        #     'view_mode': 'tree,form',
        #     'res_model': 'purchase.order',
        #     'domain': [('id','=', self.id)],
        #     'context': "{'create': False}"
        # }

    def open_running_stock(self):
        print("---------------------------*****************")
        sql = "delete from hop_product_running_report;"
        self._cr.execute(sql)
        product_rec = self.env['product.product'].search([('product_tmpl_id','=',self.id)])        
        self.env['hop.product.running.report'].generate_running_stock(datetime.now().year,product_rec)
        return {
                'type': 'ir.actions.act_window',
                'name': 'Running Stock',
                'view_mode': 'tree',
                'res_model': 'hop.product.running.report',
                'domain': [('product_id','=', product_rec.id)],
                'context': "{'create': False,'edit':False,'delete':False}"
            }