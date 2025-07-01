from odoo import api, models, fields,_
from odoo.exceptions import UserError
from datetime import datetime,date

class MenuReportWizard(models.TransientModel):
    _name = 'hop.menu.report.wizard'


    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    fuction_ids = fields.Many2many('hop.function','ref_menu_fuction_ids',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")

    def action_print_vals(self):
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        if self.fuction_ids:
            domain.append(('id','in',self.fuction_ids.ids))


        functions = self.env['hop.function'].search(domain)

        main = []
        if not functions:
            raise UserError("No Record Found............")

        for fun in functions:
            party_list={}
            t= False
            if fun.am_pm == 'am':
                t =f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}" + ' AM'
            else:
                t = f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}" + ' PM'
            party_list.update({'party_name':fun.party_name_id.name,
                              'company_id': fun.company_id.logo if fun.company_id.logo else False,
                              'emergency_contact':fun.emergency_contact,
                              'venue_address':fun.venue_address,
                              'fuction_name':fun.fuction_name_id.name,
                              'date':fun.date,
                              'meal_type':dict(fun._fields['meal_type'].selection).get(fun.meal_type),
                              'time':t,
                              'remarks':fun.remarks,
                              'no_of_pax':fun.no_of_pax,
                              'manager_name':fun.manager_name_id.name,
                              'phone':fun.manager_name_id.phone,
                              })
            menu_list = []
            for menu in fun.fuction_line_ids:
                vender = False
                contact = False
                in_out= False
                if menu.insider_id:
                    vender = menu.insider_id.name
                    contact = menu.insider_id.phone
                    in_out = "In-House"
                else:
                    vender = menu.out_sider_id.name
                    contact = menu.out_sider_id.phone
                    in_out = "Out-source"
                menu_list.append({
                   'category' : menu.category_id.name,
                   'item_id' : menu.item_id.name,
                   'no_of_pax': menu.no_of_pax,
                   'instruction':menu.instruction,
                   'vender': vender,
                   'in_out': in_out,
                   'contact':contact,
                })
            party_list.update({'menu_detail':menu_list})

            service_list = []
            for ser in fun.hospitality_line_ids:
                service_list.append({
                    'service': ser.service_id.name,
                    'shift':ser.hospitality_ids.name,
                    'shift_date':ser.shift_date,
                    'shift_time': f"{int(ser.shift_time):02d}:{int((ser.shift_time % 1) * 60):02d}" ,
                    'qty': int(ser.qty_person),
                    'uom':ser.uom_id.name,
                    'remarks' : ser.remarks,
                    'vender_name': ser.vender_id.name,
                    'vender_number':ser.vender_id.phone
                })
            party_list.update({'services_detail':service_list})
            addons_list = []
            for addons in fun.extra_service_line_ids:
                t = False
                if fun.am_pm == 'am':
                    t =f"{int(addons.time):02d}:{int((addons.time % 1) * 60):02d}" + ' AM'
                else:
                    t = f"{int(addons.time):02d}:{int((addons.time % 1) * 60):02d}" + ' PM'
                addons_list.append({
                    'service': addons.service_id.name,
                    'date':addons.date,
                    'time':t,
                    'qty': int(addons.qty_ids),
                    'uom':addons.uom_id.name,
                    'price':addons.price,
                    'vender_name': addons.vender_id.name,
                    'vender_number':addons.vender_id.phone
                })

            party_list.update({'addons_detail':addons_list})
            main.append(party_list)

        return main
    
    def action_print(self):
     return self.env.ref('ct_report_v15.action_manu').report_action(self)