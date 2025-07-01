from odoo import api, models, fields,_
from odoo.exceptions import UserError
from datetime import datetime,date
from odoo.addons.ct_function_v15.custom_utils import translate_field, meal_type ,location_field

class AllProductionReportWizard(models.TransientModel):
    _name = 'hop.all.production.report.wizard'

    date = fields.Date(string="Date",default=fields.Date.context_today)
    fuction_ids = fields.Many2many('hop.function',string="Function",domain="[('date','=',date)]")
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])
    is_manager = fields.Boolean(string="Manager")
    is_ingredient = fields.Boolean(string="Ingredient")
    is_inhouse = fields.Boolean(string="Inhouse")
    is_recipe = fields.Boolean(string="Recipe")

    def production_report_vals(self):
        main=[]
        for fun in self.fuction_ids:
            report = {}
            if self.is_manager:
                if self.manager_combine():
                    report.update({'manager_combine':self.manager_combine(fun)})
            if self.is_ingredient:
                if self.ingredient_print():
                    report.update({'ingredient_print':self.ingredient_print(fun)})
            if self.is_inhouse:
                if self.inhouse_vender():
                    report.update({'inhouse_vender':self.inhouse_vender(fun)})
            if self.is_recipe:
                if self.recipe_print():
                    report.update({'recipe_print':self.recipe_print(fun)})
            main.append(report)

        # report.update({'manager_combine':self.manager_combine(),
        #                'ingredient_print':self.ingredient_print(),
        #                'inhouse_vender':self.inhouse_vender(),
        #                'recipe_print':self.recipe_print()})  
        return main
  
    def action_print(self):
        return self.env.ref('ct_report_v15.action_all_production_report').report_action(self)
    
    def manager_combine(self,fun=False):
        domain = [('date','=',self.date)]
        if fun:
            domain.append(('id','in',fun.ids))
        else:
            if self.fuction_ids:
                domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        main=[]
        for fun in functions:
            party_list={}
            t = False
            if fun.am_pm == 'am':
                t =f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}" + ' PM'
            party_list.update({'party_name': translate_field(fun.party_name_id , self.language),
                              'company_id': fun.company_id.logo if fun.company_id.logo else False,
                              'party_number':fun.mobile_num,
                              'emergency_contact':fun.emergency_contact,
                              'venue_address':fun.venue_address,
                              'fuction_name':translate_field(fun.fuction_name_id , self.language),
                              'date':fun.date,
                              'meal_type': meal_type(fun.meal_type,self.language,fun),
                              'time':t,
                              'remarks':fun.remarks,
                              'no_of_pax':fun.no_of_pax,
                              'manager_name':translate_field(fun.manager_name_id , self.language),
                              'phone':fun.manager_name_id.phone,
                              })
            # list=[]
            # for cat in fun.fuction_line_ids.mapped('category_id'):
            #     menu =[]
            #     for raw in fun.fuction_line_ids.filtered(lambda l: l.category_id.id == cat.id):
            #         if raw.insider_id: 
            #             menu.append({
            #             'item_id' : raw.item_id.name,
            #             'instruction':raw.instruction,
            #             'vender': raw.insider_id.name,
            #             })
            #     if menu:       
            #         list.append({cat.name:menu})
            # party_list.update({'product_list':list})
            in_house= []
            for vender in fun.fuction_line_ids.mapped('insider_id'):
                menu_list = []
                for line in fun.fuction_line_ids.filtered(lambda l: l.insider_id.id == vender.id):
                            menu_list.append({
                                    'category':translate_field(line.category_id , self.language),
                                    'work':translate_field(line.item_id , self.language),
                                    'no_of_pax':line.no_of_pax,
                                    'instruction':line.instruction,
                            })
                in_house.append({translate_field(vender , self.language) +'('+ str(vender.phone) +')':menu_list})
            if in_house:
                party_list.update({'in_house':in_house})    

            service_list = []
            for ser in fun.hospitality_line_ids:
                service_list.append({
                    'service': translate_field(ser.service_id , self.language),
                    'shift':ser.hospitality_ids.name,
                    'shift_date':ser.shift_date,
                    'shift_time': f"{int(ser.shift_time):02d}:{int((ser.shift_time % 1) * 60):02d}" ,
                    'qty': int(ser.qty_person),
                    'uom':ser.uom_id.name,
                    'remarks' : ser.remarks,
                    'vender_name': translate_field(ser.vender_id , self.language),
                    'vender_number':ser.vender_id.phone,
                    'location': location_field(ser.location,self.language,ser),
                })
            if service_list:
                party_list.update({'services_detail':service_list})
            if service_list != [] or in_house !=[]:
                main.append(party_list)
        return main
    
    def ingredient_print(self,fun=False):
        domain = [('date','=',self.date)]
        if fun:
            domain.append(('id','in',fun.ids))
        else:
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
                              'party_name':translate_field(raw_rec.party_name_id, self.language),
                              'company_id': raw_rec.company_id.logo if raw_rec.company_id.logo else False,
                              'party_number':raw_rec.mobile_num,
                              'emergency_contact':raw_rec.emergency_contact,
                              'venue_address':raw_rec.venue_address,
                              'fuction_name':translate_field(raw_rec.fuction_name_id , self.language),
                              'date':raw_rec.date,
                              'meal_type':meal_type(raw_rec.meal_type,self.language,raw_rec),
                              'time':t,
                              'remarks':raw_rec.remarks,
                              'no_of_pax':raw_rec.no_of_pax,
                              'manager_name':translate_field(raw_rec.manager_name_id , self.language),
                              'phone':raw_rec.manager_name_id.phone,
                              })
            list=[]
            for cat in sorted(raw_rec.material_line_ids.mapped('recipe_id.categ_id'), key=lambda x: x.name):
                raw_material=[]
                item = []
                for raw in raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.categ_id.id == cat.id):
                    purchase = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('product_id','=',raw.recipe_id.id)])
                    if not raw.recipe_id.id in item:
                        raw_rec_materials = raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.id == raw.recipe_id.id)
                        weights = '+'.join(str(round(material.weight,2)) for material in raw_rec_materials)
                        raw_material.append({
                            'raw_material':translate_field(raw.recipe_id , self.language),
                            # + ' (' + translate_field(cat , self.language) + ')'
                            'no_of_time': weights,
                            'total':round(sum(raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.id == raw.recipe_id.id).mapped('weight')),2),
                            'unit': raw.uom.name,
                            'vender':translate_field(purchase.partner_id , self.language),
                        })
                        item.append(raw.recipe_id.id)
                list.append({translate_field(cat , self.language) :raw_material})
            if list:
                party_list.update({'product_list':list})
            main.append(party_list)
        return main
    
    def inhouse_vender(self,fun=False):
        domain = [('date','=',self.date)]
        if fun:
            domain.append(('id','in',fun.ids))
        else:
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
                              'party_name':translate_field(raw_rec.party_name_id, self.language),
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
                    raw_material=[]
                    item = []
                    recipes = False
                    for line in record:
                        if recipes ==  False:
                            recipes = translate_field(line.recipe_id , self.language)
                        else:
                            recipes = recipes + " , "
                            recipes = recipes  + translate_field(line.recipe_id , self.language)
                            
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
            if list :
                party_list.update({'product_list':list})
            main.append(party_list)
        return main
        
    def recipe_print(self,fun=False):
        domain = [('date','=',self.date)]
        if fun:
            domain.append(('id','in',fun.ids))
        else:
            if self.fuction_ids:
                domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        print(functions)
        main=[]
        for raw_rec in functions:
            t= False
            if raw_rec.am_pm == 'am':
                t =f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' PM'
            party_list={}
            party_list.update({
                              'party_name':translate_field(raw_rec.party_name_id, self.language),
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
                        record = self.env['hop.recipe.rm'].search([('function_id','=',raw_rec.id),('recipe_id','=',fun.item_id.id)])
                        for rm in record.rec_rm_ids:
                             raw_material.append({
                                'categ': translate_field(rm.product_id.categ_id, self.language),
                                'raw_material': translate_field(rm.product_id, self.language),
                                'total': round(rm.weight, 2),
                                'unit': rm.uom.name
                            })
                        # for rm in fun.item_id.raw_materials_ids:
                        #     weight = (rm.weight * fun.qty) / rm.recipes_category_id.qty
                        #     raw_material.append({
                        #         'categ': translate_field(rm.item_id.categ_id, self.language),
                        #         'raw_material': translate_field(rm.item_id, self.language),
                        #         'total': round(weight, 2),
                        #         'unit': rm.uom.name
                        #     })
                    str = translate_field(fun.item_id, self.language) if fun.item_id else ''
                    if fun.instruction:
                        str = f'{str} ({fun.instruction})'
                    if fun.insider_id:
                        str = f'{str} ------> {translate_field(fun.insider_id, self.language)}'
                    vendor_list.append({'vender': str, 'list': raw_material,'vander_change':vander_change})
                    vander_change = False
            if vendor_list:
                party_list['In-House'] = vendor_list



            # out_source = []
            # in_house = []
            # for fun in raw_rec.fuction_line_ids:
                
             
                    
            #         raw_material = []
            #         if fun.insider_id:
            #             for rm in fun.item_id.raw_materials_ids:
            #                 wt = (rm.weight*fun.qty)/rm.recipes_category_id.qty
            #                 raw_material.append({
            #                         'categ':translate_field(rm.item_id.categ_id, self.language),
            #                         'raw_material':translate_field(rm.item_id, self.language),
            #                         'total':round(wt,2),
            #                         'unit': rm.uom.name
            #                     })

            #         str = ''
            #         if fun.item_id:
            #             str =  translate_field(fun.item_id , self.language)
            #         if fun.instruction :
            #             str = str + '(' + fun.instruction +')'
                    
            #         if fun.insider_id :
            #             str = str +' ------> ' + translate_field(fun.insider_id , self.language)
            #         in_house.append({str :raw_material})
            # if in_house:
            #     party_list.update({'In-House':in_house})
            # if out_source:     
            #     party_list.update({'Out-Source': out_source})
            main.append(party_list)
        return main
        
            
    
                    
                
                