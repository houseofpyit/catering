from odoo import api, models, fields, _
from datetime import date
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from datetime import datetime, timedelta, time, date
import pytz
from lxml import etree
import json
from odoo.addons.ct_function_v15.custom_utils import translate_field 


class hoplead(models.Model):
    _name = "hop.lead"
    _inherit = ['mail.thread']
    _rec_name = "party_name_id"

    name = fields.Char(string="Number", required=True, copy=False, default='New',tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    stage = fields.Selection([('details','Details'),('create_menu','Menu Created'),('addons','Add-ons'),('quotation','Quotation'),('production','Menu Confirmed'),('cancel','Cancel')],string="Stage",default="details",tracking=True)
    party_name_id = fields.Many2one('res.partner',string="Party Name",tracking=True,domain=[('is_customer','=',True)],readonly=True,stage={'production': [('readonly', False)]})
    mobile_num = fields.Char(string="Mobile Number",tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    fuction_name_id = fields.Many2one('hop.function.mst',string="Function Name",tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    date = fields.Date(string="Function Date",default=fields.Date.context_today,tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    emergency_contact = fields.Text(string="Emergency Contact",tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    remarks = fields.Text(string="Remarks",tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type",tracking=True)
    no_of_pax = fields.Integer(string="No Of Pax",tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    time = fields.Float(string="Time",tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    venue_address = fields.Text('Venue Address',tracking=True)
    manager_name_id = fields.Many2one('res.partner',string="Manager Name",domain=[('is_vender','=',True)],default=lambda self:self.env.user.company_id.manager_name_id,tracking=True,stage={'production': [('readonly', False)]})

    hop_funtion_id = fields.Many2one('hop.function',string="Hop Funtion")
    order_count = fields.Integer(string='Order', compute='_cumpute_order_count',readonly=True)

    vender_id = fields.Many2one('res.partner',string="Vendor",domain=[('is_vender','=',True)],readonly=False,stage={'production': [('readonly', False)]})
    service_id = fields.Many2one('product.product', string='Service',tracking=True, domain=[('is_service','=',True)],readonly=False,stage={'production': [('readonly', False)]})
    hospitality_ids = fields.Many2many('ct.hospitality.shift',string="Hospitality Shift",tracking=True,readonly=False,stage={'production': [('readonly', False)]})

    fuction_line_ids = fields.One2many('hop.fuction.lead.line', 'lead_id',string="Function Line",tracking=True)
    hospitality_line_ids = fields.One2many('hospitality.shift.lead.line', 'hs_id',string="Hospitality Shift Line",tracking=True,readonly=False,stage={'production': [('readonly', False)]})
    accompplishment_line_ids = fields.One2many('hop.accomplishment.lead.line','function_id',string="Accomplishment Line",readonly=False,stage={'production': [('readonly', True)]})
    extra_service_line_ids = fields.One2many('hop.extra.service.lead.line', 'extra_service_id',string="Extra Service Line",tracking=True,readonly=True,stage={'production': [('readonly', False)]})
    recipes_ids = fields.Many2many('hop.recipes','ref_recipes_ids_function_ref',string="Recipes Name",track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id)
    stage_check = fields.Selection([('create_menu','Menu Created'),('production','Menu Confirmed')],string="Stage",compute='_compute_stage_check')
    calendar_id = fields.Many2one('hop.calendar',string="Calender")
    calendar_line_id = fields.Many2one('hop.calendar.line',string="Calender line")
    accompplishment_visible = fields.Boolean("Accompplishment Visible" ,compute='_compute_accompplishment_visible')
    quot_count = fields.Integer(string="Quotation",compute='_compute_quotation_order')
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")
    open_oder = fields.Boolean(default=False,string="Open Order")
    without_description = fields.Boolean("Without Description",default=False)
    notes = fields.Text(string="Notes")

    menu_cost = fields.Float(string="Menu Cost",compute='_cumpute_cost')
    labour_cost = fields.Float(string="Labour Cost",compute='_cumpute_cost')
    add_ons_cost = fields.Float(string="Add-Ons Cost",compute='_cumpute_cost')
    total_cost = fields.Float(string="Total Cost",compute='_cumpute_cost')

    @api.onchange('fuction_line_ids','hospitality_line_ids','accompplishment_line_ids','extra_service_line_ids')
    @api.depends('fuction_line_ids','hospitality_line_ids','accompplishment_line_ids','extra_service_line_ids')
    def _cumpute_cost(self):
        self.menu_cost = sum(self.fuction_line_ids.mapped('total_cost'))
        self.labour_cost = sum(self.hospitality_line_ids.mapped('cost'))
        self.add_ons_cost = sum(self.extra_service_line_ids.mapped('cost'))
        self.total_cost = self.menu_cost + self.labour_cost + self.add_ons_cost
        
    
    def set_to_draft(self):
        lead = self.env[self.env.context['active_model']].search([('id','=',self.env.context['active_id'])])
        if lead:
            if lead.hop_funtion_id:
                po_records  = self.env['purchase.order'].search([('fuction_id_rec','=',lead.hop_funtion_id.ids[0])])
                for order in po_records:
                    order.state = 'cancel'
                    order.unlink()
                utensils_rec = self.env['utensils.mst'].search([('function_id','=', lead.hop_funtion_id.ids[0])])        
                print(utensils_rec)
                for utensils in utensils_rec:
                    utensils.stage = 'cancel'
                    utensils.unlink()
            quot_count = self.env['sale.order'].search([('lead_id','=',lead.id)])
            for order in quot_count:
                order.state = 'cancel'
                order.unlink()
        lead.hop_funtion_id.active = False
        lead.stage = 'details'

    @api.onchange('date')
    def _onchange_date(self):  
        current_date = datetime.now().date()
        if  self.date:
            if  self.date < current_date:
                raise UserError("Can't Select Previous Date!!!!")
    
    @api.depends('quot_count')   
    def _compute_quotation_order(self):
        self.quot_count = self.env['sale.order'].search_count([('lead_id','=',self.id)])

    @api.model
    def action_cancel(self):
        vals = {"model":'hop.lead','id':self.ids}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel',
            'view_mode': 'form',
            'res_model': 'hop.cancel',
            'target':'new',
            'context':vals
        }

    def cancel(self,reason):

        function = self.env['hop.function'].search([('hop_lead_id','=',self.ids),('stage','!=','cancel')])
        if function:
            raise UserError('First Cancel Confirmed Orders Details')     
        records  = self.env['sale.order'].search([('lead_id','=',self.id),('state','!=','cancel')]) 
        for order in records:
            # order.action_cancel()  
            order.state = 'cancel'
            order.active = False
            order.unlink()
        self.env['hop.cancel.report'].create({
            'party_id': self.party_name_id.id,
            'date': self.date,
            'meal_type': self.meal_type,
            'cancel_type': 'Menu Planner',
            'no_of_pax' : self.no_of_pax,
            'venue_address': self.venue_address,
            'reason' :reason,
        })
        self.stage = 'cancel'
        self.calendar_line_id.active = False
        if len(self.calendar_id.calendar_line_ids.filtered(lambda l: l.active == True)) == 0:
            self.calendar_id.active = False  
        self.active = False   
        
    @api.onchange('stage')
    def _onchange_stage(self):
        required_fields = [self.party_name_id, self.mobile_num, self.fuction_name_id, self.date, self.meal_type,self.am_pm]
        if self.stage in ["create_menu", "production"] and (not all(required_fields) or self.no_of_pax <= 0 or self.time <= 0):
            raise UserError('Fill all the details first')
        if self.stage == 'details':
            if self.id:
                record = self.env['sale.order'].search([('lead_id','=',self.ids[0])])
                if record:
                    record.unlink()
    def unlink(self):
        for res in self:
            search_quotation = self.env['sale.order'].search([('lead_id','=',res.id)])
            search_production = self.env['hop.function'].search([('hop_lead_id','=',res.id)])
            if search_quotation:
                raise UserError(("already send quotation"))
            if search_production:
                raise UserError(("already send Production"))
        return super(hoplead,self).unlink()
    
    def create_menu(self):
        self.stage = "create_menu"
        if self.calendar_line_id:
            self.calendar_line_id.state = "create_menu"
            self.calendar_line_id._compute_color()
    def create_addons(self):
        if len(self.fuction_line_ids) == 0:
            raise UserError(("Menu is required! You can not set it empty."))
        self.stage = "addons"
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }

    def create_quotation(self):
        for q in self.extra_service_line_ids:
            if q.qty_ids <=0:
                raise UserError('kindly add Quantity/Person in Add-ons..')
        order_line = []
        record = self.env['sale.order'].search([('lead_id','=',self.id),('state','!=','cancel')])
        # if record:
        #     for rec in record:
        #         if rec.state not in  ('done','cancel'):
        #             rec.action_cancel()
        product = False

        if self.meal_type == 'early_morning_tea':
            product = self.env.ref('ct_function_v15.meal_1')
        elif self.meal_type == 'breakfast':
            product = self.env.ref('ct_function_v15.meal_2')
        elif self.meal_type == 'brunch':
            product = self.env.ref('ct_function_v15.meal_3')
        elif self.meal_type == 'lunch':
            product = self.env.ref('ct_function_v15.meal_4')
        elif self.meal_type == 'hi-tea':
            product = self.env.ref('ct_function_v15.meal_5')
        elif self.meal_type == 'dinner':
            product = self.env.ref('ct_function_v15.meal_6')
        elif self.meal_type == 'late_night_snacks':
            product = self.env.ref('ct_function_v15.meal_7')
        elif self.meal_type == 'mini_meals':
            product = self.env.ref('ct_function_v15.meal_8')

        if record:
            
            price = False
            last_record =  self.env['sale.order'].search([('lead_id','=',self.id),('state','!=','cancel')])
            if last_record:
                for rec in last_record:
                    flg = False
                    for line in rec.order_line: 
                        if line.product_id.id == product.id:
                            price = line.price_unit
                            flg = True
                            break
                    if flg :
                        break 
            if not price:
                records = self.env['sale.order'].search([('partner_id','=',self.party_name_id.id)],order="id desc")
                for rec in records:
                    flg = False
                    for line in rec.order_line: 
                        if line.product_id.id == product.id:
                            price = line.price_unit
                            flg = True
                            break
                    if flg :
                        break 
            if price == False:
                price = 1
            record.order_line = False
            order_line =[]
            if self.fuction_name_id:
                order_line.append((0, 0, {
                                        'name':self.remarks if self.remarks else '',
                                        'product_id': product.id,
                                        'product_uom_qty':self.no_of_pax,
                                        'product_uom': product.uom_id.id,
                                        'price_unit':price,
                                        'is_manu_planner':True
                                        }))
            for line  in self.extra_service_line_ids:
                order_line.append((0, 0, {
                                    'name':line.instruction if line.instruction else '',
                                    'product_id': line.service_id.id,
                                    'product_uom_qty': line.qty_ids,
                                    'product_uom': line.uom_id.id,
                                    'price_unit': line.price,
                                    'is_manu_planner':True
                                    }))
            record.write({
                'partner_id': self.party_name_id.id,
                'date_order': self.date,
                'lead_id':self.id,
                'order_line': order_line,
                'state' : 'draft',
                'fun_date': self.date,
                'meal_type' : self.meal_type,
                'venue_address': self.venue_address, 
            })
            return {
                    'name': 'Quotations',
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.order',
                    'view_mode': 'form',
                    'res_id': record.id,
                    'target':'current',
                } 

        else:
            if self.fuction_name_id:
                # price = False
                # records = self.env['sale.order'].search([('partner_id','=',self.party_name_id.id)],order="id desc")
                # print(records)
                # for rec in records:
                #     flg = False
                #     for line in rec.order_line: 
                #         if line.product_id.id == product.id:
                #             price = line.price_unit
                #             print(line.price_unit)
                #             flg = True
                #             break
                #     if flg :
                #         break 
                # if price == False:
                #     price = 1
                order_line.append((0, 0, {
                                        'name':self.remarks if self.remarks else '',
                                        'product_id': product.id,
                                        'product_uom_qty':self.no_of_pax,
                                        'product_uom': product.uom_id.id,
                                        # 'price_unit':price,
                                        'is_manu_planner':True
                                        }))
            for line  in self.extra_service_line_ids:
                if line.service_id:
                    order_line.append((0, 0, {
                                        'name':line.instruction if line.instruction else '',
                                        'product_id': line.service_id.id,
                                        'product_uom_qty': line.qty_ids,
                                        'product_uom': line.uom_id.id,
                                        'price_unit': line.price,
                                        'is_manu_planner':True
                                        }))
            new  = self.env['sale.order'].create({
                'partner_id': self.party_name_id.id,
                'date': self.date,
                'remarks': self.remarks,
                'lead_id':self.id,
                'order_line': order_line,
                'name':self.name,
                'fun_date': self.date,
                'meal_type' : self.meal_type,
                'venue_address': self.venue_address, 
            })
            # if record:
            #     l = len(record)
            #     new.write({'name':new.name+' - '+str(l)})
            self.stage = "quotation"
            return {
                    'name': 'Quotations',
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.order',
                    'view_mode': 'form',
                    'res_id': new.id,
                    'target':'current',
                }     
            
    def fetch_menu(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ct_function_v15.action_fetch_menu")
        action['context'] = {'active_id': self.env.context['active_id'],
                             'active_model': self.env.context['active_model']}
        return action

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(hoplead, self).fields_view_get(view_id=view_id,
                                                    view_type=view_type,
                                                    toolbar=toolbar,
                                                    submenu=submenu)
        if self.env.context.get('lead_id',False):
            record = self.env['hop.lead'].search([('id','=',self.env.context.get('lead_id',False))])
            if record:
                if record.stage == "addons":
                    doc = etree.XML(res['arch'])
                    for node in doc.xpath("//page[@name='addons']"):
                        node.set("autofocus", "autofocus")
                        modifiers = json.loads(node.get("modifiers"))
                        modifiers['autofocus'] = True
                        node.set("modifiers", json.dumps(modifiers))
                    res['arch'] = etree.tostring(doc)

        if self.env.context.get('params',False):
            record = self.env['hop.lead'].search([('id','=',self.env.context.get('params',False).get('id'))])
            if record:
                if record.stage == "addons":
                    doc = etree.XML(res['arch'])
                    for node in doc.xpath("//page[@name='addons']"):
                        node.set("autofocus", "autofocus")
                        modifiers = json.loads(node.get("modifiers"))
                        modifiers['autofocus'] = True
                        node.set("modifiers", json.dumps(modifiers))
                    res['arch'] = etree.tostring(doc)
        return res     
    
    def convert_to_24hr_time(self, time_str, am_pm):
        try:
            if not time_str or not am_pm:
                return None

            # Convert the input to a float and split into hours and minutes
            time_float = float(time_str)
            hours = int(time_float)
            minutes = int(round((time_float - hours) * 60))  # Convert fractional hours to minutes

            # Ensure minutes are valid
            if minutes >= 60:
                raise ValueError("Invalid time format")

            # Construct time string
            time_str = f"{hours}:{minutes:02d}"

            # Parse and adjust for AM/PM
            time_obj = datetime.strptime(time_str, '%I:%M')
            if am_pm.lower() == 'pm' and time_obj.hour != 12:
                time_obj = time_obj.replace(hour=time_obj.hour + 12)
            elif am_pm.lower() == 'am' and time_obj.hour == 12:
                time_obj = time_obj.replace(hour=0)
            return time_obj.time()
        except (ValueError, TypeError) as e:
            print(f"Error: {e}")
            return None
    
    def sort_list(self,record):
        list_record=[]
        for line in record:
            list_record.append({
                'object':line,"time":self.convert_to_24hr_time(line.lead_id.time,line.lead_id.am_pm)
            })
        sorted_list = sorted(list_record, key=lambda x: x['time'])
        return [entry['object'] for entry in sorted_list]

    
    # def get_menu_item(self):
    #     party_list={}
    #     list=[]
    #     sorted_lines = self.fuction_line_ids.sorted(
    #         key=lambda l: (getattr(l, 'date', None), getattr(l, 'time', None))
    #     )
    #     item=[]
    #     for line in sorted_lines.mapped('category_id'):
    #         item = []
    #         for res in sorted_lines.filtered(lambda l: l.category_id.id == line.id):
    #             item.append(res.item_id.name)
    #         list.append({line.name:item})
    #     party_list.update({'product_list':list})
    #     if list:
    #         return party_list
    #     else:
    #         False

    def get_menu_item(self):
        party_list = {}
        list = []

        sorted_lines = self.sort_list(self.fuction_line_ids)
        unique_categories = []
        seen = set()
        for entry in sorted_lines:
            category_id = entry['category_id']
            sequence = entry['sequence']
            if category_id.id not in seen:
                unique_categories.append({'category_id':category_id,'sequence':sequence})
                seen.add(category_id.id)
        unique_categories = sorted(unique_categories, key=lambda x: x['sequence'])
        for line in unique_categories:
            item = [
                res.item_id.name
                for res in sorted_lines
                if res.category_id.id == line.get('category_id').id
            ]
            list.append({line.get('category_id').name: item})

        party_list.update({'product_list': list})
        return party_list if list else False

    def quotation_open(self):
        record = self.env['sale.order'].search([('lead_id','=',self.id),('state','!=','cancel')])
        if record:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quotations',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'domain': [('lead_id','=', self.id)],
                'res_id': record.id,
                'context': "{'create': False}"
            }
    
    @api.onchange('meal_type')
    def _onchange_meal_type(self): 
        time_mapping = {
            'early_morning_tea': ('07', 'am'),
            'breakfast': ('08', 'am'),
            'brunch': ('09', 'am'),
            'mini_meals': ('10', 'am'),
            'lunch': ('11', 'am'),
            'hi-tea': ('04', 'pm'),
            'dinner': ('07', 'pm'),
            'late_night_snacks': ('11', 'pm')
        }

        self.time, self.am_pm = time_mapping.get(self.meal_type, ('', ''))

    @api.onchange('party_name_id')
    def _onchange_party_name_id(self):
        if self.party_name_id:
            self.mobile_num = self.party_name_id.phone

    @api.model
    def create(self, vals):
        if vals.get('time') == 0:
            raise UserError("Please Enter Time First!!!")
        if vals.get('no_of_pax') == 0:
            raise UserError("No. of Pax field is required!!!")
        # if not vals.get('name') or vals['name'] == _('New'):
        #     vals['name'] = self.env['ir.sequence'].next_by_code('hop.lead') or _('New')
        res = super(hoplead, self).create(vals)
        
        time_string = res.time
        hours = int(time_string)
        minutes = int((time_string * 60) % 60)
        t = False
        if res.am_pm == 'am':
            t = str(hours) + ':' + str(minutes) + ' AM'
        else:
            t = str(hours) + ':' + str(minutes) + ' PM'

        datetime_obj = datetime.strptime(t, '%I:%M %p')
        time_24h = datetime_obj.strftime('%H:%M')

        combined_datetime = datetime.combine(res.date, datetime.strptime(time_24h, '%H:%M').time())

        # Convert combined_datetime from IST to GMT/UTC
        ist_timezone = pytz.timezone('Asia/Kolkata')
        gmt_timezone = pytz.timezone('Etc/GMT')
        combined_datetime_gmt = ist_timezone.localize(combined_datetime).astimezone(gmt_timezone)

        # Convert combined_datetime_gmt to naive datetime
        combined_datetime_naive = combined_datetime_gmt.replace(tzinfo=None)

        calendar_rec = self.env['calendar.event'].create({
            'name': res.party_name_id.name,
            'fuction_name_id': res.fuction_name_id.id,
            'lead_id': res.id,
            'start': combined_datetime_naive,
            'stop': combined_datetime_naive,
            'mobile_num': res.mobile_num,
        })

        print("--------calendar_rec.name------------", calendar_rec.name)
        for line in  res.fuction_line_ids:
            if not line.item_id:
                raise UserError('Frist select Iteam name  in "%s" Category'% line.category_id.name)
        return res
    
   
    
    # @api.onchange('fuction_line_ids')
    # def _onchange_fuction_line_ids(self):
    #     line_list = []
    #     # if not self.fuction_line_ids.insider_id and self.fuction_line_ids.item_id:
    #     # if not self.fuction_line_ids.insider_id:
    #     #     self.accompplishment_line_ids = False
    #     self.accompplishment_line_ids = False
    #     if self.fuction_line_ids:
    #         if self.no_of_pax == 0:
    #             raise UserError("Kindly Enter The No. Of Pax First!!!")
    #         for line in self.fuction_line_ids:
    #             if line.item_id:
    #                 line_list.append(line.item_id.id)

    #         self.recipes_ids = [(6,0,line_list)]
    #     else:
    #         self.recipes_ids = False

    def action_apply_all(self):
        hospital_list = []
        if self.vender_id and self.hospitality_ids:
            for i in self.hospitality_ids:
                print(i)
                fag=True
                for line in self.hospitality_line_ids:
                    if self.vender_id.id == line.vender_id.id and line.hospitality_ids.id == i.id and self.service_id.id == line.service_id.id:
                        fag =False  
                if i.id:
                    night = self.env.ref('ct_function_v15.shift3').id

                    current_date = self.date
                    previous_date = current_date - timedelta(days=1)
                    user_date =False 
                    if night in i.ids:
                        user_date = previous_date
                    else:
                        user_date = current_date

                if fag:
                    hospital_list.append((0,0, {
                            'vender_id' : self.vender_id.id,
                            'hospitality_ids' : i.id,
                            'shift_date' :user_date,
                            'service_id' :self.service_id.id,
                            'uom_id':self.service_id.uom_id.id,
                            'rate': self.service_id.standard_price 
                            }))  
        if self.vender_id:
            for line in self.hospitality_line_ids:
                if line.hospitality_ids == 'late_night':
                    print("................................")

        if not self.vender_id:
            raise UserError("Please Enter Vender First !!!")

        self.hospitality_line_ids = hospital_list
        self.hospitality_ids = False
        self.vender_id = False
        self.service_id = False

        for line in self.hospitality_line_ids:
            line._onchange_hospitality_ids()

    def create_order(self):
        line_list = []
        if not self.fuction_line_ids:
            raise UserError('Menu details are mandatory')
        if self.accompplishment_line_ids:
            for rec in self.accompplishment_line_ids:
                if not rec.accomplishment_id:
                    raise UserError('Kindly add Accomplish Item in %s'% rec.item_id.name)
                
        for record in self.fuction_line_ids.sorted(key=lambda line: line.sequence):
            insider_id = False
            out_sider_id = False
            if record.item_id:
                if record.item_id.jobwork_type == 'in_house':
                    insider_id = record.item_id.vender_id.id
                elif record.item_id.jobwork_type == 'out_source':
                    out_sider_id = record.item_id.vender_id.id
            line_list.append((0,0,{
                'category_id': record.category_id.id,
                'item_id': record.item_id.id,
                'uom': record.item_id.uom.id,
                'jobwork_type': record.jobwork_type,
                'total_cost': record.total_cost,
                'no_of_pax': self.no_of_pax,
                'per_qty': record.per_had_qty,
                'qty': record.qty,
                'insider_id': insider_id,
                'out_sider_id': out_sider_id,
                'cost':record.cost,
                'rate':record.rate,
                'instruction':record.instruction,
            }))
        accompplishment_list = []
        for o in self.accompplishment_line_ids:
            for line in o.accomplishment_id.ids:
               accompplishment_list.append(line)
        for line in set(accompplishment_list):
            recipes = self.env['hop.recipes'].search([('id','=',line)])
            line_list.append((0,0,{
            'item_id': line,
            'category_id': recipes.category_id.id,
            'uom': recipes.uom.id,
        }))
            
        list_line = []
        for i in self.hospitality_line_ids:
            list_line.append((0,0,{
                'vender_id':i.vender_id.id,
                'service_id':i.service_id.id,
                'shift_date':i.shift_date,
                'shift_time':i.shift_time,
                'remarks':i.remarks,
                'qty_person':i.qty_person,
                'uom_id':i.uom_id.id,
                'hospitality_ids':i.hospitality_ids.id,
                # 'manager_name_id':i.manager_name_id.id,
                'location':i.location,
                'rate':i.rate,
                'cost':i.cost
                
            }))
        
        list = []
        for o in self.accompplishment_line_ids:
            list.append((0,0,{
                'item_id':o.item_id.id,
                'accomplishment_id':[(6, 0,o.accomplishment_id.ids)]
            }))

        ser_list = []
        for q in self.extra_service_line_ids:
            ser_list.append((0,0,{
                'service_id':q.service_id.id,
                'qty_ids':q.qty_ids,
                'uom_id':q.uom_id.id,
                'price':q.price,
                'cost':q.cost,
                'vender_id':q.vender_id.id,
                'date':q.date,
                'time':q.time,
                'am_pm' : q.am_pm,
                'instruction':q.instruction,
            }))
        search_quotation = self.env['sale.order'].search([('lead_id','=',self.id)])
        fun_rec = self.env['hop.function'].create({
                    'name' : self.name,
                    'venue_address' : self.venue_address,
                    'party_name_id':self.party_name_id.id,
                    'remarks':self.remarks,
                    'mobile_num' : self.mobile_num,
                    'emergency_contact' : self.emergency_contact,
                    'meal_type' : self.meal_type,
                    'manager_name_id' : self.manager_name_id.id,
                    'no_of_pax' : self.no_of_pax,
                    'time' : self.time,
                    'am_pm' : self.am_pm,
                    'fuction_name_id' : self.fuction_name_id.id,
                    'fuction_line_ids':line_list,
                    'hospitality_line_ids':list_line,
                    'accompplishment_line_ids':list,
                    'extra_service_line_ids':ser_list,
                    'hop_lead_id':self.id,
                    'date':self.date 
                })
        
        for line in fun_rec.fuction_line_ids:
            line._onchange_per_qty()


        fun_rec.stage = 'confirm_menu'
        self.hop_funtion_id = fun_rec.id
        calendar_id = self.env['calendar.event'].search([('lead_id','=',self.id)])
        if calendar_id:

            time_string = self.time
            hours = int(time_string)
            minutes = int((time_string * 60) % 60)
            t = False
            if self.am_pm == 'am':
                t = str(hours) + ':' + str(minutes) + ' AM'
            else:
                t = str(hours) + ':' + str(minutes) + ' PM'

            datetime_obj = datetime.strptime(t, '%I:%M %p')
            time_24h = datetime_obj.strftime('%H:%M')

            combined_datetime = datetime.combine(self.date, datetime.strptime(time_24h, '%H:%M').time())

            # Convert combined_datetime from IST to GMT/UTC
            ist_timezone = pytz.timezone('Asia/Kolkata')
            gmt_timezone = pytz.timezone('Etc/GMT')
            combined_datetime_gmt = ist_timezone.localize(combined_datetime).astimezone(gmt_timezone)

            # Convert combined_datetime_gmt to naive datetime
            combined_datetime_naive = combined_datetime_gmt.replace(tzinfo=None)


            calendar_id.write({
                        'name': self.party_name_id.name,
                        'fuction_id':self.hop_funtion_id.id,
                        'fuction_name_id': self.fuction_name_id.id,
                        'lead_id':self.id,
                        'start': combined_datetime_naive,
                        'stop': combined_datetime_naive,
                        'mobile_num': self.mobile_num,
                    })
        self.stage = "production"
        if self.calendar_line_id:
            self.calendar_line_id.state = "production"
        record = self.env['sale.order'].search([('lead_id','=',self.id),('state','in',('draft','send'))])
        # if record:
        #     record.action_confirm()
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Order',
        #     'view_mode': 'form',
        #     'res_model': 'hop.function',
        #     'domain': [('id','=', self.hop_funtion_id.id)],
        #     'context': "{'create': False}",
        #     'res_id':  self.hop_funtion_id.id,  
        # }

    @api.depends('stage_check')
    def _compute_stage_check(self):
        for rec in self:
            if rec.stage == 'production':
                rec.stage_check =  'production'
            else:
                if len(rec.fuction_line_ids) == 0:
                    rec.stage_check =  False
                else:
                    rec.stage_check =  'create_menu'

    
    @api.depends('order_count')
    def _cumpute_order_count(self):
        for i in self:
            record = self.env['hop.function'].search([('hop_lead_id','=',i.id)])
            i.order_count = len(record)

    def order_open(self):
        self.open_oder =  True
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Order',
        #     'view_mode': 'tree,form',
        #     'res_model': 'hop.function',
        #     'domain': [('hop_lead_id','=', self.id)],
        #     'context': "{'create': False}"
        # }
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order',
            'view_mode': 'form',
            'res_model': 'hop.function',
            'context': "{'create': False}",
            'res_id':  self.hop_funtion_id.id,  
        }

    @api.depends('accompplishment_line_ids')
    def _compute_accompplishment_visible(self):
        if len(self.accompplishment_line_ids)>0:
            self.accompplishment_visible = True
        else:
            self.accompplishment_visible = False

    @api.onchange('fuction_line_ids')
    def _onchange_function_id(self):
        self.recipes_ids = False
        self.recipes_ids = self.fuction_line_ids.mapped('item_id').ids
        line_list = []          
        # if not self.fuction_line_ids.insider_id:
        # self.accompplishment_line_ids = False
        acc_list = []
        aco_list = []
        for i in self.accompplishment_line_ids:
            if i.item_id.id in self.fuction_line_ids.mapped('item_id').ids:
                aco_list.append((0,0, {
                                    'item_id': i.item_id.id,
                                    'accomplishment_id' : [(6,0,i.accomplishment_id.ids)]
                                }))
        # this code item remove but accompplishment not remove in accompplishment  
        self.accompplishment_line_ids = False
        self.accompplishment_line_ids = aco_list

        for i in self.accompplishment_line_ids:
            acc_list.append(i.item_id.id)
        if self.fuction_line_ids:
            for rec in self.fuction_line_ids.mapped('item_id'):  
                if rec.accomplishment:
                    if rec.id not in acc_list:
                        line_list.append((0,0, {
                                    'item_id': rec.id,
                                }))
                self.accompplishment_line_ids = line_list
        else:
            self.accompplishment_line_ids = False

    def write(self, vals):
        if vals.get('fuction_line_ids'):
            data_text = ""
            for i in vals.get('fuction_line_ids'):
                if i[2]:
                    data_text += str(i[2]) + ","
            message = _("Changes in Menu %s ",data_text if data_text else "Delete")
            self.message_post(body=message,message_type='comment')

        if vals.get('hospitality_line_ids'):
            data_text = ""
            for i in vals.get('hospitality_line_ids'):
                if i[2]:
                    data_text += str(i[2]) + ","
            message = _("Changes in Services %s ",data_text if data_text else "Delete")
            self.message_post(body=message,message_type='comment')

        if vals.get('accompplishment_line_ids'):
            data_text = ""
            for i in vals.get('accompplishment_line_ids'):
                if i[2]:
                    data_text += str(i[2]) + ","
            message = _("Changes in Accompplishment %s ",data_text if data_text else "Delete")
            self.message_post(body=message,message_type='comment')

        if vals.get('extra_service_line_ids'):
            data_text = ""
            for i in vals.get('extra_service_line_ids'):
                if i[2]:
                    data_text += str(i[2]) + ","
            message = _("Changes in Addons %s ",data_text if data_text else "Delete")
            self.message_post(body=message,message_type='comment')

        res = super(hoplead, self).write(vals)
        self.calendar_id.write({
            'name':self.party_name_id.name,
            'customer_id':self.party_name_id.id,
            'party_number':self.mobile_num,
            'date':self.date,
            'venue_address':self.venue_address,
        })
        self.calendar_line_id.write({
            'date':self.date,
            'function_name':self.fuction_name_id.id,
            'time':self.time,
            'remarks':self.remarks,
            'meal_type':self.meal_type,
            'am_pm':self.am_pm,
            'no_of_pax':self.no_of_pax,
        })
        for line in  self.fuction_line_ids:
            if not line.item_id:
                raise UserError('Frist select Iteam name  in "%s" Category'% line.category_id.name)
            

        if self.calendar_id:
            self.calendar_id.customer_id = self.party_name_id
            self.calendar_id.party_number = self.mobile_num
            self.calendar_line_id.time = self.time
            self.calendar_line_id.am_pm = self.am_pm
            self.calendar_line_id.date = self.date
            
        lead_quotation = self.env['sale.order'].search([('lead_id','=',self.id)])
        if lead_quotation:
            lead_quotation.partner_id = self.party_name_id

        return res
    
    def item_with_accomplisment(self, vals,lg_type=False):
        if lg_type:
            record = self.fuction_line_ids.filtered(lambda l: l.item_id.id == vals.id)
            acc = ', '.join(translate_field(res,lg_type) for line in self.accompplishment_line_ids for res in line.accomplishment_id if line.item_id.id == record.item_id.id)
            if acc:
                if lg_type == 'gujarati':
                    return translate_field(vals, lg_type) + f' સાથે {acc}'
                elif lg_type == 'hindi':
                    return translate_field(vals, lg_type) + f' साथ {acc}'
                else:
                    return translate_field(vals, lg_type) + f' with {acc}'
            return translate_field(vals, lg_type)
        else:
            record = self.fuction_line_ids.filtered(lambda l: l.item_id.name == vals)
            acc = ', '.join(res.name for line in self.accompplishment_line_ids for res in line.accomplishment_id if line.item_id.id == record.item_id.id)
            if acc:
                vals += f' with {acc}'

            return vals
        
    def item_description(self,vals):
        record = self.fuction_line_ids.filtered(lambda l: l.item_id.name == vals)
        if record.item_id.description:
            return record.item_id.description or False
        else:
            return False
    
    def get_item_instruction(self, vals):
        record = self.fuction_line_ids.filtered(lambda l: l.item_id.name == vals)
        vals = False
        for line in record:
            vals = line.instruction

        return vals
    
class HopFunctionleadLine(models.Model):
    _name = "hop.fuction.lead.line"

    lead_id = fields.Many2one('hop.lead',string="Function", ondelete='cascade', log_access=True)

    category_id = fields.Many2one('hop.recipes.category',string="Category",track_visibility='onchange')
    item_id = fields.Many2one('hop.recipes',string="Item Name",track_visibility='onchange')
    no_of_pax = fields.Integer(string="No Of Pax",track_visibility='onchange')
    per_qty = fields.Float(string="Per Head Qty",track_visibility='onchange')
    qty = fields.Float(string="Qty",track_visibility='onchange')
    uom = fields.Many2one('uom.uom',string="Uom",track_visibility='onchange')
    insider_id = fields.Many2one('res.partner',string="In-House",domain=[('is_vender','=',True)] ,track_visibility='onchange')
    out_sider_id = fields.Many2one('res.partner',string="Out-Source",domain=[('is_vender','=',True)],track_visibility='onchange')
    cost = fields.Float(string="Cost",track_visibility='onchange')
    rate = fields.Float(string="Rate",track_visibility='onchange')
    instruction = fields.Char(string="Instruction",track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id)
    jobwork_type = fields.Selection([('in_house','In-House'),('out_source','Out-Source')],string="Work Type")
    per_had_qty = fields.Float('Per Head Qty' ,default=1)
    total_cost = fields.Float('Total Cost')
    sequence = fields.Integer('Sequence')

    @api.onchange('jobwork_type','per_had_qty')
    def _onchange_jobwork_type(self):
        if self.jobwork_type == "in_house":
            if self.per_had_qty == 0:
                self.per_had_qty = 1
            self.total_cost = (self.per_had_qty * self.lead_id.no_of_pax) * self.item_id.cost
        if self.jobwork_type == "out_source":
            self.per_had_qty = 1
            self.total_cost = self.lead_id.no_of_pax * self.item_id.rate
    @api.onchange('insider_id','out_sider_id')
    def _onchange_insider_id(self):
        if self.insider_id:
            if self.out_sider_id:
                raise UserError("You Can Select Insider As You Already Selected The Outsider!!!")
        elif self.out_sider_id:
            if self.insider_id:
                raise UserError("You Can Select Outsider As You Already Selected The Insider!!!") 

    @api.onchange('insider_id','out_sider_id')
    def _onchange_no_of_pax(self):
        if self.insider_id:
            self.no_of_pax = self.lead_id.no_of_pax
        else:
            self.no_of_pax = self.lead_id.no_of_pax

    @api.onchange('per_qty')
    def _onchange_per_qty(self):
        if self.per_qty:
            self.qty = self.no_of_pax * self.per_qty
        else:
            self.qty = 0

    @api.onchange('item_id')
    def _onchange_item_id(self):
        if self.item_id:
            if not self.item_id.uom:
                raise UserError('Select UoM First in %s'%self.item_id.name)            
            self.uom = self.item_id.uom.id
            self.jobwork_type = self.item_id.jobwork_type

class HospitalityShiftleadLine(models.Model):
    _name = 'hospitality.shift.lead.line'

    hs_id = fields.Many2one('hop.lead',string="Hospitality", ondelete='cascade', log_access=True)

    vender_id = fields.Many2one('res.partner',string="Vender Name",domain=[('is_vender','=',True)] ,tracking=True)
    service_id = fields.Many2one('product.product', string='Vendor Category',track_visibility='onchange', domain=[('is_service','=',True)])
    hospitality_ids = fields.Many2one('ct.hospitality.shift',string="Hospitality Shift",tracking=True)
    shift_date = fields.Date(string="Shift Date")
    shift_time = fields.Float(string="Shift Time")
    remarks = fields.Char(string="Shift Remarks")
    qty_person = fields.Float(string="Quantity/Person")
    uom_id = fields.Many2one('uom.uom', string="UOM")
    rate = fields.Float(string="Rate",tracking=True)
    cost = fields.Float(string="Cost",tracking=True)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id)
    location = fields.Selection([
        ('add_venue', "At Venue"),
        ('add_godown', "At Godown")], default=False, string="Location")
    @api.onchange('rate','qty_person')
    def _onchange_rate(self):
        self.cost  = self.qty_person * self.rate

    @api.onchange('hospitality_ids')
    def _onchange_hospitality_ids(self): 
        if self.hospitality_ids:
            mrng = self.env.ref('ct_function_v15.shift1').id
            eve = self.env.ref('ct_function_v15.shift2').id
            night = self.env.ref('ct_function_v15.shift3').id
            late_night = self.env.ref('ct_function_v15.shift4').id

            if mrng:
                if mrng in self.hospitality_ids.ids:
                    self.shift_time = '8'
            if eve:
                if eve in self.hospitality_ids.ids:
                    self.shift_time = '4'
            if night:
                if night in self.hospitality_ids.ids:
                    self.shift_time = '8'
            if late_night:
                if late_night in self.hospitality_ids.ids:
                    self.shift_time = '12'

class HospitalityShiftleadLine(models.Model):
    _name = 'hop.extra.service.lead.line'
    _description = 'Extra Service Line'

    extra_service_id = fields.Many2one('hop.lead',string="Hospitality", ondelete='cascade', log_access=True)
    vender_id = fields.Many2one('res.partner',string="Vender Name",domain=[('is_vender','=',True)] ,tracking=True)
    service_id = fields.Many2one('product.product', string='Vendor Category',track_visibility='onchange',domain=['|',('utility_type', '=','service'),('is_recipe', '=',True)])
    qty_ids = fields.Float(string="Quantity/Person",tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UoM')
    price = fields.Float(string="Sale Price",tracking=True)
    rate = fields.Float(string="Rate",tracking=True)
    cost = fields.Float(string="Amount",tracking=True)
    date = fields.Date(string="Date")
    time = fields.Float(string="Time")
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    instruction = fields.Char(string="Instruction",track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id)

    @api.onchange('date')
    def _onchange_date(self):  
        current_date = datetime.now().date()
        if  self.date:
            if  self.date < current_date:
                raise UserError("Can't Select Previous Date!!!!")

    @api.onchange('qty_ids','rate')
    def _onchange_qty_ids(self):
        if self.qty_ids:
            self.cost = self.qty_ids * self.rate 
        if self.rate:
            self.cost = self.qty_ids * self.rate 

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.cost = self.service_id.standard_price  
            self.price, self.uom_id = self.service_id.lst_price, self.service_id.uom_id
            self.date,self.time, self.am_pm = self.extra_service_id.date, self.extra_service_id.time,self.extra_service_id.am_pm
            self.rate = self.service_id.standard_price

    def write(self, vals):
        res = super(HospitalityShiftleadLine, self).write(vals)
        lead_record = self.env['product.product'].search([('id', '=', self.service_id.id)])
        if lead_record:
            lead_record.standard_price = self.rate

        return res


class AccomplishmentleadLine(models.Model):
    _name="hop.accomplishment.lead.line"

    function_id = fields.Many2one('hop.lead',string="Function",ondelete='cascade')

    item_id = fields.Many2one('hop.recipes',string="Item Name")

    accomplishment_id = fields.Many2many('hop.recipes','accomplishment_id_recipes_ref',string="Accomplishment Item",domain=lambda self: "[('category_id', '=', %s)]" % self.env.ref('ct_function_v15.rec_cat_1').id)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id)