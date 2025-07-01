from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons.ct_function_v15.custom_utils import translate_field ,meal_type, utensils_type

class UtensilsReportWizard(models.TransientModel):
    _name = 'hop.utensils.report.wizard'

    fuction_ids = fields.Many2many('hop.function',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")
    utensils_type = fields.Selection([('ground','Ground'),('kitche','Kitchen'),('disposable','Disposable'),('decoration','Decoration'),('all','All')],string="Utensils Type",default="all")
    is_utensils = fields.Boolean(string="Utensils")
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])

    def utensils_vals(self):
        # domain = [('date','=',self.date)]
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        if self.fuction_ids:
            domain.append(('function_id','in',self.fuction_ids.ids))
     
        utensils_ids = self.env['utensils.mst'].search(domain)
        print(utensils_ids)
        main = []
        if not self.is_utensils:
            if not utensils_ids:
                raise UserError("Record Not Found in Utensils!!!")
        
        
        for uten in utensils_ids:
            uutensils_ids_filter = False
            party_list={}
            t= False
            if uten.am_pm == 'am':
                t =f"{int(uten.time):02d}:{int((uten.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(uten.time):02d}:{int((uten.time % 1) * 60):02d}" + ' PM'
            party_list.update({
                              'company_id': uten.company_id.logo if uten.company_id.logo else False,
                              'function_id': translate_field(uten.function_id.party_name_id , self.language),
                              'time': t,
                              'meal_type':meal_type(uten.meal_type,self.language,uten),
                              'am_pm':dict(uten._fields['am_pm'].selection).get(uten.am_pm),
                              'no_of_pax': uten.no_of_pax,
                              'phones': uten.function_id.party_name_id.phone,
                              'em_phone': uten.function_id.emergency_contact,
                              'remarks': uten.remarks,
                              'fuction_name': translate_field(uten.fuction_name_id , self.language),
                              'venue_address':uten.venue_address,
                              'date':uten.date,
                              'manager_name':translate_field(uten.manager_name_id , self.language),
                              'phone':uten.manager_name_id.phone,
                              })

            utensils_list =[]
            if self.utensils_type:
                if self.utensils_type !='all':
                    uutensils_ids_filter = uten.utensils_line_ids.filtered(lambda l: l.utensils_id.utensils_type == self.utensils_type)
                else:
                    uutensils_ids_filter = uten.utensils_line_ids
            else:
                uutensils_ids_filter = uten.utensils_line_ids
            if self.is_utensils:
                unique_utensils_types = set(self.env['product.template'].search([('utility_type', '=', 'utensils')]).mapped('utensils_type'))
                utensils_list = []
                for utn in unique_utensils_types:
                    for line in self.env['product.template'].search([('utility_type', '=', 'utensils'), ('utensils_type', '=', utn)]):
                        utensils_list.append({
                            'utensils': translate_field(line, self.language),
                            'uom': line.uom_id.name,
                            'utensils_type': utensils_type(line.utensils_type, self.language, line),
                        })
            else:
                for line in uutensils_ids_filter:
                    utensils_list.append({
                        'utensils' : translate_field(line.utensils_id , self.language),
                        'uom' : line.uom.name,
                        'utensils_type' : utensils_type(line.utensils_type,self.language,line),
                        'qty' : line.qty,
                        # 'uten_cost' : line.uten_cost,
                    })
            if utensils_list:
                party_list.update({'utensils_detail':utensils_list})
                main.append(party_list)
          
        return main
  
    def action_print(self):
        return self.env.ref('ct_report_v15.action_utensils_report').report_action(self)
        