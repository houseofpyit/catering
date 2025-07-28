from odoo import api, models, fields,_
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from datetime import datetime, date ,timedelta



class hop_calendar(models.Model):
    _name = "hop.calendar"
    _rec_name = "customer_id"
    _inherit = ['mail.thread']

    # name = fields.Char(string="Number",readonly=True, copy=False, default='New',tracking=True)
    name = fields.Char(string="Party Name")
    customer_id = fields.Many2one('res.partner',string="Party Name")
    seq_name = fields.Char(string="Number", required=True, copy=False, default='New',tracking=True,readonly=True)
    date = fields.Date(string="Inquiry Date",default=fields.Date.context_today)
    party_number = fields.Char(string="Party Number")
    venue_address = fields.Text(string="Venue Address")
    inquiry_by = fields.Text(string="Inquiry By")
    color_type = fields.Selection([('red','Lead'),('green','Function')],string="Type")
    color = fields.Integer(string="Color")
    is_lead = fields.Boolean(string="Is Lead" ,default =False ,copy=False)
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")
    email = fields.Char(string="Email")
    type = fields.Selection([('normal','Normal'),('website','Website')],default='normal',string="Inquiry Type")
    calendar_line_ids = fields.One2many('hop.calendar.line','calendar_id',string="Calendar Line")
    state = fields.Selection([('draft','Draft'),('convert_planner','Convert Planner'),('create_menu','Menu Created'),('production','Production'),('cancel','Cancel')],string="State",default="draft") 
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id)
    pkg_list = fields.Text('Package List')

    def update_customer_id(self):
        for res in self.search([]):
            for line in res.calendar_line_ids:
                if not res.customer_id:
                    res.customer_id = line.lead_id.party_name_id.id
                    res.party_number = line.lead_id.mobile_num
                    break

        for line in set(self.search([('customer_id','=',False)]).mapped('party_number')):
            existing_partner = self.env['res.partner'].search(
                [('phone', '=', line)])
            if not existing_partner:
                
                calendar = self.env['hop.calendar'].search(
                    [('party_number', '=', line)],limit=1)
                
                existing_partner = self.env['res.partner'].search(
                [('name', '=', calendar.name)])
                if not existing_partner :
                    partner = self.env['res.partner'].create({
                                    'name': calendar.name,
                                    'phone': calendar.party_number,
                                    'is_customer':True,
                                    'email':calendar.email
                                    })
        for line in self.search([]):
            if not line.customer_id :
                existing_partner = self.env['res.partner'].search(
                [('phone', '=', line.party_number)])
                if existing_partner:
                    line.customer_id = existing_partner.id
            
        # for res in self.search([]):
        #     if not res.customer_id:
        #         existing_partner = self.env['res.partner'].search(
        #         [('phone', '=', res.party_number)], limit=1
        #         )
        #         print("*********",existing_partner)
        #         if existing_partner:
        #             res.customer_id = existing_partner.id
        #         else:
        #             if len(self.env['hop.calendar'].search([('party_number','=',res.party_number)])) == 1:
        #                 if res.id not in list_id:
        #                     print("*******1****",res.name,list_id,res)
        #                     partner = self.env['res.partner'].create({
        #                     'name': res.name,
        #                     'phone': res.party_number,
        #                     'is_customer':True,
        #                     'email':res.email
        #                     })
        #                     res.customer_id = partner.id
        #                     list_id.append(res.id)
        #             else:
        #                 if res.id not in list_id:
        #                     print("****3333*******",res.name,list_id,res)
        #                     partner = self.env['res.partner'].create({
        #                     'name': res.name,
        #                     'phone': res.party_number,
        #                     'is_customer':True,
        #                     'email':res.email
        #                     })
        #                     for line in self.env['hop.calendar'].search([('party_number','=',res.party_number)]):
        #                         line.customer_id = partner.id
        #                         list_id.append(line.id)
                        

    # @api.onchange('name')
    # def _onchange_name(self):
    #     if self.party_number:
    #         existing_partner = self.env['res.partner'].search(
    #         [('phone', '=', self.party_number)], limit=1
    #         )
    #         if existing_partner:
    #             self.customer_id = existing_partner

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.party_number = self.customer_id.phone


    @api.onchange('party_number')
    def _onchange_party_number(self):
        if self.party_number:
            existing_partner = self.env['res.partner'].search(
            [('phone', '=', self.party_number)], limit=1
            )
            if existing_partner:
                self.customer_id = existing_partner
    
    @api.onchange('color','color_type')
    def _onchange_color_type(self):
        if self.color_type == 'red':
            self.color = "1"

        elif self.color_type == 'green':
            self.color = "10"

        else:
            self.color = "1"


    @api.model
    def inquiry_cancel(self):
        vals = {"model":'hop.calendar','id':self.ids}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel',
            'view_mode': 'form',
            'res_model': 'hop.cancel',
            'target':'new',
            'context':vals
        }

    def cancel(self,reason):
        for res in self:
            if res.state == "convert_planner":
                raise UserError('You cannot delete this entry because the menu planner has already been created.')
            if res.state == "create_menu":
                raise UserError('You cannot delete this entry because the menu planner has already been created.')
            if res.state == "production":
                raise UserError('You cannot delete this entry because the Confirmed Order has already been created.')
            if res.state == 'draft':
                for line in self.calendar_line_ids:
                    existing_partner = self.env['res.partner'].search(
                [('phone', '=', self.party_number)], limit=1)
                    self.env['hop.cancel.report'].create({
                        'party_id': existing_partner.id,
                        'date': line.date,
                        'meal_type': line.meal_type,
                        'cancel_type': 'Event Inquiry',
                        'no_of_pax' : line.no_of_pax,
                        'venue_address': self.venue_address,
                        'reason' :reason,
                    })
                res.state = 'cancel'
                res.active = False

    def unlink(self):
        for record in self:
            if record.is_lead:
                raise UserError("You cannot delete this entry...")
        return super().unlink()
    
    def convert_planner(self):

        if not  self.env.company.manager_name_id :
            raise UserError('Please Set manager in Company Master..!!!!')
        if not self.calendar_line_ids:
            raise UserError('Please Fill Menu First!!!!')
        for line in self.calendar_line_ids:
            if not line.function_name:
                raise UserError("Frist Select Function Name")
            if not line.meal_type:
                raise UserError("Frist Select Meal Type")
        existing_partner = self.env['res.partner'].search(
            [('phone', '=', self.party_number)], limit=1
        )
        partner = False
        
        if existing_partner :
            partner = existing_partner
        else:
            partner = self.env['res.partner'].create({
                'name': self.customer_id.name,
                'phone': self.party_number,
                'is_customer':True,
                'email':self.email
            })
        self.seq_name = self.env['ir.sequence'].next_by_code('hop.calendar') or _('New')
        if len(self.calendar_line_ids) == 1:
                for res in self.calendar_line_ids:
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

                    time, am_pm = time_mapping.get(res.meal_type, ('', ''))
                    if res.meal_type == 'parcel':
                        time = res.time
                        am_pm = res.am_pm
                    res.lead_id = self.env['hop.lead'].create({
                        'party_name_id' : partner.id,
                        'mobile_num' : partner.phone,
                        'venue_address' : self.venue_address,
                        'emergency_contact' : self.inquiry_by,
                        'date':res.date,
                        'meal_type': res.meal_type,
                        'fuction_name_id': res.function_name.id,
                        'time':time,
                        'am_pm':am_pm,
                        'no_of_pax':res.no_of_pax,
                        'remarks':res.remarks,
                        'name':self.seq_name,
                        'stage':'details',
                        'manager_name_id': self.env.company.manager_name_id.id,
                        'calendar_id':self.id,
                        'calendar_line_id':res.id
                    }).id
                    res.state = 'convert_planner'
                    res._compute_color()
                # self.color = "2"
                self.is_lead = True
        else:
                unique_dates = set()
                last_record = False
                for record in self.calendar_line_ids:
                    if record.date not in unique_dates:
                        unique_dates.add(record.date)
                        calendar_line = []
                        for res in self.calendar_line_ids.filtered(lambda l: l.date == record.date):
                            calendar_line.append((0,0, {
                                            'lead_id': res.lead_id.id,
                                            'meal_type': res.meal_type,
                                            'no_of_pax': res.no_of_pax,
                                            'remarks': res.remarks,
                                            'function_name': res.function_name.id,
                                            'date': res.date,
                                            'state':'convert_planner',
                                            'time':res.time,
                                            'am_pm':res.am_pm,
                                        }))    
                        last_record = self.env['hop.calendar'].create({ 
                            'seq_name': self.env['ir.sequence'].next_by_code('hop.calendar') or _('New'),
                            'customer_id':self.customer_id.id,
                            'date':res.date,
                            'party_number':self.party_number,
                            'venue_address': self.venue_address,
                            'inquiry_by':self.inquiry_by,

                            'is_lead':True,
                            'calendar_line_ids':calendar_line,
                            # 'color':"2",
                        })
                        for res in last_record.calendar_line_ids:
                            res._compute_color()
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

                            time, am_pm = time_mapping.get(res.meal_type, ('', ''))
                            if res.meal_type == 'parcel':
                                time = res.time
                                am_pm = res.am_pm
                            res.lead_id = self.env['hop.lead'].create({
                                'name':last_record.seq_name,
                                'party_name_id' : partner.id,
                                'mobile_num' : partner.phone,
                                'venue_address' : last_record.venue_address,
                                'emergency_contact' : last_record.inquiry_by,
                                'date':res.date,
                                'meal_type': res.meal_type,
                                'fuction_name_id': res.function_name.id,
                                'time':time,
                                'am_pm':am_pm,
                                'no_of_pax':res.no_of_pax,
                                'remarks':res.remarks,
                                'stage':'details',
                                'manager_name_id': self.env.company.manager_name_id.id,
                                'calendar_id':last_record.id,
                                'calendar_line_id':res.id
                            }).id
                        # last_record.color = "2"
                        res._compute_color()
                        last_record.is_lead = True


                self.active = False
                # return super(hop_calendar, self).create(self)
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Calendar',
                    'view_mode': 'form',
                    'res_model': 'hop.calendar',
                    'res_id': last_record.id,
                    'target':'main',
                }
    @api.onchange('calendar_line_ids')
    def _onchange_calendar_line_ids(self):  
        last_date=False
        if len(self.calendar_line_ids) == 1:
            if not self.calendar_line_ids.date:
                self.calendar_line_ids.date = self.date
        else:
            for i in self.calendar_line_ids:
                if i.date:
                    last_date =  i.date
                if not i.date:
                    i.date = last_date
            
    @api.onchange('date')
    def _onchange_date(self):  
        current_date = datetime.now().date()
        if  self.date:
            if  self.date < current_date:
                raise UserError("Can't Select Previous Date!!!!")

    def print(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ct_function_v15.action_print")
        action['context'] = {'active_id': self.env.context['active_ids'],
                             'active_model': self.env.context['active_model']}
        return action

class hop_calendarline(models.Model):
    _name = "hop.calendar.line"
    _rec_name = "function_name"

    calendar_id = fields.Many2one('hop.calendar',string="Calendar")
    color = fields.Integer(string="Color",compute="_compute_color")
    lead_id = fields.Many2one('hop.lead',string="Lead")
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type")
    no_of_pax = fields.Integer(string="No Of Pax")
    remarks = fields.Char(string="Remarks")
    time = fields.Float(string="Time",tracking=True)
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    function_name = fields.Many2one('hop.function.mst',string="Function Name")
    state = fields.Selection([('draft','Draft'),('convert_planner','Convert Planner'),('create_menu','Menu Created'),('production','Production')],string="State",default="draft") 
    date = fields.Date(string='Date', default=lambda self: self._default_date())
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id)

    @api.onchange('date')
    def _onchange_date(self):  
        if  self.date:
            if  self.date < datetime.now().date():
                raise UserError("Can't Select Previous Date!!!!")

    @api.depends('color')
    def _compute_color(self):
        for rec in self:
            if rec.state == 'draft':
                rec.color = "1"
            elif rec.state == 'convert_planner':
                rec.color = '2'
            elif rec.state == 'create_menu':
                rec.color = "4"
            else:
                rec.color = "10"
            if rec.calendar_id.state !='cancel':
                draf = True
                convert_planner = True
                create_menu = True
                production =  True

                for line in rec.calendar_id.calendar_line_ids:
                    if line.state != 'draft':
                        draf =  False
                        break
                for line in rec.calendar_id.calendar_line_ids:
                    if line.state != 'convert_planner':
                        convert_planner =  False
                        break

                for line in rec.calendar_id.calendar_line_ids:
                    if line.state != 'create_menu':
                        create_menu =  False
                        break

                for line in rec.calendar_id.calendar_line_ids:
                    if line.state != 'production':
                        production =  False
                        break
                if draf:
                    rec.calendar_id.color = "1"
                    rec.calendar_id.state = 'draft' 
                if convert_planner:
                    rec.calendar_id.color = "2"
                    rec.calendar_id.state = 'convert_planner' 
                if create_menu:
                    rec.calendar_id.color = "4"
                    rec.calendar_id.state = 'create_menu' 
                if production:
                    rec.calendar_id.color = "10"
                    rec.calendar_id.state = 'production' 

    def name_get(self):
        result = []
        for res in self:
            if res.meal_type and res.function_name:
                name = res.function_name.name + ' - '+  dict(res._fields['meal_type'].selection).get(res.meal_type) + ' - ' + str(res.no_of_pax) 
            else:
                name =  str(res.no_of_pax) 
            result.append((res.id, name))
        return result

    @api.model
    def _default_date(self):
        parent = self.env['hop.calendar'].browse(self._context.get('default_parent_id'))
        return parent.date if parent else False
    
    def write(self, vals):
        res =  super(hop_calendarline,self).write(vals)
        self.production_to_all()
        return res
    
    def production_to_all(self):
        flg = True
        for line in self.calendar_id.calendar_line_ids:
            if line.state != 'production':
                flg = False
                break
        if flg:
            self.calendar_id.color = "10"

    def open_planner(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Lead',
                'view_mode': 'form',
                'res_model': 'hop.lead',
                'res_id': self.lead_id.id,
                'target':'current',
                'context':{'create':False,'lead_id':self.lead_id.id}
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

class Alarm(models.Model):
    _inherit = 'calendar.alarm'

    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company.id)


