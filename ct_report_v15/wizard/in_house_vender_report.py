from odoo import api, models, fields,_
from odoo.exceptions import UserError
from datetime import datetime,date
from odoo.addons.ct_function_v15.custom_utils import translate_field, meal_type

class InHouseVenderReportWizard(models.TransientModel):
    _name = 'hop.in.house.vender.report.wizard'

    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    fuction_ids = fields.Many2many('hop.function','ref_in_house_vender_fuction_ids',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])

    def vender_in_house_vals(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        # domain = [('date','=',self.date)]
        if self.fuction_ids:
            domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        main=[]
        for raw_rec in functions:
            party_list={}
            t= False
            if raw_rec.am_pm == 'am':
                t =f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' PM'
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
            list=[]
            # if raw_rec.material_line_ids:
            #     for vender in raw_rec.material_line_ids.mapped('vender_id'):
            #         raw_material=[]
            #         item = []
            #         recipes_id = False
            #         for raw in raw_rec.material_line_ids.filtered(lambda l: l.vender_id.id == vender.id):
            #             if not raw.recipe_id.id in item:
            #                 raw_material.append({
            #                     'categ':translate_field(raw.recipe_id.categ_id, self.language),
            #                     'raw_material':translate_field(raw.recipe_id , self.language),
            #                     'total':round(sum(raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.id == raw.recipe_id.id and l.vender_id.id == vender.id ).mapped('weight')),2),
            #                     'unit': raw.uom.name
            #                 })
            #                 item.append(raw.recipe_id.id)
            #                 recipes_id = raw.recipes_id
            #         if recipes_id:
            #             list.append({translate_field(vender , self.language)+'('+translate_field(recipes_id , self.language)+')':raw_material})
            #         else:
            #             list.append({translate_field(vender , self.language):raw_material})
            #     party_list.update({'product_list':list})
            if raw_rec.fuction_line_ids:
                unique_ids = []
                for line in raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id != False ):
                    if line.insider_id.id not in unique_ids:
                        unique_ids.append(line.insider_id.id)
                
                list = []  # Renamed the variable 'list' to 'result_list' to avoid shadowing the built-in 'list' type
                for vender_id in unique_ids:
                    vander_ob = self.env['res.partner'].search([('id','=',vender_id)])
                    item_raw = raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id == vender_id).mapped('item_id')
                    record = self.env['hop.recipe.rm'].search([('function_id','in',raw_rec.ids),('recipe_id','in',item_raw.ids)])
                    rec_rm = self.env['hop.rec_rm.line'].search([('recipe_rm_id','in',record.ids)])
                    recipes = False
                    for line in record:
                        if recipes ==  False:
                            recipes = translate_field(line.recipe_id , self.language)
                        else:
                            recipes = recipes + " , "
                            recipes = recipes  + translate_field(line.recipe_id , self.language)
                            
                    raw_material=[]
                    item = []
                    recipes_id = False
                    for line in rec_rm:
                        if not line.product_id.id in item:
                            raw_material.append({
                                'categ':translate_field(line.product_id.categ_id, self.language),
                                'raw_material':translate_field(line.product_id , self.language),
                                'total':round(sum(rec_rm.filtered(lambda l: l.product_id.id == line.product_id.id).mapped('weight')),2),
                                'unit': line.uom.name
                            })
                            item.append(line.product_id.id)

                    if vander_ob.phone :
                        list.append({translate_field(vander_ob , self.language) + "("+vander_ob.phone+")" + "(" + recipes + ")":raw_material})
                    else:
                        list.append({translate_field(vander_ob , self.language):raw_material})
                party_list.update({'product_list': list})
            if list:
                main.append(party_list)
        return main
    
    def action_print(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        # domain = [('date','=',self.date)]
        if self.fuction_ids:
            domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        if not functions:
            raise UserError("No Record Found............")
        return self.env.ref('ct_report_v15.action_in_house_vender_report').report_action(self)

                    
                
                