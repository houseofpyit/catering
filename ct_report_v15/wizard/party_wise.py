from odoo import api, models, fields,_
from odoo.exceptions import UserError

class PartyWiseReportWizard(models.TransientModel):
    _name = 'hop.party.wise.report.wizard'

    party_ids = fields.Many2many('res.partner',string="Party",tracking=True,domain=[('is_customer','=',True)])
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)

    @api.onchange('to_date','from_date')
    def onchange_from_date(self):
        domain = []
        functions = self.env['hop.function'].search([('date','>=',self.from_date),('date','<=',self.to_date)])
        if functions:
            domain.append(('id', 'in', functions.party_name_id.ids))
        else:
            domain.append(('id', '=', 0))
        return {'domain': {'party_ids': domain}}

    def action_print(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        if self.party_ids:
            domain.append(('party_name_id','in',self.party_ids.ids))
        functions = self.env['hop.function'].search(domain)
        print(functions)
        if not functions:
            raise UserError("No Record Found............")
        self.env['hop.party.wise.report'].search([]).unlink()
        for fun in functions:
            self.env['hop.party.wise.report'].create({
                'function_id':fun.id,
                'fuction_name_id':fun.fuction_name_id.id,
                'party_name_id':fun.party_name_id.id,
                'mobile_num':fun.mobile_num,
                'date':fun.date,
                'emergency_contact':fun.emergency_contact,
                'remarks':fun.remarks,
                'manager_name_id':fun.manager_name_id.id,
                'meal_type':fun.meal_type,
                'no_of_pax':fun.no_of_pax,
                'time':fun.time,
                'am_pm':fun.am_pm,
                'venue_address':fun.venue_address
            })
        return {
                'type': 'ir.actions.act_window',
                'name': 'Party Wise Report',
                'view_mode': 'tree',
                'res_model': 'hop.party.wise.report',
                'target':'main',
                'context': {
            'group_by': 'party_name_id',  # Replace 'field_name' with the actual field name to group by
            },
            }