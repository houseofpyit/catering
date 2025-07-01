from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons.ct_function_v15.custom_utils import translate_field, meal_type,location_field

class ConfirmInHouseServiceReport(models.TransientModel):
    _name = 'hop.confirm.in.house.service.report.wizard'

    fuction_ids = fields.Many2many('hop.function',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])
    # date = fields.Date(string="Date",default=fields.Date.context_today)

    def in_house_vals(self):
        # domain = [('date','=',self.date)]
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        if self.fuction_ids:
            domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        print(functions)
        if not functions:
            raise UserError("No Record Found............")
        main=[]
        for fun in functions:
            party_list={}
            t = False
            if fun.am_pm == 'am':
                t =f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}" + ' PM'
            party_list.update({'party_name':translate_field(fun.party_name_id, self.language),
                              'company_id': fun.company_id.logo if fun.company_id.logo else False,
                              'party_number':fun.mobile_num,
                              'emergency_contact':fun.emergency_contact,
                              'venue_address':fun.venue_address,
                              'fuction_name':translate_field(fun.fuction_name_id , self.language),
                              'date':fun.date,
                              'meal_type': meal_type(fun.meal_type,self.language,fun),
                              'time':t,
                              'remarks':fun.remarks,
                              'no_of_pax':int(fun.no_of_pax),
                              'manager_name':translate_field(fun.manager_name_id , self.language),
                              'phone':fun.manager_name_id.phone,
                              })
            list=[]
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
                                    'category':translate_field(line.category_id, self.language),
                                    'work':translate_field(line.item_id, self.language),
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
            party_list.update({'services_detail':service_list})
            main.append(party_list)

        return main
    
    def action_print(self):
        return self.env.ref('ct_report_v15.action_confirm_in_house_menu_and_service').report_action(self)
            