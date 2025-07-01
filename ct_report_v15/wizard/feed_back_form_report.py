from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons.ct_function_v15.custom_utils import translate_field,meal_type

class feedbackreportwizard(models.TransientModel):
    _name = 'feedback.report.wizard'

    fuction_ids = fields.Many2many('hop.function',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])

    def feedback_vals(self):
        print(".........")
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        if self.fuction_ids:
            domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        print(functions)
        if not functions:
            raise UserError("No Record Found............")
        main=[]
        for fun in functions:
            t= False
            if fun.am_pm == 'am':
                t =f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}" + ' PM'
            addons_data = []
            for line in fun.extra_service_line_ids:
                addons_data.append(translate_field(line.service_id , self.language))
            addons_data = ' , '.join(addons_data)
            party_list={}
            party_list.update({'party_name':translate_field(fun.party_name_id , self.language),
                              'company_id': fun.company_id.logo if fun.company_id.logo else False,
                              'party_number':fun.mobile_num,
                              'emergency_contact':fun.emergency_contact,
                              'venue_address':fun.venue_address,
                              'fuction_name':translate_field(fun.fuction_name_id , self.language),
                              'date':fun.date,
                              'meal_type': meal_type(fun.meal_type,self.language,fun),
                              'time':t,
                              'am_pm':dict(fun._fields['am_pm'].selection).get(fun.am_pm),
                              'remarks':fun.remarks,
                              'no_of_pax':fun.no_of_pax,
                              'manager_name':translate_field(fun.manager_name_id , self.language),
                              'phone':fun.manager_name_id.phone,
                              'addons_data': addons_data if addons_data else False
                              })
            main.append(party_list)

        return main

    def action_print(self):
        return self.env.ref('ct_report_v15.action_feed_back_report').report_action(self)
            