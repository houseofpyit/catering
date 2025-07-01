from odoo import api, models, fields,_
from odoo.exceptions import UserError

class ItemWiseReportWizard(models.TransientModel):
    _name = 'hop.item.wise.report.wizard'

    item_ids = fields.Many2many('hop.recipes',string="Item")
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)

    def action_print(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        functions = self.env['hop.function'].search(domain)
        print(functions)
        if not functions:
            raise UserError("No Record Found............")
        self.env['hop.item.wise.report'].search([]).unlink()
        for fun in functions:
            if self.item_ids: 
                for line in fun.fuction_line_ids.filtered(lambda l: l.item_id.id in self.item_ids.ids):
                    self.env['hop.item.wise.report'].create({
                        'function_id':fun.id,
                        'category_id':line.category_id.id,
                        'item_id':line.item_id.id,
                        'no_of_pax':line.no_of_pax,
                        'per_qty':line.per_qty,
                        'qty':line.qty,
                        'uom':line.uom.id,
                        'insider_id':line.insider_id.id,
                        'out_sider_id':line.out_sider_id.id,
                        'cost':line.cost,
                        'rate':line.rate,
                        'instruction':line.instruction
                    })
            else:
                for line in fun.fuction_line_ids:
                    self.env['hop.item.wise.report'].create({
                        'function_id':fun.id,
                        'category_id':line.category_id.id,
                        'item_id':line.item_id.id,
                        'no_of_pax':line.no_of_pax,
                        'per_qty':line.per_qty,
                        'qty':line.qty,
                        'uom':line.uom.id,
                        'insider_id':line.insider_id.id,
                        'out_sider_id':line.out_sider_id.id,
                        'cost':line.cost,
                        'rate':line.rate,
                        'instruction':line.instruction
                    })

        return {
                'type': 'ir.actions.act_window',
                'name': 'Item Wise Report',
                'view_mode': 'tree',
                'res_model': 'hop.item.wise.report',
                'target':'main',
                  'context': {
            'group_by': 'item_id',  # Replace 'field_name' with the actual field name to group by
            },
            }