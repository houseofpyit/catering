from odoo import api, models, fields,_
from odoo.exceptions import UserError

class RMWithCategoryReportWizard(models.TransientModel):
    _name = 'hop.rm.with.category.report.wizard'

    category_ids = fields.Many2many('product.category',string="Category")
    product_ids = fields.Many2many('product.product',string="Raw Material")
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    party_ids = fields.Many2many('res.partner',string="Party")

    @api.onchange('type', 'from_date', 'to_date')
    def onchange_function_ids(self):
        self.party_ids = False
        d = [line.party_name_id.id for line in self.env['hop.function'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date)])]

        return {'domain': {'party_ids': [('id', 'in', d)]}} if d else {'domain': {'party_ids': [('id', '=', 0)]}}
    
    @api.onchange('category_ids')
    def _onchange_category_ids(self):
        if self.category_ids:
            self.product_ids = False
        
    def action_print(self):
        domain = []
        domain.append(('date','>=',self.from_date))
        domain.append(('date','<=',self.to_date))
        if self.party_ids:
            domain.append(('party_name_id','in',self.party_ids.ids))

        functions = self.env['hop.function'].search(domain)
        print(functions)
        if not functions:
            raise UserError("No Record Found............")
        self.env['hop.rm.with.category.report'].search([]).unlink()
        for fun in functions:
            item_raw = fun.fuction_line_ids.filtered(lambda l: l.insider_id.id != False).mapped('item_id')
            record = self.env['hop.recipe.rm'].search([('function_id','in',fun.ids),('recipe_id','in',item_raw.ids)])
            rec_rm_domain = []
            rec_rm_domain.append(('recipe_rm_id','in',record.ids))
            if self.category_ids:
                rec_rm_domain.append(('product_id.categ_id','in',self.category_ids.ids))
            if self.product_ids:
                rec_rm_domain.append(('product_id','in',self.product_ids.ids))
            rec_rm = self.env['hop.rec_rm.line'].search(rec_rm_domain) 
            for line in rec_rm:
                self.env['hop.rm.with.category.report'].create({
                    'function_id':fun.id,
                    'recipe_id':line.recipe_rm_id.recipe_id.product_id.id,
                    'product_id':line.product_id.id,
                    'categ_id':line.product_id.categ_id.id,
                    'name':line.product_id.name,
                    'uom':line.uom.id,
                    'weight':line.weight,
                    'req_weight':line.weight,
                    'cost_price':line.cost,
                    'item_cost':line.item_cost,
                    'vender_id':fun.fuction_line_ids.filtered(lambda l: l.item_id.id == line.recipe_rm_id.id ).insider_id.id,
                })

            # if self.category_ids:
            #     if self.category_ids:
            #         for line in fun.material_line_ids.filtered(lambda l: l.recipe_id.categ_id.id in self.category_ids.ids):
            #             if line.recipe_id.categ_id:
            #                 self.env['hop.rm.with.category.report'].create({
            #                     'function_id':fun.id,
            #                     'recipe_id':line.recipe_id.id,
            #                     'categ_id':line.recipe_id.categ_id.id,
            #                     'name':line.name,
            #                     'uom':line.uom.id,
            #                     'weight':line.weight,
            #                     'req_weight':line.req_weight,
            #                     'cost_price':line.cost_price,
            #                     'item_cost':line.item_cost,
            #                     'vender_id':line.vender_id.id,
            #                 })
            # else:
            #     for line in fun.material_line_ids:
            #         if line.recipe_id.categ_id:
            #             self.env['hop.rm.with.category.report'].create({
            #                 'function_id':fun.id,
            #                 'recipe_id':line.recipe_id.id,
            #                 'categ_id':line.recipe_id.categ_id.id,
            #                 'name':line.name,
            #                 'uom':line.uom.id,
            #                 'weight':line.weight,
            #                 'req_weight':line.req_weight,
            #                 'cost_price':line.cost_price,
            #                 'item_cost':line.item_cost,
            #                 'vender_id':line.vender_id.id,
            #             })

        return {
        'type': 'ir.actions.act_window',
        'name': 'Raw-Material With Category Report',
        'view_mode': 'tree',
        'res_model': 'hop.rm.with.category.report',
        'target': 'main',
        'context': {
            'group_by': ['categ_id','product_id'],  # Replace 'field_name' with the actual field name to group by
            },
}