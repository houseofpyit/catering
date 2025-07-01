from odoo import api, models, fields,_
from odoo.exceptions import UserError

class OrderReportWizard(models.TransientModel):
    _name = 'hop.order.report.wizard'

    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    type = fields.Selection([('lead','Lead'),('confirm','Confirm')],string="Type")

    def action_print(self):
        if self.type == 'lead':

            return {
                        'type': 'ir.actions.act_window',
                        'name': 'Lead',
                        'target':'main',
                        'view_mode': 'tree,form',
                        'res_model': 'hop.lead',
                        'domain': [('date','>=', self.from_date),('date','<=', self.to_date)],
                        'context': "{'create': False,'edit':False}"
                    }
        elif self.type == 'confirm':
            return {
                            'type': 'ir.actions.act_window',
                            'name': 'Order',
                            'target':'main',
                            'view_mode': 'tree,form',
                            'res_model': 'hop.function',
                            'domain': [('date','>=', self.from_date),('date','<=', self.to_date)],
                            'context': "{'create': False,'edit':False}"
                        }
        else:
            raise UserError("Select The Type....!!!")
        