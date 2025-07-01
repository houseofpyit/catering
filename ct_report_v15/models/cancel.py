from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

class HopCancel(models.TransientModel):
    _name = 'hop.cancel.report.wizard'

    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    def action_print(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        record=self.env['hop.cancel.report'].search(domain)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel Report',
            'view_mode': 'tree',
            'domain': [('id','in', record.ids)],
            'res_model': 'hop.cancel.report',
            'context': "{'create': False,'edit':False,'delete':False, 'group_by': 'party_id'}"
        }


    def generate_cancel_pdf_vals(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        record=self.env['hop.cancel.report'].search(domain)
        main={}
        party_data=[]
        for res in record.mapped('party_id'):
            record_list = []
            for line in record.filtered(lambda l: l.party_id.id == res.id):
                record_list.append(
                    {
                    'date': line.date,
                    'meal_type': dict(line._fields['meal_type'].selection).get(line.meal_type) ,
                    'cancel_type': dict(line._fields['cancel_type'].selection).get(line.cancel_type),
                    })
            party_data.append({'party':res.name,'detail':record_list})
        main.update({'cancel_data':party_data})
        main.update({'company_id':self.company_id.logo if self.company_id.logo else False})

        return [main]

    def generate_pdf(self):
        return self.env.ref('ct_report_v15.action_cancel_report').report_action(self)              
