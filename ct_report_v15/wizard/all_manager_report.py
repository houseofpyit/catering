from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.addons.ct_function_v15.custom_utils import translate_field, meal_type, utensils_type ,location_field

def tuple_return(cut_list):
    typle_list=''
    for i in cut_list:
        if typle_list == '':
            typle_list += '(' + str(i)
        else:
            typle_list += ',' + str(i)
    typle_list +=')'
    return typle_list

class AllManagerReportWizard(models.TransientModel):
    _name = 'hop.all.manager.report.wizard'

    fuction_ids = fields.Many2many('hop.function', 'ref_all_manager_funtion_ids', string="Function", domain="[('date', '=', date)]")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])
    is_utensil = fields.Boolean(string="Utensils")
    is_blank_utensils = fields.Boolean(string="Blank Utensils")
    is_vendor = fields.Boolean(string="Vendor")
    is_feedback = fields.Boolean(string="Feedback")
    is_menu = fields.Boolean(string="Menu")

    def manager_vals(self):
        main = []

        query = f"""SELECT id FROM hop_function WHERE id IN {tuple_return(self.fuction_ids.ids)}
            ORDER BY am_pm, time ASC"""
        self.env.cr.execute(query)
        query_result = self.env.cr.fetchall()

        for fun_id in query_result:
            fun = self.env['hop.function'].sudo().search([('id','=',fun_id)])
            report = {}
            if self.is_utensil or self.is_blank_utensils:
                if self.utensils_report():
                    report.update({'utensils_report': self.utensils_report(fun)})
                # if self.report_menu():
                #     report.update({'report_menu':self.report_menu()})
            if self.is_vendor:
                if self.vendor_confirmation():
                    report.update({'vendor_confirmation': self.vendor_confirmation(fun)})
            if self.is_feedback:
                if self.feedback_report():
                    report.update({'feedback_report': self.feedback_report(fun)})
            if self.is_menu:
                if self.menu_report():
                    report.update({'menu_report': self.menu_report(fun)})
            main.append(report)
        
        return main
    
    def action_print(self):
        if self.is_utensil and self.is_blank_utensils:
            raise UserError("You cannot select both  Utensils and Blank Utensils!!!") 
        return self.env.ref('ct_report_v15.action_all_manager_report').report_action(self)

    def utensils_report(self, fun=None):
        domain = [('date', '=', self.date)]

        if fun:
            domain.append(('function_id', 'in', fun.ids))
        elif self.fuction_ids:
            domain.append(('function_id', 'in', self.fuction_ids.ids))

        utensils_ids = self.env['utensils.mst'].search(domain)
        main = []

        for uten in utensils_ids:
            if self.is_utensil:
                utensils_list = [
                    {
                        'utensils': translate_field(line.utensils_id , self.language),
                        'uom': line.uom.name,
                        'utensils_type': utensils_type(line.utensils_type,self.language,line),
                        'qty': line.qty,
                        # 'uten_cost': line.uten_cost,
                    }
                    for line in uten.utensils_line_ids
                ]
            elif self.is_blank_utensils:
                unique_utensils_types = set(self.env['product.template'].search([('utility_type', '=', 'utensils')]).mapped('utensils_type'))
                utensils_list = []
                for utn in unique_utensils_types:
                    for line in self.env['product.template'].search([('utility_type', '=', 'utensils'), ('utensils_type', '=', utn)]):
                        utensils_list.append({
                            'utensils': translate_field(line, self.language),
                            'uom': line.uom_id.name,
                            'utensils_type': utensils_type(line.utensils_type, self.language, line),
                        })

            party_list = {
                'function_id': translate_field(uten.function_id.party_name_id , self.language),
                'company_id': uten.company_id.logo if uten.company_id.logo else False,
                'time': f"{int(uten.time):02d}:{int((uten.time % 1) * 60):02d} {'AM' if uten.am_pm == 'am' else 'PM'}",
                'meal_type': meal_type(uten.meal_type,self.language,uten),
                'am_pm': dict(uten._fields['am_pm'].selection).get(uten.am_pm),
                'no_of_pax': uten.no_of_pax,
                'phones': uten.function_id.party_name_id.phone,
                'em_phone': uten.function_id.emergency_contact,
                'remarks': uten.remarks, 
                'fuction_name': translate_field(uten.fuction_name_id , self.language),
                'venue_address': uten.venue_address,
                'date': uten.date,
                'manager_name': translate_field(uten.manager_name_id , self.language),
                'phone': uten.manager_name_id.phone,
            }

            if utensils_list:
                party_list['utensils_detail'] = utensils_list
            
            if party_list:
                main.append(party_list)

        return main

    def report_menu(self, fun=None):
        domain = [('date', '=', self.date)]

        if fun:
            domain.append(('id', 'in', fun.ids))
        elif self.fuction_ids:
            domain.append(('id', 'in', self.fuction_ids.ids))

        functions = self.env['hop.function'].search(domain)
        main = []

        for fun in functions:
            meal_type = dict(fun._fields['meal_type'].selection).get(fun.meal_type)

            menu_list = [
                { 
                    'category': translate_field(menu.category_id , self.language),
                    'item_id': translate_field(menu.item_id , self.language),
                    'no_of_pax': menu.no_of_pax,
                    'instruction': menu.instruction,
                    'vendor': translate_field(menu.insider_id.name if menu.insider_id else menu.out_sider_id.name, self.language),
                    'in_out': "In-House" if menu.insider_id else "Out-source",
                    'contact': menu.insider_id.phone if menu.insider_id else menu.out_sider_id.phone,
                }
                for menu in fun.fuction_line_ids
            ]

            service_list = [
                {   
                    'service': translate_field(ser.service_id , self.language),
                    'shift': ser.hospitality_ids.name,
                    'shift_date': ser.shift_date,
                    'shift_time': f"{int(ser.shift_time):02d}:{int((ser.shift_time % 1) * 60):02d}",
                    'qty': int(ser.qty_person),
                    'uom': ser.uom_id.name,
                    'remarks': ser.remarks,
                    'vendor_name': translate_field(ser.vender_id , self.language),
                    'vendor_number': ser.vender_id.phone,
                    'location': location_field(ser.location,self.language,ser),
                }
                for ser in fun.hospitality_line_ids
            ]

            addons_list = [
                {    
                    'service': translate_field(addons.service_id, self.language),
                    'date': addons.date,
                    'time': f"{int(addons.time):02d}:{int((addons.time % 1) * 60):02d} {'AM' if fun.am_pm == 'am' else 'PM'}",
                    'qty': int(addons.qty_ids),
                    'uom': addons.uom_id.name,
                    'price': addons.price,
                    'vendor_name': translate_field(addons.vender_id , self.language),
                    'vendor_number': addons.vender_id.phone,
                    'instruction':addons.instruction,
                }
                for addons in fun.extra_service_line_ids
            ]

            if menu_list or service_list or addons_list:
                main.append({     
                    'party_name': translate_field(fun.party_name_id , self.language),
                    'company_id': fun.company_id.logo if fun.company_id.logo else False,
                    'party_number': fun.mobile_num,
                    'emergency_contact': fun.emergency_contact,
                    'venue_address': fun.venue_address, 
                    'fuction_name': translate_field(fun.fuction_name_id , self.language),
                    'date': fun.date,
                    'meal_type': meal_type(fun.meal_type,self.language,fun),
                    'time': f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d} {'AM' if fun.am_pm == 'am' else 'PM'}",
                    'remarks': fun.remarks,
                    'no_of_pax': fun.no_of_pax,
                    'manager_name': translate_field(fun.manager_name_id , self.language),
                    'phone': fun.manager_name_id.phone,
                    'menu_detail': menu_list,
                    'services_detail': service_list,
                    'addons_detail': addons_list,
                })

        return main

    def vendor_confirmation(self, fun=False):
        domain = [('date', '=', self.date)]

        if fun:
            domain.append(('id', 'in', fun.ids))
        else:
            if self.fuction_ids:
                domain.append(('id', 'in', self.fuction_ids.ids))

        functions = self.env['hop.function'].search(domain)
        main = []
        
        for raw_rec in functions:
            line = {
                'party_name': translate_field(raw_rec.party_name_id , self.language),
                'company_id': raw_rec.company_id.logo if raw_rec.company_id.logo else False,
                'party_number': raw_rec.mobile_num,
                'emergency_contact': raw_rec.emergency_contact,
                'venue_address': raw_rec.venue_address, 
                'fuction_name': translate_field(raw_rec.fuction_name_id , self.language),
                'date': raw_rec.date,
                'meal_type': meal_type(raw_rec.meal_type,self.language,raw_rec),
                'time': self.format_time(raw_rec.time, raw_rec.am_pm),
                'remarks': raw_rec.remarks,
                'no_of_pax': raw_rec.no_of_pax,
                'manager_name': translate_field(raw_rec.manager_name_id , self.language),
                'phone': raw_rec.manager_name_id.phone,
                'in_house': [],
                'out_source': [],
                'hospitality_list': [],
                'addons_list': []
            }
            for vendor in raw_rec.fuction_line_ids.mapped('insider_id'):
                menu_list = []
                for fun in raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id == vendor.id):
                    menu_list.append({ 
                        'work': translate_field(fun.item_id , self.language),
                        'no_of_pax': fun.no_of_pax,
                        'helper': fun.helper,
                        'chief': fun.chief,
                        'instruction': fun.instruction,
                        'category': translate_field(fun.category_id, self.language),
                    })
                
                line['in_house'].append({f"{translate_field(vendor,self.language)} ({vendor.phone})": menu_list})
            for vendor in raw_rec.fuction_line_ids.mapped('out_sider_id'):
                menu_list = []
                for fun in raw_rec.fuction_line_ids.filtered(lambda l: l.out_sider_id.id == vendor.id):
                    menu_list.append({
                        'work': translate_field(fun.item_id , self.language),
                        'no_of_pax': fun.no_of_pax,
                        'helper': fun.helper,
                        'chief': fun.chief,
                        'instruction': fun.instruction,
                        'category': translate_field(fun.category_id, self.language),
                    })
                line['out_source'].append({f"{translate_field(vendor,self.language)} ({vendor.phone})": menu_list})

            for vendor in raw_rec.hospitality_line_ids.mapped('vender_id'):
                hospitality_list = []
                for ser in raw_rec.hospitality_line_ids.filtered(lambda l: l.vender_id.id == vendor.id):
                    hospitality_list.append({ 
                        'service': translate_field(ser.service_id , self.language),
                        'shift': ser.hospitality_ids.name,
                        'shift_date': ser.shift_date,
                        'shift_time': self.format_time(ser.shift_time),
                        'qty': int(ser.qty_person),
                        'uom': ser.uom_id.name,
                        'remarks': ser.remarks,
                    })
                line['hospitality_list'].append({f"{translate_field(vendor,self.language)} ({vendor.phone})": hospitality_list})

            for vendor in raw_rec.extra_service_line_ids.mapped('vender_id'):
                addons_list = []
                for addons in raw_rec.extra_service_line_ids.filtered(lambda l: l.vender_id.id == vendor.id):
                    addons_list.append({
                        'service': translate_field(addons.service_id , self.language),
                        'date': addons.date,
                        'time': self.format_time(addons.time),
                        'qty': int(addons.qty_ids),
                        'uom': addons.uom_id.name,
                        'price': addons.price,
                        'instruction':addons.instruction,
                    })
                line['addons_list'].append({f"{translate_field(vendor,self.language)} ({vendor.phone})": addons_list})

        if any([line['in_house'], line['out_source'], line['hospitality_list'], line['addons_list']]):
            main.append(line)
        return main

    # def vendor_confirmation(self,fun=False):
    #     domain = [('date','=',self.date)]
    #     # domain = [('date','=',self.date)]
    #     if fun:
    #          domain.append(('id','in',fun.ids))
    #     else:
    #         if self.fuction_ids:
    #             domain.append(('id','in',self.fuction_ids.ids))
    #     functions = self.env['hop.function'].search(domain)
    #     main=[]
    #     for raw_rec in functions:
    #         line = {}
    #         in_house = []
    #         out_source = []
    #         service = []
    #         addon = []
    #         t= False
    #         if raw_rec.am_pm == 'am':
    #             t =f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' AM'
    #         else:
    #             t = f"{int(raw_rec.time):02d}:{int((raw_rec.time % 1) * 60):02d}" + ' PM'
    #         line.update({
    #                     'party_name':translate_field(raw_rec.party_name_id , self.language),
    #                     'company_id': raw_rec.company_id.logo,
    #                     'party_number':raw_rec.mobile_num,
    #                     'emergency_contact':raw_rec.emergency_contact,
    #                     'venue_address':raw_rec.venue_address,
    #                     'fuction_name':translate_field(raw_rec.fuction_name_id , self.language),
    #                     'date':raw_rec.date,
    #                     'meal_type': meal_type(raw_rec.meal_type,self.language,raw_rec),
    #                     'time':t,
    #                     'remarks':raw_rec.remarks,
    #                     'no_of_pax':raw_rec.no_of_pax,
    #                     'manager_name': translate_field(raw_rec.manager_name_id , self.language),
    #                     'phone':raw_rec.manager_name_id.phone,
    #                     })
    #         for vender in raw_rec.fuction_line_ids.mapped('insider_id'):
    #             menu_list = []
    #             for fun in raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id == vender.id):
                    
    #                         menu_list.append({
    #                                 'work':translate_field(fun.item_id , self.language),
    #                                 'no_of_pax':fun.no_of_pax,
    #                                 'instruction':fun.instruction,
    #                         })
    #             in_house.append({vender.name +'('+ str(vender.phone) +')':menu_list})
    #             line.update({'in_house':in_house})

    #         for vender in raw_rec.fuction_line_ids.mapped('out_sider_id'):
    #             menu_list = []
    #             for fun in raw_rec.fuction_line_ids.filtered(lambda l: l.out_sider_id.id == vender.id):
    #                          menu_list.append({
    #                                 'work':translate_field(fun.item_id , self.language),
    #                                 'no_of_pax':fun.no_of_pax,
    #                                 'instruction':fun.instruction,
    #                         })
                    
    #             out_source.append({vender.name+'('+ str(vender.phone) +')':menu_list})
    #         if out_source:      
    #             line.update({'out_source':out_source})

    #         for vender in raw_rec.hospitality_line_ids.mapped('vender_id'):
    #             hospitality_list=[]
    #             for ser in raw_rec.hospitality_line_ids.filtered(lambda l: l.vender_id.id == vender.id):
               
    #                 hospitality_list.append({
    #                     'service': translate_field(ser.service_id , self.language),
    #                     'shift':ser.hospitality_ids.name,
    #                     'shift_date':ser.shift_date,
    #                     'shift_time': f"{int(ser.shift_time):02d}:{int((ser.shift_time % 1) * 60):02d}" ,
    #                     'qty': ser.qty_person,
    #                     'uom':ser.uom_id.name,
    #                     'remarks' : ser.remarks,
    #                 })   
    #             service.append({vender.name+'('+ str(vender.phone) +')':hospitality_list})
    #         if service:
    #             line.update({'hospitality_list':service})
    #         for vender in raw_rec.extra_service_line_ids.mapped('vender_id'):
    #             addons_list=[]
    #             for addons in raw_rec.extra_service_line_ids.filtered(lambda l: l.vender_id.id == vender.id):
    #                 t= False
    #                 if addons.am_pm == 'am':
    #                     t =f"{int(addons.time):02d}:{int((addons.time % 1) * 60):02d}" + ' AM'
    #                 else:
    #                     t = f"{int(addons.time):02d}:{int((addons.time % 1) * 60):02d}" + ' PM'
    #                 addons_list.append({
    #                     'service': translate_field(addons.service_id , self.language),
    #                     'date':addons.date,
    #                     'time':t,
    #                     'qty': addons.qty_ids,
    #                     'uom':addons.uom_id.name,
    #                     'price':addons.price,
    #                 })
    #             addon.append({vender.name+'('+ str(vender.phone) +')':addons_list})
    #         if addon:
    #             line.update({'addons_list':addon})
            
    #         # in_main ={}
    #         # menu_list = []
    #         # hospitality_list = []
    #         # addons_list = []
    #         # for fun in raw_rec.fuction_line_ids:
    #         #     if fun.insider_id :
    #         #         menu_list.append({
    #         #                 'vender': fun.insider_id.name,
    #         #                 'contact':fun.insider_id.phone,
    #         #                 'work':fun.item_id.name,
    #         #                 'no_of_pax':fun.no_of_pax,
    #         #                 'instruction':fun.instruction,
    #         #                 'type':'In-House'
    #         #         })
    #         #     else:
    #         #         menu_list.append({
    #         #                 'vender': fun.out_sider_id.name,
    #         #                 'contact':fun.out_sider_id.phone,
    #         #                 'work':fun.item_id.name,
    #         #                 'no_of_pax':fun.no_of_pax,
    #         #                 'instruction':fun.instruction,
    #         #                 'type':'Out-Source'
    #         #         })
         
    #         # if menu_list:
    #         #     in_main.update({'menu_list':menu_list})
      
    #         # for ser in raw_rec.hospitality_line_ids:
    #         #     hospitality_list.append({
    #         #         'service': ser.service_id.name,
    #         #         'shift':ser.hospitality_ids.name,
    #         #         'shift_date':ser.shift_date,
    #         #         'shift_time': ser.shift_time,
    #         #         'qty': ser.qty_person,
    #         #         'uom':ser.uom_id.name,
    #         #         'remarks' : ser.remarks,
    #         #         'vender_name': ser.vender_id.name,
    #         #         'vender_number':ser.vender_id.phone
    #         #     })   

    #         # if hospitality_list:
    #         #     in_main.update({'hospitality_list':hospitality_list}) 
    #         # for addons in raw_rec.extra_service_line_ids:
    #         #     addons_list.append({
    #         #         'service': addons.service_id.name,
    #         #         'date':addons.date,
    #         #         'time':addons.time,
    #         #         'qty': addons.qty_ids,
    #         #         'uom':addons.uom_id.name,
    #         #         'price':addons.price,
    #         #         'vender_name': ser.vender_id.name,
    #         #         'vender_number':ser.vender_id.phone
    #         #     })
    #         # if addons_list:
    #         #     in_main.update({'addons_list':addons_list}) 
    #         if in_house != [] or out_source != [] or service != [] or addon != []:
    #             main.append(line)
    #     return main

    def format_time(self, time, am_pm=None):
        t = f"{int(time):02d}:{int((time % 1) * 60):02d}"
        if am_pm:
            t += ' AM' if am_pm == 'am' else ' PM'
        return t

    def feedback_report(self, fun=False):
        domain = [('date', '=', self.date)]
        if fun:
            domain.append(('id', 'in', fun.ids))
        else:
            if self.fuction_ids:
                domain.append(('id', 'in', self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        main = []

        for fun in functions:
            t = self.format_time(fun.time, fun.am_pm)
            addons_data = []
            for line in fun.extra_service_line_ids:
                addons_data.append(translate_field(line.service_id , self.language))
            addons_data = ' , '.join(addons_data)
            party_list = {  
                'party_name': translate_field(fun.party_name_id , self.language),
                'company_id': fun.company_id.logo if fun.company_id.logo else False,
                'party_number': fun.mobile_num,
                'emergency_contact': fun.emergency_contact,
                'venue_address': fun.venue_address,
                'fuction_name': translate_field(fun.fuction_name_id , self.language),
                'date': fun.date,
                'meal_type': meal_type(fun.meal_type,self.language,fun),
                'time': t,
                'am_pm': dict(fun._fields['am_pm'].selection).get(fun.am_pm),
                'remarks': fun.remarks,
                'no_of_pax': fun.no_of_pax,
                'manager_name': translate_field(fun.manager_name_id , self.language),
                'phone': fun.manager_name_id.phone,
                'addons_data': addons_data if addons_data else False
            }

            if party_list:
                main.append(party_list)

        if main:
            return main
        else:
            return False

    def menu_report(self, fun=False):
        print("-----------------------fun",fun)
        domain = [('date', '=', self.date)]

        if fun:
            domain.append(('hop_funtion_id', 'in', fun.ids))
        else:
            if self.fuction_ids:
                domain.append(('hop_funtion_id', 'in', self.fuction_ids.ids))

        menu = self.env['hop.lead'].search(domain)
        main = []

        for me in menu:
            t = self.format_time(me.time, me.am_pm)

            party_list = {  
                'company_id': me.company_id.logo if me.company_id.logo else False,
                'party_name': translate_field(me.party_name_id , self.language),
                'venue_address': me.venue_address,
                'mobile_num': me.mobile_num,
                'date': me.date,
                'meal_type': meal_type(me.meal_type,self.language,me),
                'time': t,
                'remarks': me.remarks,
                'function_name': me.fuction_name_id.name,
                'notes': me.notes,
                'no_of_pax': me.no_of_pax,
            }

            product_list = []
            for line in me.fuction_line_ids.mapped('category_id'):
                items = []
                for res in me.fuction_line_ids.filtered(lambda l: l.category_id.id == line.id):
                    items.append({
                        'product': me.item_with_accomplisment(res.item_id ,self.language),
                        'instruction': me.get_item_instruction(res.item_id.name),
                        'description':res.item_id.description or False
                    })
                product_list.append({'category': translate_field(line,self.language), 'category_details': items})

            party_list['product_list'] = product_list

            if party_list:
                main.append(party_list)
        if main:
            return main
        else:
            return False
