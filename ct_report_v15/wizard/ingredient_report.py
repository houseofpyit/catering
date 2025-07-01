from odoo import api, models, fields,_
from odoo.exceptions import UserError
from datetime import datetime,date
from odoo.addons.ct_function_v15.custom_utils import translate_field,meal_type

class ingredientsReportWizard(models.TransientModel):
    _name = 'hop.ingredients.report.wizard'

    type =  fields.Selection([('normal','Normal'),('details','Details')])
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    fuction_ids = fields.Many2many('hop.function','ref_ingredients_fuction_ids',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])

    def ingredients_vals(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        # domain = [('date','=',self.date)]
        if self.fuction_ids:
            domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        if not functions:
            raise UserError("No Record Found............")
        main=[]
        for raw_rec in functions:
            party_list={}
            t= False
            if raw_rec.am_pm == 'am':
                t =f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' PM'
            party_list.update({
                              'party_name': translate_field(raw_rec.party_name_id , self.language),
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
            # for cat in raw_rec.material_line_ids.mapped('recipe_id.categ_id'):
            #     raw_material=[]

            #     item = []
            #     for raw in raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.categ_id.id == cat.id):
                   
            #             if not raw.recipe_id.id in item:
            #                 raw_rec_materials = raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.id == raw.recipe_id.id)
            #                 weights = '+'.join(str(round(material.weight,2)) for material in raw_rec_materials)
            #                 raw_material.append({
            #                     'raw_material': translate_field(raw.recipe_id , self.language) + ' (' + translate_field(cat , self.language) + ')',
            #                     'no_of_time': weights,
            #                     'total':round(sum(raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.id == raw.recipe_id.id).mapped('weight')),2),
            #                     'unit': raw.uom.name
            #                 })
            #                 item.append(raw.recipe_id.id)
            #     list.append({translate_field(cat , self.language):raw_material})
            # party_list.update({'product_list':list})
            for cat in sorted(raw_rec.material_line_ids.mapped('recipe_id.categ_id'), key=lambda x: x.name):
                raw_material = []
                item = []
                for raw in raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.categ_id.id == cat.id):
                    purchase = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('product_id','=',raw.recipe_id.id)])
                    if raw.recipe_id.id not in item:
                        raw_rec_materials = raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.id == raw.recipe_id.id)
                        weights = '+'.join(str(round(material.weight,2)) for material in raw_rec_materials)
                        raw_material.append({
                            'raw_material': translate_field(raw.recipe_id, self.language),
                            #  + ' (' + translate_field(cat, self.language) + ')'
                            'no_of_time': weights,
                            'total':round(sum(raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.id == raw.recipe_id.id).mapped('weight')), 2),
                            'unit': raw.uom.name,
                            'vender':translate_field(purchase.partner_id , self.language),
                        })
                        item.append(raw.recipe_id.id)
                list.append({translate_field(cat , self.language) :raw_material})
            print("***********************",list)
            party_list.update({'product_list':list})
            main.append(party_list)
            # if list == []:
            #     raise UserError("Record Not Found...!")
        return main

    def action_print_normal(self):   
        return self.env.ref('ct_report_v15.action_ingredients_report').report_action(self)

    def ingredients_report_details(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        # domain = [('date','=',self.date)]
        if self.fuction_ids:
            domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        if not functions:
            raise UserError("No Record Found............")
        main=[]
        for raw_rec in functions:
            party_list={}
            t= False
            if raw_rec.am_pm == 'am':
                t =f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' PM'
            party_list.update({
                              'party_name': translate_field(raw_rec.party_name_id , self.language),
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
            record = self.env['hop.recipe.rm'].search([('function_id','in',raw_rec.ids)])
            rec_rm = self.env['hop.rec_rm.line'].search([('recipe_rm_id','in',record.ids)])
            
            for cat in rec_rm.mapped('product_id.categ_id'):
                product_record = rec_rm.filtered(lambda l: l.product_id.categ_id.id == cat.id)
                cat_detail = []
                product_list = []
                for line in product_record:
                    if line.product_id.id not in product_list:
                        
                        purchase = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('product_id','=',line.product_id.id)])
                        if len(product_record.filtered(lambda l: l.product_id.id == line.product_id.id)) == 1:
                            cat_detail.append(
                                {
                                    'vender':translate_field(purchase.partner_id, self.language),
                                    'product':translate_field(line.product_id, self.language),
                                    'total': round(line.weight,2),
                                    'uom':line.uom.name,
                                    'item':translate_field(line.recipe_rm_id.recipe_id, self.language),
                                    'qty':round(line.weight,2),
                                    'u_uom':line.uom.name
                                }
                            )

                        else:
                            
                            length = int(len(product_record.filtered(lambda l: l.product_id.id == line.product_id.id)))
                            i = 1
                            for l in product_record.filtered(lambda x: x.product_id.id == line.product_id.id):
                                if i  == 1:
                                    cat_detail.append(
                                    {
                                        'vender': translate_field(purchase.partner_id, self.language),
                                        'product':translate_field(l.product_id, self.language),
                                        'total': round(sum(product_record.filtered(lambda x: x.product_id.id == line.product_id.id).mapped('weight')),2),
                                        'uom':l.uom.name,
                                        'item':translate_field(l.recipe_rm_id.recipe_id, self.language),
                                        'qty':round(l.weight,2),
                                        'u_uom':l.uom.name
                                    })
                                else:
                                    cat_detail.append(
                                    {
                                        'vender': '',
                                        'product':'',
                                        'total':0,
                                        'uom':'',
                                        'item':translate_field(l.recipe_rm_id.recipe_id, self.language),
                                        'qty':round(l.weight,2),
                                        'u_uom':l.uom.name
                                    })
                        
                                i = i + 1 
                        product_list.append(line.product_id.id)
                list.append({'catag':translate_field(cat, self.language),'raw_detail':cat_detail})
            party_list.update({'product_list':list})
            main.append(party_list)
            # if list == []:
            #     raise UserError("Record Not Found...!")
        return main
    def action_print(self):
        return self.env.ref('ct_report_v15.action_ingredients_report_details').report_action(self)
                
                