from odoo import models,fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError

class hop_transfer(models.Model):
    _name = "hop.transfer"

    stock = fields.Char(string = "Stock")
    out = fields.Char(string = "Out")
    name = fields.Char(string='Company Name')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)


    def action_transfer(self):
        sql = "delete from hop_opening_stock where company_id = %s "% (self.env.company.children_company_id.id)
        self._cr.execute(sql)
        for product in self.env['product.product'].search([]):
            date =  self.env.company.to_date     
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
            on_hand = pur_qty - rm_qty - issue_qty + return_qty + sum(self.env['hop.opening.stock'].search([('product_id','=',product.id)]).mapped('qty'))
            print("............................",product.name,on_hand)
            
            if on_hand > 0:
                print("...................")
                from_year = self.env.company.from_date.year
                new  = self.env['hop.opening.stock'].sudo().create({'product_id': product.id,
                    'date':datetime(from_year + 1, 4, 1),
                    'qty':on_hand,
                    'company_id':self.env.company.children_company_id.id,

                })
                print(new.company_id.name)

    def action_ok(self):
        pass

    def action_all(self):

        if not self.env.company.from_date or not self.env.company.to_date:
            raise UserError(_('First Fill Financial Year Date!!!'))
        # year = self.env.company.to_date.year
        from_year = self.env.company.from_date.year
        to_year = self.env.company.to_date.year
        start_date = datetime(from_year + 1, 4, 1)
        end_date = datetime(to_year + 1, 3, 31)
        company = self.env.company.name
        company_id = self.env.company.id
        name =  company + ' ' + '(' + str(start_date.strftime('%Y')) + '-' + str(end_date.strftime('%Y')) + ')'
        res_comp = self.env['res.company'].create({
            'name': name,
            'from_date':start_date,
            'to_date':end_date,
            'parent_company_id':company_id,
        })

        self.env.company.write({
                'children_company_id': res_comp.id,
            })
