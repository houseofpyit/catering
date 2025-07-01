from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.addons.ct_function_v15.custom_utils import translate_field,meal_type

class VenderConfirmationFromWizard(models.TransientModel):
    _name = 'hop.vender.confirmation.from.wizard'

    from_date = fields.Date(string="From Date", default=fields.Date.context_today)
    to_date = fields.Date(string="To Date", default=fields.Date.context_today)
    fuction_ids = fields.Many2many('hop.function', 'ref_hop_vender_confirmation_fuction_ids',
                                   string="Function", domain="[('date','>=',from_date),('date','<=',to_date)]")
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])
    
    def vender_confirmation_vals(self):
        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]
        if self.fuction_ids:
            domain.append(('id', 'in', self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        if not functions:
            raise UserError("No Record Found............")
        
        main = []
        
        for raw_rec in functions:
            line = self.prepare_basic_data(raw_rec)
            line['in_house'] = self.prepare_vendor_data(raw_rec.fuction_line_ids, 'insider_id')
            line['out_source'] = self.prepare_vendor_data(raw_rec.fuction_line_ids, 'out_sider_id')
            line['hospitality_list'] = self.prepare_service_data(raw_rec.hospitality_line_ids)
            line['addons_list'] = self.prepare_addons_data(raw_rec.extra_service_line_ids)
            
            main.append(line)
            
        # datas = {
        #     'ids': self.ids,
        #     'form': self.ids,
        #     'model': 'hop.vender.confirmation.from.wizard',
        #     'data': main,
        # }
        return main
    
    def action_print(self):
        return self.env.ref('ct_report_v15.action_vendor_confirmation_report').report_action(self)
    
    def prepare_basic_data(self, raw_rec):
        t = self.format_time(raw_rec.time, raw_rec.am_pm)
        return {
            'company_id': raw_rec.company_id.logo if raw_rec.company_id.logo else False,
            'party_name': translate_field(raw_rec.party_name_id , self.language),
            'party_number': raw_rec.mobile_num,
            'emergency_contact': raw_rec.emergency_contact,
            'venue_address': raw_rec.venue_address,
            'fuction_name': translate_field(raw_rec.fuction_name_id , self.language),
            'date': raw_rec.date,
            'meal_type': meal_type(raw_rec.meal_type,self.language,raw_rec),
            'time': t,
            'remarks': raw_rec.remarks,
            'no_of_pax': raw_rec.no_of_pax,
            'manager_name': translate_field(raw_rec.manager_name_id , self.language),
            'phone': raw_rec.manager_name_id.phone,
        }
    
    def prepare_vendor_data(self, lines, vendor_type):
        vendor_list = []
        
        for vender in lines.mapped(vendor_type):
            menu_list = []
            for fun in lines.filtered(lambda l: getattr(l, vendor_type).id == vender.id):
                menu_list.append({
                    'category': translate_field(fun.category_id, self.language),
                    'work': translate_field(fun.item_id , self.language),
                    'no_of_pax': fun.no_of_pax,
                    'helper': fun.helper,
                    'chief': fun.chief,
                    'instruction': fun.instruction,
                    'qty':fun.qty,
                })
            
            vendor_list.append({translate_field(vender , self.language) +'('+ str(vender.phone) +')':menu_list})
        
        return vendor_list
    
    def prepare_service_data(self, hospitality_lines):
        service_list = []
        
        for vender in hospitality_lines.mapped('vender_id'):
            service_entries = []
            for ser in hospitality_lines.filtered(lambda l: l.vender_id.id == vender.id):
                service_entries.append({
                    'service': translate_field(ser.service_id.product_tmpl_id , self.language),
                    'shift': ser.hospitality_ids.name,
                    'shift_date': ser.shift_date,
                    'shift_time': self.format_time(ser.shift_time),
                    'qty': int(ser.qty_person),
                    'uom': ser.uom_id.name,
                    'remarks': ser.remarks,
                })
            
            service_list.append({translate_field(vender , self.language) +'('+ str(vender.phone) +')':service_entries})
        
        return service_list
    
    def prepare_addons_data(self, addons_lines):
        addons_list = []
        
        for vender in addons_lines.mapped('vender_id'):
            addons_entries = []
            for addons in addons_lines.filtered(lambda l: l.vender_id.id == vender.id):
                t = self.format_time(addons.time)
                addons_entries.append({
                    'service': translate_field(addons.service_id.product_tmpl_id , self.language),
                    'date': addons.date,
                    'time': t,
                    'qty': int(addons.qty_ids),
                    'uom': addons.uom_id.name,
                    'price': addons.price,
                    'instruction': addons.instruction,
                })
            
            addons_list.append({translate_field(vender , self.language) +'('+ str(vender.phone) +')':addons_entries})
        
        return addons_list
    
    def format_time(self, raw_time, raw_am_pm=None):
        if raw_am_pm is None:
            return f"{int(raw_time):02d}:{int((raw_time % 1) * 60):02d}"
        
        formatted_time = self.format_time(raw_time)
        formatted_time += ' AM' if raw_am_pm == 'am' else ' PM'
        
        return formatted_time
