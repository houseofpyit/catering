from odoo import api, models, fields,_
from odoo.exceptions import UserError
from datetime import datetime,date
from odoo.addons.ct_function_v15.custom_utils import translate_field,meal_type

class FunctionWiseRecipesReportWizard(models.TransientModel):
    _name = 'hop.function.wise.recipes.report.wizard'


    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    fuction_ids = fields.Many2many('hop.function','ref_function_wise_recipes_fuction_ids',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])

    def function_wise_recipes_vals(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        # domain = [('date','=',self.date)]
        if self.fuction_ids:
            domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        print(functions)
        if not functions:
            raise UserError("No Record Found............")
        main=[]
        for raw_rec in functions:
            t= False
            if raw_rec.am_pm == 'am':
                t =f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' PM'
            party_list={}
            party_list.update({
                              'party_name':translate_field(raw_rec.party_name_id , self.language),
                              'company_id': raw_rec.company_id.logo if raw_rec.company_id.logo else False,
                              'party_number':raw_rec.mobile_num,
                              'emergency_contact':raw_rec.emergency_contact,
                              'venue_address':raw_rec.venue_address,
                              'fuction_name':translate_field(raw_rec.fuction_name_id , self.language),
                              'date':raw_rec.date,
                              'meal_type': meal_type(raw_rec.meal_type,self.language,raw_rec),
                              'time':t,
                              'remarks':raw_rec.remarks,
                              'no_of_pax':raw_rec.no_of_pax,
                              'manager_name':translate_field(raw_rec.manager_name_id , self.language),
                              'phone':raw_rec.manager_name_id.phone,
                            })
            vendor_list = []
            vander_change = False
            for line in raw_rec.fuction_line_ids.mapped('insider_id'):
                in_house = []
                vander_change = True
                for fun in raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id == line.id):
                    raw_material = []
                    if fun.insider_id:
                        # for rm in fun.item_id.raw_materials_ids:
                        #     weight = (rm.weight * fun.qty) / rm.recipes_category_id.qty
                        #     raw_material.append({
                        #         'categ': translate_field(rm.item_id.categ_id, self.language),
                        #         'raw_material': translate_field(rm.item_id, self.language),
                        #         'total': round(weight, 2),
                        #         'unit': rm.uom.name
                        #     })
                        record = self.env['hop.recipe.rm'].search([('function_id','=',raw_rec.id),('recipe_id','=',fun.item_id.id)])
                        for rm in record.rec_rm_ids:
                             raw_material.append({
                                'categ': translate_field(rm.product_id.categ_id, self.language),
                                'raw_material': translate_field(rm.product_id, self.language),
                                'total': round(rm.weight, 2),
                                'unit': rm.uom.name
                            })
                    str = translate_field(fun.item_id, self.language) if fun.item_id else ''
                    if fun.instruction:
                        str = f'{str} ({fun.instruction})'
                    if fun.insider_id:
                        str = f'{str} ------> {translate_field(fun.insider_id, self.language)}'
                    vendor_list.append({'vender': str, 'list': raw_material,'vander_change':vander_change})
                    vander_change = False
            if vendor_list:
                party_list['In-House'] = vendor_list
            # if out_source:     
            #     party_list.update({'Out-Source': out_source})
            main.append(party_list)
        return main
    
    def action_print(self):
        return self.env.ref('ct_report_v15.action_function_wise_recipes_report').report_action(self)

                    
                
                