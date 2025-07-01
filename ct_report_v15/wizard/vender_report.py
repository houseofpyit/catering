from odoo import api, models, fields,_
from odoo.exceptions import UserError
from odoo.addons.ct_function_v15.custom_utils import translate_field, location_field
from datetime import datetime, timedelta, time, date

class VenderReportWizard(models.TransientModel):
    _name = 'hop.vender.report.wizard'

    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    type = fields.Selection([('inhouse','In House'),('outsource','Out Source'),('service','Service'),('addons','Addons')],string="Type")
    function_ids = fields.Many2many('hop.function',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")
    vender_ids = fields.Many2many('res.partner',string="Vendor")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])

    @api.onchange('type','from_date','to_date')
    def onchange_function_ids(self):
        self.vender_ids = False
        d = []
        if self.type == 'inhouse':
            for line in self.env['hop.function'].search([('date','>=',self.from_date),('date','<=',self.to_date)]):
                for l in line.fuction_line_ids.mapped('insider_id').ids:
                    d.append(l)
        elif self.type == 'outsource':
            for line in self.env['hop.function'].search([('date','>=',self.from_date),('date','<=',self.to_date)]):
                for l in line.fuction_line_ids.mapped('out_sider_id').ids:
                    d.append(l)
        elif self.type == 'service':
            for line in self.env['hop.function'].search([('date','>=',self.from_date),('date','<=',self.to_date)]):
                for l in line.hospitality_line_ids.mapped('vender_id').ids:
                    d.append(l)
        elif self.type == 'addons':
            for line in self.env['hop.function'].search([('date','>=',self.from_date),('date','<=',self.to_date)]):
                for l in line.extra_service_line_ids.mapped('vender_id').ids:
                    d.append(l)
        if d :
            return {'domain': {'vender_ids': [('id', 'in', d)]}}
        else:
            return {'domain': {'vender_ids': [('id', '=', 0)]}}
    
    def in_house_out_source_report_create(self):
        sql = "delete from hop_fuction_line_report ;" 
        self._cr.execute(sql)
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        records = self.env['hop.function'].search(domain)
        print(records)
        filter = False
        for line in records:
            if self.type == 'inhouse':
                if self.vender_ids:
                    filter = lambda l: l.insider_id.id in self.vender_ids.ids
                else:
                    filter = lambda l: l.insider_id.id in line.fuction_line_ids.mapped('insider_id').ids
            if self.type == 'outsource':
                if self.vender_ids:
                    filter = lambda l: l.out_sider_id.id in self.vender_ids.ids
                else:
                    filter = lambda l: l.out_sider_id.id in line.fuction_line_ids.mapped('out_sider_id').ids
            for res in line.fuction_line_ids.filtered(filter):
                    vandor = False
                    if self.type == 'inhouse':
                        vandor = res.insider_id.id
                    if self.type == 'outsource':
                        vandor = res.out_sider_id.id
                    venue_address = res.fuction_id.venue_address
                    if res.fuction_id.remarks :
                        venue_address = venue_address + " ( Food Note : "+ res.fuction_id.remarks +" ) "
                    self.env['hop.fuction.line.report'].create({
                            'category_id': res.category_id.id,
                            'item_id': res.item_id.id,
                            'uom': res.uom.id,
                            'no_of_pax': res.no_of_pax,
                            'helper': res.helper,
                            'chief': res.chief,
                            'per_qty': res.per_qty,
                            'qty': res.qty,
                            'vender_id':vandor,
                            'cost': res.cost,
                            'rate': res.rate,
                            'instruction': res.instruction,
                            'date': res.fuction_id.date,
                            'venue_address': venue_address ,
                            'time':res.fuction_id.time,
                            'am_pm':res.fuction_id.am_pm,
                            'function_id':res.fuction_id.id,

                        })
    def addones_create(self):
        sql = "delete from hop_extra_service_line_report ;" 
        self._cr.execute(sql)
        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]
        records = self.env['hop.function'].search(domain)
        report_lines = []

        for line in records:
            filter_func = lambda l: l.vender_id.id in self.vender_ids.ids if self.vender_ids else True
            report_lines += [{
                'vender_id': res.vender_id.id,
                'service_id':  res.service_id.id,
                'uom_id': res.uom_id.id,
                'qty_ids': int(res.qty_ids),
                'price': res.price,
                'uom_id': res.uom_id.id,
                'date': res.date,
                'time': res.time,
                'am_pm': res.am_pm,
                'instruction': res.instruction,
                'date_fun': res.extra_service_id.date,
                'venue_address': res.extra_service_id.venue_address,
                'time_fun': res.extra_service_id.time,
                'am_pm_fun': res.extra_service_id.am_pm,
            } for res in line.extra_service_line_ids.filtered(filter_func)]

        if report_lines:
            self.env['hop.extra.service.line.report'].create(report_lines)
    
    def service_create(self):
        sql = "delete from hospitality_shift_line_report ;" 
        self._cr.execute(sql)
        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]
        records = self.env['hop.function'].search(domain)
        report_lines = []

        for line in records:
            filter_func = lambda l: l.vender_id.id in self.vender_ids.ids if self.vender_ids else True
            report_lines += [{
                'vender_id': res.vender_id.id,
                'hospitality_ids':  res.hospitality_ids.id,
                'service_id':res.service_id.id,
                'shift_date': res.shift_date,
                'shift_time': res.shift_time,
                'remarks': res.remarks,
                'location':res.location,
                'qty_person': int(res.qty_person),
                'uom_id': res.uom_id.id,
                'date': res.hs_id.date,
                'venue_address': res.hs_id.venue_address,
                'time': res.hs_id.time,
                'am_pm': res.hs_id.am_pm,
            } for res in line.hospitality_line_ids.filtered(filter_func)]

        if report_lines:
            self.env['hospitality.shift.line.report'].create(report_lines)
    def action_print(self):
        if self.type == 'inhouse' or self.type == 'outsource':
            self.in_house_out_source_report_create() 
            vals=  {
                            'type': 'ir.actions.act_window',
                            'target':'main',
                            'view_mode': 'tree',
                            'res_model': 'hop.fuction.line.report',
                            'context': "{'create': False,'edit':False,'group_by':['vender_id','date','venue_address']}"
                        }
            if self.type == 'inhouse':
                vals.update({'name': 'In-House',})
            elif self.type == 'outsource':
                vals.update({'name': 'Out-Source',})
            return vals
    
        elif self.type == 'service':
            self.service_create()
            group_by_fields = ['vender_id', 'date']
            return {
                'type': 'ir.actions.act_window',
                'target':'main',
                'name': 'Service',
                'view_mode': 'tree',
                'res_model': 'hospitality.shift.line.report',
                'context': {'create': False, 'edit': False, 'delete': False, 'group_by': group_by_fields}
            }
        
        elif self.type == 'addons':
            self.addones_create()
            group_by_fields = ['vender_id', 'date']
            return {
                'type': 'ir.actions.act_window',
                'target':'main',
                'name': 'Add-ons',
                'view_mode': 'tree',
                'res_model': 'hop.extra.service.line.report',
                'context': {'create': False, 'edit': False, 'delete': False, 'group_by': group_by_fields}
            }

    def create_pdf(self):
        print("**********************")
        if self.type == 'inhouse' or self.type == 'outsource':
            return self.env.ref('ct_report_v15.action_vendor_in_house_out_source_report').report_action(self)               
        if self.type == 'service':
            return self.env.ref('ct_report_v15.action_vendor_service_report').report_action(self)              
        elif self.type == 'addons':
            return self.env.ref('ct_report_v15.action_vendor_addons_report').report_action(self)  
                    

    def convert_to_24hr_time(self, time_str, am_pm):
        try:
            if not time_str or not am_pm:
                return None
            time_float = float(time_str)
            hours = int(time_float)
            minutes = int(round((time_float - hours) * 60)) 

            if minutes >= 60:
                raise ValueError("Invalid time format")

            time_str = f"{hours}:{minutes:02d}"

            time_obj = datetime.strptime(time_str, '%I:%M')
            if am_pm.lower() == 'pm' and time_obj.hour != 12:
                time_obj = time_obj.replace(hour=time_obj.hour + 12)
            elif am_pm.lower() == 'am' and time_obj.hour == 12:
                time_obj = time_obj.replace(hour=0)
            return time_obj.time()
        except (ValueError, TypeError) as e:
            print(f"Error: {e}")
            return None
        
    def create_pdf_vals(self):
        meal_dict = {
                'early_morning_tea': 'Early Morning Tea',
                'breakfast': 'Breakfast',
                'brunch': 'Brunch',
                'mini_meals': 'Mini Meals',
                'lunch': 'Lunch',
                'hi-tea': 'HI-TEA',
                'dinner': 'Dinner',
                'late_night_snacks': 'Late Night Snacks'
            }
        if self.type == 'inhouse' or self.type == 'outsource':
            self.in_house_out_source_report_create() 
            records = self.env['hop.fuction.line.report'].search([])
            main = []
            if records:
                vendors = records.mapped('vender_id')
                for vendor in vendors:
                    vender_data = []
                    unique_dates = records.filtered(lambda l: l.vender_id == vendor).mapped('date')
                    for date in sorted(set(unique_dates)):
                        # venues = records.filtered(lambda l: l.vender_id == vendor and l.date == date).mapped('venue_address')
                        # fun_time = records.filtered(lambda l: l.vender_id == vendor and l.date == date).mapped('time')
                        fun_time=[]
                        venues =[]
                        for tm in records.filtered(lambda l: l.vender_id == vendor and l.date == date):
                            fun_time.append({
                                'object':tm,"time":self.convert_to_24hr_time(tm.time,tm.am_pm),'venue_address':tm.venue_address
                            })
                        sorted_list = sorted(fun_time, key=lambda x: x['time'])
                        for m in sorted_list:
                            if m.get('time') not in fun_time:
                                fun_time.append(m.get('time'))
                            if m.get('venue_address') not in venues:
                                venues.append(m.get('venue_address'))
                        # fun_time=  [entry['object'].time for entry in sorted_list]
                        address_data = []
                        for t in fun_time:
                            for venue in venues:
                                data = []
                                for am_pm_value in ['am', 'pm']:
                                    filtered_records = records.filtered(lambda l: l.vender_id == vendor and l.date == date and l.venue_address == venue and self.convert_to_24hr_time(l.time,l.am_pm) == t and l.am_pm == am_pm_value)
                                    sorted_records = sorted(filtered_records, key=lambda l: l.time)
                                    for res in sorted_records:
                                        data.append({
                                            'category': translate_field(res.category_id , self.language),
                                            # 'company_id': res.company_id.logo,
                                            'item': translate_field(res.item_id , self.language),
                                            'uom': res.uom.name,
                                            'no_of_pax': res.no_of_pax,
                                            'helper': res.helper,
                                            'chief': res.chief,
                                            'per_qty': res.per_qty,
                                            'qty': res.qty,
                                            'vender':translate_field(res.vender_id , self.language),
                                            'cost': res.cost,
                                            'rate': res.rate,
                                            'instruction': res.instruction,
                                            'date': res.date,
                                            'venue_address': res.venue_address,
                                            'time':res.time,
                                            'am_pm': dict(res._fields['am_pm'].selection).get(res.am_pm),
                                            'meal_type':meal_dict.get(res.function_id.meal_type),

                                    })
                                if data:
                                    data = sorted(data, key=lambda x: x['category'])
                                    address_data.append({'address': venue, 'vender_data': data})
                        if address_data:
                            # vender_data.append({
                            #                     'date': date.strftime('%d/%m/%Y') + ' ' +
                            #                             f"{int(filtered_records.function_id.time):02d}:" +
                            #                             f"{int((filtered_records.function_id.time % 1) * 60):02d} " +
                            #                             f"{'AM' if filtered_records.function_id.am_pm == 'am' else 'PM'}" +
                            #                             (' (' + filtered_records.function_id.remarks + ')' if filtered_records.function_id.remarks else ''),
                            #                     'date_wish_data': address_data
                            #                 })
                            vender_data.append({
                                            'date': date.strftime('%d/%m/%Y') + ' ' +
                                                    f"{int(filtered_records.function_id.time):02d}:" +
                                                    f"{int((filtered_records.function_id.time % 1) * 60):02d} " +
                                                    f"{'AM' if filtered_records.function_id.am_pm == 'am' else 'PM'}" ,
                                            'date_wish_data': address_data
                                        })
                    main.append({'company_id':self.company_id.logo if self.company_id.logo else False,'from_date':self.from_date.strftime('%d/%m/%Y'),'to_date':self.to_date.strftime('%d/%m/%Y'),'vender_name': vendor.name, 'data': vender_data})
            return main

        if self.type == 'service':
            self.service_create()
            records = self.env['hospitality.shift.line.report'].search([])

            main = []

            if records:
                vendors = records.mapped('vender_id')
                for vendor in vendors:
                    vender_data = []
                    unique_dates = records.filtered(lambda l: l.vender_id == vendor).mapped('date')
                    for date in sorted(set(unique_dates)):
                        venues = records.filtered(lambda l: l.vender_id == vendor and l.date == date).mapped('venue_address')
                        address_data = []
                        for venue in set(venues):
                            filtered_records = records.filtered(lambda l: l.vender_id == vendor and l.date == date and l.venue_address == venue)
                            data = []
                            for rec in filtered_records:
                                data.append({
                                    'vender': translate_field(rec.vender_id , self.language),
                                    # 'company_id': rec.company_id.logo,
                                    'service':translate_field(rec.service_id , self.language),
                                    'hospitality': rec.hospitality_ids.name,
                                    'shift_date': rec.shift_date.strftime('%d/%m/%Y'),
                                    'shift_time': rec.shift_time,
                                    'remarks': rec.remarks,
                                    'location': location_field(rec.location,self.language,rec),
                                    'qty_person': int(rec.qty_person),
                                    'uom_id': rec.uom_id.name,
                                    'date': rec.date.strftime('%d/%m/%Y'),
                                    'venue_address': rec.venue_address,
                                    'time': rec.time,
                                    'am_pm': dict(rec._fields['am_pm'].selection).get(rec.am_pm),
                                })
                            address_data.append({'address': venue, 'vender_data': data})
                        vender_data.append({'date': date.strftime('%d/%m/%Y'), 'date_wish_data': address_data})
                    main.append({'company_id':self.company_id.logo if self.company_id.logo else False,'from_date':self.from_date.strftime('%d/%m/%Y'),'to_date':self.to_date.strftime('%d/%m/%Y'),'vender_name': vendor.name, 'data': vender_data})
            print("...................",main)
            return main


    
        # elif self.type == 'service':
        #     self.service_create()
        #     records = self.env['hospitality.shift.line.report'].search([])
        #     list=[]
        #     if records:
        #         main=[]
        #         vander=[]
        #         for record in records.mapped('vender_id'):
        #             p={'party':record.name}
        #             unique_dates = records.filtered(lambda l: l.vender_id.id == record.id).mapped('date')
        #             p={}
        #             for line in sorted(set(unique_dates)):
        #                 unique_venues = records.filtered(lambda l: l.vender_id.id == record.id and l.date == line).mapped('venue_address')
        #                 x={}
        #                 for venue in set(unique_venues):
                        
        #                     filtered_records = records.filtered(lambda l: l.vender_id.id == record.id and l.date == line and l.venue_address == venue)
        #                     data = []
        #                     for rec in filtered_records:
        #                         data.append(
        #                             {
        #                                 'vender': rec.vender_id.name,
        #                                 'hospitality':  rec.hospitality_ids.name,
        #                                 'shift_date': rec.shift_date.strftime('%d/%m/%Y'),
        #                                 'shift_time': rec.shift_time,
        #                                 'remarks': rec.remarks,
        #                                 'location': location_field(res.location,self.language,res),
        #                                 'qty_person': rec.qty_person,
        #                                 'uom_id': rec.uom_id.name,
        #                                 'date': rec.date.strftime('%d/%m/%Y'),
        #                                 'venue_address': rec.venue_address,
        #                                 'time': rec.time,
        #                                 'am_pm': rec.am_pm,
        #                             }
        #                         )
                        
        #                     x.update({'address':venue,"vender_data":data})
        #                 p.update({'date':line.strftime('%d/%m/%Y'),'date_wish_data':x})
        #                 vander.append(p)
        #             main.append({'vender_name':record.name,'data':vander})
        #         print(main)
     
        

            # else:
            #     raise UserError("No Record Found............")
            
        elif self.type == 'addons':
            self.addones_create()

            records = self.env['hop.extra.service.line.report'].search([])
            main = []
            if records:
                vendors = records.mapped('vender_id')
                for vendor in vendors:
                    vender_data = []
                    unique_dates = records.filtered(lambda l: l.vender_id == vendor).mapped('date_fun')
                    for date in sorted(set(unique_dates)):
                        venues = records.filtered(lambda l: l.vender_id == vendor and l.date_fun == date).mapped('venue_address')
                        address_data = []
                        for venue in set(venues):
                            filtered_records = records.filtered(lambda l: l.vender_id == vendor and l.date_fun == date and l.venue_address == venue)
                            data = []
                            for res in filtered_records:
                                data.append({
                                        'vender': translate_field(res.vender_id , self.language),
                                        # 'company_id': res.company_id.logo,
                                        'service':  translate_field(res.service_id , self.language),
                                        'uom': res.uom_id.name,
                                        'qty_ids': res.qty_ids,
                                        'price': res.price,
                                        'date': res.date.strftime('%d/%m/%Y'),
                                        'time': res.time,
                                        'am_pm': dict(res._fields['am_pm'].selection).get(res.am_pm),
                                        'instruction': res.instruction,
                                        'date_fun': res.date_fun,
                                        'venue_address': res.venue_address,
                                        'time_fun': res.time_fun,
                                        'am_pm_fun': dict(res._fields['am_pm_fun'].selection).get(res.am_pm_fun),
                                })
                            address_data.append({'address': venue, 'vender_data': data})
                        vender_data.append({'date': date.strftime('%d/%m/%Y'), 'date_wish_data': address_data})
                    main.append({'company_id':self.company_id.logo if self.company_id.logo else False,'from_date':self.from_date.strftime('%d/%m/%Y'),'to_date':self.to_date.strftime('%d/%m/%Y'),'vender_name': vendor.name, 'data': vender_data})
            print("...............",main)
            return main             
            

class HopFunctionLineReport(models.Model):
    _name = "hop.fuction.line.report"

    category_id = fields.Many2one('hop.recipes.category',string="Category",track_visibility='onchange')
    item_id = fields.Many2one('hop.recipes',string="Item Name",track_visibility='onchange')
    no_of_pax = fields.Integer(string="No Of Pax",track_visibility='onchange')
    per_qty = fields.Float(string="Per Head Qty",track_visibility='onchange')
    qty = fields.Float(string="Qty",track_visibility='onchange')
    uom = fields.Many2one('uom.uom',string="Uom",track_visibility='onchange')
    vender_id = fields.Many2one('res.partner',"Vendor")
    cost = fields.Float(string="Cost",track_visibility='onchange')
    rate = fields.Float(string="Rate",track_visibility='onchange')
    instruction = fields.Char(string="Instruction",track_visibility='onchange')
    date = fields.Date("Date")
    helper = fields.Integer(string="Helper")
    chief = fields.Integer(string="Chief")
    venue_address = fields.Text('Venue Address')
    time = fields.Float(string="Time",tracking=True)
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
    function_id = fields.Many2one('hop.function',string="Function")


class HospitalityShiftLineReport(models.Model):
    _name = 'hospitality.shift.line.report'
    _description = 'Hospitality Shift Line'

    vender_id = fields.Many2one('res.partner',string="Vender Name",domain=[('is_vender','=',True)] ,tracking=True)
    service_id = fields.Many2one('product.product', string='Vendor Category',track_visibility='onchange')
    hospitality_ids = fields.Many2one('ct.hospitality.shift',string="Hospitality Shift",tracking=True)
    shift_date = fields.Date(string="Shift Date")
    shift_time = fields.Float(string="Shift Time")
    remarks = fields.Char(string="Shift Remarks")
    location = fields.Selection([
        ('add_venue', "At Venue"),
        ('add_godown', "At Godown")], default=False, string="Location")
    qty_person = fields.Float(string="Quantity/Person")
    uom_id = fields.Many2one('uom.uom', string="UOM")
    date = fields.Date("Date")
    venue_address = fields.Text('Venue Address')
    time = fields.Float(string="Time",tracking=True)
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)


class HospitalityShiftLineReport(models.Model):
    _name = 'hop.extra.service.line.report'
    _description = 'Extra Service Line'

    vender_id = fields.Many2one('res.partner',string="Vender Name",domain=[('is_vender','=',True)] ,tracking=True)
    service_id = fields.Many2one('product.product', string='Vendor Category',track_visibility='onchange',required=True)
    qty_ids = fields.Float(string="Quantity/Person",tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UoM')
    price = fields.Float(string="Price",tracking=True)
    date = fields.Date(string="Date")
    time = fields.Float(string="Time")
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    instruction = fields.Char(string="Instruction",track_visibility='onchange')
    date_fun = fields.Date("Date")
    venue_address = fields.Text('Venue Address')
    time_fun = fields.Float(string="Time",tracking=True)
    am_pm_fun = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)


