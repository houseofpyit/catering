from odoo import api, models, fields, _
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from datetime import datetime, date ,timedelta
from odoo.tools import html_escape

class HopFunction(models.Model):
    _name = "hop.function"
    _inherit = ['mail.thread']
    _description = "Function"
    _rec_name = "party_name_id"

    name = fields.Char(string="Number",readonly=True, required=True, copy=False, default='New',tracking=True)
    stage = fields.Selection([('details','Details'),('create_menu','Menu Created'),('confirm_menu','Confirm Menu'),('raw_materials','Raw Materials'),('purchase_order','Generate Purchase Order'),('manager_report','Utensils Report'),('invoice','File Completed'),('cancel','Cancel')],string="Stage",default="details",tracking=True)
    party_name_id = fields.Many2one('res.partner',string="Party Name",tracking=True,domain=[('is_customer','=',True)])
    mobile_num = fields.Char(string="Mobile Number",tracking=True)
    fuction_name_id = fields.Many2one('hop.function.mst',string="Function Name",tracking=True)
    date = fields.Date(string="Function Date",default=fields.Date.context_today,tracking=True)
    emergency_contact = fields.Text(string="Emergency Contact")
    remarks = fields.Text(string="Remarks",tracking=True)
    manager_name_id = fields.Many2one('res.partner',string="Manager Name",domain=[('is_vender','=',True)] ,tracking=True)
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type",tracking=True)
    no_of_pax = fields.Integer(string="No Of Pax",tracking=True)
    time = fields.Float(string="Time",tracking=True)
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    venue_address = fields.Text('Venue Address')
    po_count = fields.Integer(string='PO Count',compute='_count_po_rec',readonly=True)
    vender_id = fields.Many2one('res.partner',string="Vendor Name",domain=[('is_vender','=',True)])
    service_id = fields.Many2one('product.product', string='Vendor Category',tracking=True, domain=[('utility_type','=','service')])
    hospitality_ids = fields.Many2many('ct.hospitality.shift',string="Hospitality Shift",tracking=True)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    is_purchase = fields.Boolean(string="Is Purchase",default=False)
    is_service_po = fields.Boolean(string="Is Service po",default=False)
    is_addons_po = fields.Boolean(string="Is Addons po",default=False)
    skip_labour = fields.Boolean(string="Skip Labour")
    skip_addons = fields.Boolean(string="Skip Addons")
    
    hop_lead_id = fields.Many2one('hop.lead',string="Hop lead")
    lead_order_count = fields.Integer(string='Lead Order', compute='_cumpute_lead_order_count',readonly=True)

    fuction_line_ids = fields.One2many('hop.fuction.line', 'fuction_id',string="Function Line",tracking=True)
    material_line_ids = fields.One2many('hop.raw.materal', 'fuction_id',string="Material Line",tracking=True)
    utensils_line_ids = fields.One2many('hop.utensils', 'fuction_id',string="Utensils Line",tracking=True)
    extra_service_line_ids = fields.One2many('hop.extra.service.line', 'extra_service_id',string="Extra Service Line",tracking=True)
    hospitality_line_ids = fields.One2many('hospitality.shift.line', 'hs_id',string="Hospitality Shift Line",tracking=True)
    accompplishment_line_ids = fields.One2many('hop.accomplishment.line','function_id',string="Accomplishment Line")
    recipes_ids = fields.Many2many('hop.recipes','hop_ref_recipes_ids_function_ref',string="Recipes Name",track_visibility='onchange')
    inventory_line_ids = fields.One2many('hop.inventory','inventory_id',string="Inventory Line")

    out_source = fields.Integer(string="Out Source",compute="_compute_po_count",readonly=True)
    in_house = fields.Integer(string="In Source",compute="_compute_po_count",readonly=True)
    service = fields.Integer(string="Labour",compute="_compute_po_count",readonly=True)
    addons = fields.Integer(string="Add-ons",compute="_compute_po_count",readonly=True)
    quotation_count = fields.Integer(string="Quotation",compute="_compute_quotation_count",readonly=True)
    issue_return_visible = fields.Boolean(string="Is Issue Return Visible",compute='_count_issue_return_visible')
    is_utensils = fields.Boolean(string="Is Untensils",compute='_count_is_utensils')
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")
    file_completed = fields.Boolean(string="File Completed")
    completed = fields.Boolean(string="File Completed",compute='_compute_file_completed')

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
    
    @api.depends('completed','material_line_ids','hospitality_line_ids','extra_service_line_ids','fuction_line_ids')
    def _compute_file_completed(self):
        for i in self:
            if i.visible_raw_material ==  False and self.visible_labour == False and self.visible_addons == False and self.visible_out_source == False and self.visible_in_house == False:
                i.completed = True
                i.file_completed = True
            else:
                 i.completed = False
                 i.file_completed = False

    def file_completed_button(self):
        self.sudo().with_context(completed=True).write({'stage':'invoice'})
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'File Completed Successfully',
                'img_url': '/ct_function_v15/static/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
    def reset_to_draft(self):
        self.sudo().with_context(reset_to_draft=True).write({'stage':'confirm_menu'})

    def write(self, vals):
        if self.stage == 'invoice':
            if vals.get('stage',False):
                if not self.env.context.get('reset_to_draft'):
                    raise UserError('Once a file is in the completion stage, users cannot make any changes; to modify it, click on "Action" > "Add/Update Menu."')
        if vals.get('stage') == 'invoice':
            if not self.env.context.get('completed'):
                raise UserError('Please Press the file Completed Button...')
        if vals.get('stage') == 'invoice':
            if not self.env.context.get('completed'):
                raise UserError('Please Press the file Completed Button...')
        res =  super(HopFunction,self).write(vals)
        lead_record = self.env['hop.lead'].search([('hop_funtion_id','=',self.id)])
        if lead_record:
            lead_record.party_name_id = self.party_name_id
            lead_record.mobile_num = self.mobile_num
            lead_record.date = self.date
            lead_record.time = self.time
            lead_record.am_pm = self.am_pm
        return res
    

    def action_back_to_edit(self):
        vals = {"model":'hop.function','id':self.ids}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm',
            'view_mode': 'form',
            'res_model': 'hop.confirm',
            'target':'new',
            'context':vals
        }
    
    def edit_function(self):
        vals = {"model":'hop.function','id':self.ids}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Function',
            'view_mode': 'form',
            'res_model': 'hop.edit.function',
            'target':'new',
            'context':vals
        }

    def unlink(self):
        for i in self:
            # po_out  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','out_source')])
            # print("-----------1",po_out)
            # if po_out:
            #     raise UserError("Can't Delete This Record")
            # po_in  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','in_house')])
            # print("-----------2",po_in)
            # if po_in:
            #     raise UserError("Can't Delete This Record")
            # po_ser  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','service')])
            # print("-----------3",po_ser)
            # if po_ser:
            #     raise UserError("Can't Delete This Record")
            # po_add  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','addons')])
            # print("-----------4",po_add)
            # if po_add:
            #     pass
            # raise UserError("Can't Delete This Record")
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('state','in',('draft','sent','to approve'))])
            for line in po_rec:
                # line.button_cancel()
                line.state = 'cancel'
                line.unlink()
            if self.hop_lead_id:
                self.hop_lead_id.open_oder = False
                self.hop_lead_id.stage = 'details'
            quot_count = self.env['sale.order'].search([('lead_id','=',self.hop_lead_id.id)])
            for order in quot_count:
                order.state = 'cancel'
                order.unlink()
        return super(HopFunction,self).unlink()

    @api.onchange('manager_name_id')
    def _onchange_manager_name_id(self):
        utensils_id = self.env['utensils.mst'].search([('function_id','=',self.ids[0])])
        if utensils_id:
            utensils_id.manager_name_id = self.manager_name_id.id
        pass

    @api.depends('issue_return_visible')
    def _count_issue_return_visible(self):
        for i in self:
            if i.date <= date.today():
                i.issue_return_visible = True
            else:
                 i.issue_return_visible = False
            print("....................",i.issue_return_visible)

    @api.depends('is_utensils')
    def _count_is_utensils(self):
        for i in self:
            if len(i.utensils_line_ids) > 0:
                i.is_utensils = True
            else:
                i.is_utensils = False

    def action_utensils(self):
        return{
            'name': 'Utensils',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'hop.utensils',
            'domain': [('fuction_id','=', self.id)],
            'context': "{'create': False}",
            'target':'new',
        }
    
    @api.model
    def action_cancel(self):
        vals = {"model":'hop.function','id':self.ids}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel',
            'view_mode': 'form',
            'res_model': 'hop.cancel',
            'target':'new',
            'context':vals
        }

    def cancel(self,reason):
        self.env['hop.cancel.report'].create({
            'party_id': self.party_name_id.id,
            'date': self.date,
            'meal_type': self.meal_type,
            'cancel_type': 'Confirm Orders',
            'no_of_pax' : self.no_of_pax,
            'venue_address': self.venue_address,
            'reason' :reason,

        })
        po_records  = self.env['purchase.order'].search([('fuction_id_rec','=',self.ids[0]),('state','!=','cancel')])
        for order in po_records:
            order.state = 'cancel'
            order.unlink()
        utensils_rec = self.env['utensils.mst'].search([('function_id','=', self.ids[0]),('stage','!=','cancel')])        
        for utensils in utensils_rec:
            utensils.stage = 'cancel'
            utensils.unlink()
        self.sudo().with_context(reset_to_draft=True).write({'stage':'cancel'})
        self.hop_lead_id.cancel(reason)
        self.active = False

    @api.model
    def action_all_order_cancel(self):
        for res in self:
            if res.stage == 'invoice':
                raise UserError("You cannot cancel PO..")
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('state','in',('draft','sent','to approve'))])
            for line in po_rec:
                # line.button_cancel()
                line.state = 'cancel'
                line.unlink()
                

    def action_all_order_confirm(self):
        for res in self:
            if len(res.fuction_line_ids.mapped('out_sider_id').ids) > 0:
                po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','out_source')])
                if not po_rec:
                    raise UserError("Out Source Padding")
            if len(res.fuction_line_ids.mapped('insider_id').ids) > 0:
                po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','in_house')])
                if not po_rec:
                    raise UserError("In House Padding")
            if len(res.hospitality_line_ids) > 0:
                po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','service')])
                if not po_rec:
                    raise UserError("Labour Padding")
            if len(res.extra_service_line_ids) > 0:
                po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','addons')])
                if not po_rec:
                    raise UserError("Add-ons Padding")
            if len(res.material_line_ids) > 0:
                po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','row_material')])
                if not po_rec:
                    raise UserError("Raw-Material Padding")
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('state','in',('draft','sent','to approve'))])
            for line in po_rec:
                line.button_confirm()

    @api.onchange('date')
    def _onchange_date(self):  
        current_date = datetime.now().date()
        if  self.date:
            if  self.date < current_date:
                raise UserError("Can't Select Previous Date!!!!")
    
    visible_raw_material = fields.Boolean(string="Visible Raw Material",compute="_compute_po_raw_material")
    visible_labour = fields.Boolean(string="Visible Labour",compute="_compute_po_labour")
    visible_addons = fields.Boolean(string="Visible Addons",compute="_compute_po_addons")
    visible_out_source = fields.Boolean(string="Visible Out Source",compute="_compute_po_out_source_in_house")
    visible_in_house = fields.Boolean(string="Visible In House",compute="_compute_po_out_source_in_house")

    @api.depends('material_line_ids','visible_raw_material')
    def _compute_po_raw_material(self):
        for i in self:
            if len(i.material_line_ids) >= 1:
                tot_cat = len(self.material_line_ids.mapped('recipe_id.categ_id').ids)
                po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',self.ids[0]),('po_type','=','row_material'),('state','!=','cancel')]).mapped('category_id')
                if len(po_rec)  == tot_cat:
                    i.visible_raw_material = False
                else:
                    i.visible_raw_material = True
            else:
                i.visible_raw_material = False
    @api.depends('fuction_line_ids','visible_out_source','visible_in_house')
    def _compute_po_out_source_in_house(self):
        for i in self:
            in_house_purchase = []
            in_house = []
            out_source = []
            out_source_purchase = []
            blank_fun = []
            # in house po
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('state','!=','cancel'),('po_type','=','in_house')])
            for order in purchase_record:
                for line in order.order_line:
                    if line.fuction_line_id:
                        in_house_purchase.append(line.fuction_line_id.id)
            # out source po
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('state','!=','cancel'),('po_type','=','out_source')])
            for order in purchase_record:
                for line in order.order_line:
                    if line.fuction_line_id:
                        out_source_purchase.append(line.fuction_line_id.id)
            for line in  i.fuction_line_ids:
                if line.insider_id:
                    in_house.append(line.id)
                elif line.out_sider_id:
                    out_source.append(line.id)
                else:
                    blank_fun.append(line.id)
                    
            if len(in_house)+len(blank_fun) == len(in_house_purchase):
                i.visible_in_house = False
            else:
                i.visible_in_house = True

            if len(out_source)+len(blank_fun) == len(out_source_purchase):
                i.visible_out_source = False
            else:
                i.visible_out_source = True 
            i._compute_file_completed()
    @api.depends('hospitality_line_ids','visible_labour')
    def _compute_po_labour(self):
        # labour po
        for i in self:
            labour_purchase =[]
            black_labour =[]
            labour=[]
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('state','!=','cancel'),('po_type','=','service')])
            for order in purchase_record:
                for line in order.order_line:
                    if line.labour_line_id:
                        labour_purchase.append(line.labour_line_id.id) 
            for line in i.hospitality_line_ids:
                if line.vender_id:
                    labour.append(i.id)
                else:
                    black_labour.append(i.id)
            if len(labour)+len(black_labour)  == len(labour_purchase):
                i.visible_labour = False
            else:
                i.visible_labour = True
                i._compute_file_completed()

    @api.depends('extra_service_line_ids','visible_addons')
    def _compute_po_addons(self):
        # add-ons po
        for i in self:
            addons_purchase =[]
            black_addons =[]
            addons=[]
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('state','!=','cancel'),('po_type','=','addons')])
            for order in purchase_record:
                for line in order.order_line:
                    if line.service_line_id:
                        addons_purchase.append(line.service_line_id.id) 
            for line in i.extra_service_line_ids:
                if line.vender_id:
                    addons.append(i.id)
                else:
                    black_addons.append(i.id)
            if len(addons)+len(black_addons)  == len(addons_purchase):
                i.visible_addons = False
            else:
                i.visible_addons = True            
    
    def confirm_menu(self):
        self.stage = 'confirm'

    def name_get(self):
        function = []
        for fun in self:
            name = fun.party_name_id.name  + ' - '+  str(fun.date.strftime('%d-%m-%Y')) + ' - ' + dict(fun._fields['meal_type'].selection).get(fun.meal_type)
            function.append((fun.id, name))
        return function       


    @api.onchange('fuction_line_ids')
    def _onchange_function_id(self):
        line_list = []          
        main_list = []
        if not self.fuction_line_ids.insider_id:
            self.accompplishment_line_ids = False
            if self.fuction_line_ids:
                for rec in self.fuction_line_ids.mapped('item_id'):  
                    if rec.accomplishment:
                        line_list.append((0,0, {
                                    'item_id': rec.id,
                                }))
                self.accompplishment_line_ids = line_list
        if self.fuction_line_ids:
            for line in self.fuction_line_ids:
                if line.item_id:
                    main_list.append(line.item_id.id)

            self.recipes_ids = [(6,0,main_list)]
        else:
            self.recipes_ids = False
        for i in self:
            if len(i.fuction_line_ids.mapped('out_sider_id')) >= 1:
                 i.visible_out_source = True
            else:
                i.visible_out_source = False
            if len(i.fuction_line_ids.mapped('insider_id')) >= 1:
                 i.visible_in_house = True
            else:
                i.visible_in_house = False
            i._compute_file_completed()

    @api.onchange('meal_type')
    def _onchange_meal_type(self): 
        if self.meal_type == 'early_morning_tea':
            self.time = '07'
            self.am_pm = 'am'
        elif self.meal_type == 'breakfast':
            self.time = '08'
            self.am_pm = 'am'
        elif self.meal_type == 'brunch':
            self.time = '09'
            self.am_pm = 'am'
        elif self.meal_type == 'mini_meals':
            self.time = '10'
            self.am_pm = 'am'
        elif self.meal_type == 'lunch':
            self.time = '11'
            self.am_pm = 'am'
        elif self.meal_type == 'hi-tea':
            self.time = '04'
            self.am_pm = 'pm'
        elif self.meal_type == 'dinner':
            self.time = '07'
            self.am_pm = 'pm'
        elif self.meal_type == 'late_night_snacks':
            self.time = '11'
            self.am_pm = 'pm'


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
        
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hop.function') or _('New')
        
        return super(HopFunction, self).create(vals)
    
    @api.onchange('fuction_line_ids')
    def _onchange_fuction_line_ids(self):
        if self.fuction_line_ids:
            if self.no_of_pax == 0:
                raise UserError("Kindly Enter The No. Of Pax First!!!")
        self._compute_po_out_source_in_house()
        
        # if self.no_of_pax:
        #     self.fuction_line_ids.no_of_pax = self.no_of_pax
    
    # @api.onchange('no_of_pax')
    # def _onchange_no_of_pax(self):
    #     if self.no_of_pax > 0:
    #         for rec in self.fuction_line_ids:
    #             rec.no_of_pax = self.no_of_pax
    @api.onchange('skip_labour')
    def _onchange_skip_labour(self):
        if self.hospitality_line_ids:
            raise UserError('If you want to skip Labour than kindly remove all the Labour First')
        
    @api.onchange('skip_addons')
    def _onchange_skip_addons(self):
        if self.extra_service_line_ids:
            raise UserError('If you want to skip Add-ons than kindly remove all the Add-ons First')

    @api.onchange('stage')
    def _onchange_stage(self):
        if self.stage == "details":
            self.material_line_ids = False
        if self.stage == "confirm_menu":
            self.material_line_ids = False
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',self.ids[0]),('po_type','=','row_material'),('state','!=','cancel')])
            if len(po_rec) > 0:
                raise UserError('You can not go to back stage as Raw Materia is created if you still want to go to Confirm Menu stage than Cancel all the Raw Material PO First.')
            # po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',self.ids[0]),('state','in',('draft','sent','to approve'))])
            # for line in po_rec:
            #     line.state = 'cancel'
        if self.stage == "create_menu":
            self.material_line_ids = False
            if (not self.party_name_id or not self.mobile_num or not self.venue_address
                or not self.fuction_name_id or not self.date or not self.time or not self.am_pm 
                or not self.am_pm or not self.no_of_pax or not self.meal_type):
                raise UserError('All the fields are mandatory')
        if self.stage in ('purchase_order','manager_report'):
            self.material_line_ids = False
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',self.ids[0]),('po_type','=','row_material'),('state','!=','cancel')])
            if len(po_rec) > 0:
                raise UserError('You can not go to back stage as Raw Materia is created if you still want to go to Confirm Menu stage than Cancel all the Raw Material PO First.')
            # flg = False
            # for line in self.fuction_line_ids:
            #     if line.insider_id:
            #         flg = True
            #         break
            # if flg:
            #     if not self.material_line_ids:
            #         raise UserError('Create First Raw Material')
            if self.skip_labour == False:
                if not self.hospitality_line_ids:
                    raise UserError("Add the Labour First")
                for rec in self.hospitality_line_ids:
                    if rec.qty_person <= 0:
                        raise UserError('Enter Quantity/Preson First in Labour Tab')
                    if not rec.location:
                        raise UserError('Enter Location in Labour Tab')
            if self.skip_addons == False:
                if not self.extra_service_line_ids:
                    raise UserError("Add the Add-ons First")
            self.create_rm()
            # self.issue_rm()
            self._onchange_stage_manager_report()
            
        if self.stage in ('details','create_menu','confirm_menu','raw_materials'):
            if self.id:
                if  self.env['purchase.order'].search([('fuction_id_rec','=',self.ids[0]),('state','!=','cancel')]) :
                    raise UserError('Purchase order is created.')
        if self.stage == "confirm_menu":
            self.material_line_ids = False
            # if not self.fuction_line_ids:
            #     raise UserError("Add the Menu First")
            utensils_id = self.env['product.product'].search([('utility_type','=','utensils')])
            utensils_list = []
            for i in utensils_id:
                if self.utensils_line_ids:
                    for rec in self.utensils_line_ids:
                        flg=True
                        if i.id not in rec.utensils_id.ids:
                            flg=False
                    if  flg:
                        utensils_list.append((0,0, {
                                    'utensils_id' : i.id,
                                    'uom': i.uom_id.id,
                                    'utensils_type' : i.utensils_type,
                                    'uten_cost' : i.standard_price,
                                }))
                else:
                    utensils_list.append((0,0, {
                                    'utensils_id' : i.id,
                                    'uom': i.uom_id.id,
                                    'utensils_type' : i.utensils_type,
                                    'uten_cost' : i.standard_price,
                                }))
            if utensils_list:
                self.utensils_line_ids = utensils_list

        if (self.stage == "raw_materials" or self.stage == "purchase_order" or self.stage == "manager_report"
            or self.stage == "invoice" or self.stage == "confirm_menu"):
            for rec in self.fuction_line_ids:
                if not rec.insider_id and not rec.out_sider_id:
                    raise UserError('Select In-House or Out-Source First')
                if rec.insider_id and rec.per_qty <= 0:
                    raise UserError('Enter the Per Head Quantity First')
                if rec.out_sider_id and rec.no_of_pax <= 0:
                    raise UserError('Enter the Number of PAX First')
        if self.stage == "raw_materials":
            self.material_line_ids = False
            if not self.hospitality_line_ids:
                raise UserError("Add the Labour First")
            # if not self.extra_service_line_ids:
            #     raise UserError("Add the Add-ons First")
            # self.issue_rm()
        if self.stage in ('details','create_menu','confirm_menu','raw_materials'):
            self.utensils_line_ids = False

        if self.stage == "invoice":
            if self.visible_raw_material == True :
                raise UserError("Genrate Raw Material PO First..")
            elif self.visible_labour == True :
                raise UserError("Genrate Labour PO First..")
            elif self.visible_addons == True :
                raise UserError("Genrate Add-ons PO First..")
            elif self.visible_out_source == True :
                raise UserError("Genrate Out Source PO First..")
            elif self.visible_in_house == True :
                raise UserError("Genrate In-house PO First..")
    #         self.file_completed()

    
    # def file_completed(self):
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'File Completed Successfully',
    #             'img_url': '/ct_function_v15/static/img/smile.svg',
    #             'type': 'rainbow_man',
    #         }
    #     }
            
    def create_rm(self):
        record = self.env['hop.recipe.rm'].search([('function_id','=',self.ids[0])])
        for line in record:
            sql = "delete from hop_rec_rm_line WHERE recipe_rm_id = "+ str(line.ids[0])
            self._cr.execute(sql)

        query = "DELETE FROM hop_recipe_rm WHERE function_id =" + str(self.ids[0])
        self._cr.execute(query)
        for line in self.fuction_line_ids:
            if line.insider_id:
                    rm_list = []
                    for rec in line.item_id.raw_materials_ids:      
                        req_wt = (rec.weight*line.qty)/rec.recipes_category_id.qty
                        rm_list.append((0,0, {
                                'product_id': rec.item_id.id,
                                'uom': rec.uom.id,
                                'weight':req_wt,
                                'cost':req_wt * rec.item_cost,
                                'item_cost':rec.item_id.standard_price
                            }))
                    self.env['hop.recipe.rm'].with_context(create_one=True).create({
                        'recipe_id': line.item_id.id,
                        'fun_date': line.fuction_id.date,
                        'venue_address': line.fuction_id.venue_address,
                        'rec_rm_ids': rm_list,
                        'function_id':line.fuction_id.ids[0]})
        self.issue_rm()
    def issue_rm(self):
        query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(self.ids[0])
        self._cr.execute(query)
        # self.material_line_ids = False
        # for i in self.fuction_line_ids:
        #     if not i.insider_id and not i.out_sider_id:
        #         raise UserError("Kindly Enter The Outsider Or Insider First!!!")
        #     if i.insider_id:
        #         if not i.per_qty:
        #             raise UserError("Kindly Enter The Per Head Quantity First!!!")
        #     if not i.qty and i.insider_id:
        #         raise UserError("Kindly Enter The Quantity First!!!")
        rm_list = []
        records = self.env['hop.recipe.rm'].search([('function_id','=',self.ids[0])])
        for rec in records:
                rm_list.append((0,0, {
                        'name': rec.recipe_id.name,
                        'display_type': 'line_section',
                        'recipes_id' : rec.recipe_id.id
                    }))
                for rm in rec.rec_rm_ids:
                    record = self.fuction_line_ids.filtered(lambda l: l.item_id.id == rec.recipe_id.id)
                    rm_list.append((0,0, {
                        'rm_vender_id': rm.product_id.vender_id.id,
                        'recipe_id': rm.product_id.id,
                        'name': rm.product_id.name,
                        'display_type':False,
                        'uom':rm.product_id.uom_id.id,
                        'weight':rm.weight,
                        'cost_price':rm.product_id.standard_price,
                        'item_cost':rm.cost,
                        'vender_id': record.insider_id.id or record.out_sider_id.id,
                        'recipes_id' : rec.recipe_id.id
                    }))
        if rm_list:
            self.material_line_ids = rm_list        
    # def issue_rm(self):
    #     self.material_line_ids=False
    #     flag = False
    #     table_rows = []
    #     for line in self.fuction_line_ids:
    #         if line.insider_id:
    #             for rec in line.item_id.raw_materials_ids:
    #                 req_wt = (rec.weight * line.qty) / rec.recipes_category_id.qty
    #                 print("...........",round(req_wt,2))
    #                 if round(req_wt,2) == 0:
    #                     flag = True
    #                     table_rows.append(f"{html_escape(line.item_id.name)}\t\t{html_escape(rec.item_id.name)}")

    #     if flag:
    #         error_message = _(
    #             "Raw Material Zero Weight\n"
    #             "Item\t\tRaw Material\n"
    #             "{divider}\n"
    #             "{rows}"
    #         ).format(divider="-" * 80, rows="\n".join(table_rows))
    #         raise UserError(error_message)

    #     for i in self.fuction_line_ids:
    #         if not i.insider_id and not i.out_sider_id:
    #             raise UserError("Kindly Enter The Outsider Or Insider First!!!")
    #         if i.insider_id:
    #             if not i.per_qty:
    #                 raise UserError("Kindly Enter The Per Head Quantity First!!!")
    #         if not i.qty and i.insider_id:
    #             raise UserError("Kindly Enter The Quantity First!!!")
    #     rm_list = []
    #     for rec in self.fuction_line_ids:
    #         if rec.insider_id:
    #             rm_list.append((0,0, {
    #                     'name': rec.item_id.name,
    #                     'display_type': 'line_section',
    #                 }))
    #             for rm in rec.item_id.raw_materials_ids:
    #                 if rm.item_id.description == "<p><br></p>":
    #                     description = rm.item_id.name
    #                 else:
    #                     description = rm.item_id.description
    #                 wt = (rm.weight*rec.qty)/rm.recipes_category_id.qty
    #                 item_cost = wt * rm.item_cost
    #                 rm_list.append((0,0, {
    #                     'recipe_id': rm.item_id.id,
    #                     'name': rm.item_id.name,
    #                     'display_type':False,
    #                     'uom':rm.uom.id,
    #                     'weight':wt,
    #                     'cost_price':rm.item_cost,
    #                     'item_cost':item_cost,
    #                     'vender_id': rec.insider_id.id or rec.out_sider_id.id
    #                 }))
    #     if rm_list:
    #         self.material_line_ids = rm_list
        

    def set_to_drafr(self):
        self.stage = 'draft'
        self.material_line_ids = False

    
    def action_create_po(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Raw Material Purchase Order',
                'view_mode': 'form',
                'res_model': 'ct.purchase.wiz',
                'target':'new',
            }
    
    # def action_hospitality(self):
    #     return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'hospitality',
    #             'view_mode': 'form',
    #             'res_model': 'ct.hospitality.wiz',
    #             'target':'new',
    #         }

    def action_create_service_po(self):
        for line in self.hospitality_line_ids:
            if not line.vender_id:
                raise UserError('Add First Vendor in Labour!!!!')
            if line.qty_person <1:
                raise UserError('Add First Quantity/Person in Labour!!!!')
            if not line.location:
                raise UserError('Select location!!!!')
        return {
                'type': 'ir.actions.act_window',
                'name': 'Labour Purchase Order',
                'view_mode': 'form',
                'res_model': 'hospitality.shift.wizard',
                'target':'new',
            }

    # def action_create_service_po(self):
    #     if self.hospitality_line_ids:
    #         service_pr = self.env.ref('ct_function_v15.product1').id
    #         product_rec = self.env['product.product'].search([('product_tmpl_id','=',service_pr)])
    #         for i in self.hospitality_line_ids.mapped('vender_id'):
    #             line_list = []
    #             for record in self.hospitality_line_ids.filtered(lambda l: l.vender_id.id == i.id):
    #                 line_list.append((0,0, {
    #                         'product_id': product_rec.id,
    #                         'name':'Services Product',
    #                         'no_of_pax': '',
    #                         'product_qty': record.qty_person,
    #                         'price_unit':'',
    #                         'product_uom':record.uom_id.id,
    #                 }))
    #             purc_rec = self.env['purchase.order'].create({
    #                     'partner_id': i.id,
    #                     'fuction_id_rec': self.id,
    #                     'po_type': 'service',
    #                     'order_line': line_list,
        
    #                 })
    #         self.is_service_po = True   
    def action_create_addons(self):
        for line in self.extra_service_line_ids:
            if not line.vender_id:
                raise UserError('Add First Vendor in Labour!!!!')
            if line.qty_ids <1:
                raise UserError('Add First Quantity/Person in Add-ons!!!!')
        return {
                'type': 'ir.actions.act_window',
                'name': 'Add-ons Purchase Order',
                'view_mode': 'form',
                'res_model': 'hop.extra.service.wizard',
                'target':'new',
            }
    # def action_create_addons(self):
    #     if self.extra_service_line_ids:
    #         for i in self.extra_service_line_ids.mapped('vender_id'): 
    #             line_list = []
    #             for record in self.extra_service_line_ids.filtered(lambda l: l.vender_id.id == i.id):
    #                 line_list.append((0,0, {
    #                         'product_id': record.service_id.id,
    #                         'name':'Services Product',
    #                         'no_of_pax': '',
    #                         'product_qty': record.qty_ids,
    #                         'price_unit':'',    
    #                         'product_uom':record.uom_id.id,
    #                 }))
    #             purc_rec = self.env['purchase.order'].create({
    #                     'partner_id': i.id,
    #                     'fuction_id_rec': self.id,
    #                     'po_type': 'addons',
    #                     'order_line': line_list
    #                 })
    #         self.is_addons_po = True

    def action_outsource_and_in_house_po(self):
        for rec in self.fuction_line_ids:
            if not rec.insider_id and not rec.out_sider_id:
                raise UserError('Select In-House or Out-Source First')
            if rec.insider_id and rec.per_qty <= 0:
                raise UserError('Enter the Per Head Quantity First')
            if rec.out_sider_id and rec.no_of_pax <= 0:
                raise UserError('Enter the Number of PAX First')
        vals = {}
        if self.env.context.get('out_sider',False):
            vals.update({"type":'out'})
            return {
                'type': 'ir.actions.act_window',
                'name': 'Out-Source Purchase Order',
                'view_mode': 'form',
                'res_model': 'hop.fuction.out.source.and.in.house.wizard',
                'target':'new',
                'context':vals
            }

        elif self.env.context.get('in_house',False):
             vals.update({"type":'in'})
             return {
                'type': 'ir.actions.act_window',
                'name': 'In-House Purchase Order',
                'view_mode': 'form',
                'res_model': 'hop.fuction.out.source.and.in.house.wizard',
                'target':'new',
                'context':vals
            }

        
    # def action_outsource_po(self):
    #     for i in self.fuction_line_ids.mapped('out_sider_id'):
    #         line_list = []
    #         for record in self.fuction_line_ids.filtered(lambda l: l.out_sider_id.id == i.id):
    #             # for record in self.fuction_line_ids:
    #             line_list.append((0,0, {
    #                     'product_id': record.item_id.product_id.id,
    #                     'name':'',
    #                     'no_of_pax': record.no_of_pax,
    #                     'product_qty': 1,
    #                     'price_unit':1,
    #                     'product_uom':record.item_id.product_id.uom_id.id,
    #             }))
    #         purc_rec = self.env['purchase.order'].create({
    #                     'partner_id': i.id,
    #                     'fuction_id_rec': self.id,
    #                     'is_out_sider': True,
    #                     'venue_address': self.venue_address,
    #                     'order_line': line_list,
    #                     'po_type':'out_source'
    #                 })
            
    # def action_in_house_po(self):
    #     for i in self.fuction_line_ids.mapped('insider_id'):
    #         line_list = []
    #         for record in self.fuction_line_ids.filtered(lambda l: l.insider_id.id == i.id):
    #             # for record in self.fuction_line_ids:
    #             line_list.append((0,0, {
    #                     'product_id': record.item_id.product_id.id,
    #                     'name':'',
    #                     'no_of_pax': record.no_of_pax,
    #                     'product_qty': 1,
    #                     'price_unit':1,
    #                     'product_uom':record.item_id.product_id.uom_id.id,
    #             }))
    #         purc_rec = self.env['purchase.order'].create({
    #                     'partner_id': i.id,
    #                     'fuction_id_rec': self.id,
    #                     'is_out_sider': True,
    #                     'venue_address': self.venue_address,
    #                     'order_line': line_list,
    #                     'po_type':'in_house'
    #                 })
    
    

    @api.depends('po_count')
    def _count_po_rec(self):
        for i in self:
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','row_material'),('state','!=','cancel')])
            i.po_count = len(po_rec)
            if len(po_rec) == 0:
                i.is_service_po = False 
                i.is_addons_po = False     

    def action_create_po_count(self):
        domain = []  
        domain.append(('fuction_id_rec','=',self.id))
        if self.env.context.get('po_type') == 'row_material':
            domain.append(('po_type','=','row_material'))
        elif self.env.context.get('po_type') == 'out_source':
            domain.append(('po_type','=','out_source'))
        elif self.env.context.get('po_type') == 'in_house':
            domain.append(('po_type','=','in_house'))
        elif self.env.context.get('po_type') == 'service':
            domain.append(('po_type','=','service'))
        elif self.env.context.get('po_type') == 'addons':
            domain.append(('po_type','=','addons'))
        po_rec  = self.env['purchase.order'].search(domain)
        return  {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'view_mode': 'tree,form',
            'domain': [('id','in',po_rec.ids)],
            'res_model': 'purchase.order',
            'context': "{'create': False}",
            'views': [(self.env.ref('purchase.purchase_order_view_tree').id, 'tree'),(False, 'form')],
        }
    
    def action_apply_all(self):
        hospital_list = []
        if self.vender_id and self.hospitality_ids:
            for i in self.hospitality_ids:
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
                    mrng = self.env.ref('ct_function_v15.shift1').id
                    eve = self.env.ref('ct_function_v15.shift2').id
                    night = self.env.ref('ct_function_v15.shift3').id
                    late_night = self.env.ref('ct_function_v15.shift4').id
                    shift_time = False
                    if mrng:
                        if i.id == mrng :
                            shift_time = '8'
                    if eve:
                        if i.id == eve :
                            shift_time = '4'
                    if night:
                        if i.id == night :
                            shift_time = '8'
                    if late_night:
                        if i.id == late_night :
                            shift_time = '12'
                    hospital_list.append((0,0, {
                            'vender_id' : self.vender_id.id,
                            'service_id' : self.service_id.id,
                            'hospitality_ids' : i.id,
                            'shift_date' : user_date,
                            'uom_id':self.service_id.uom_id.id,
                            'shift_time':shift_time
                            }))  

        if not self.vender_id:
            raise UserError("Please Enter Vender First !!!")

        self.hospitality_line_ids = hospital_list
        self.hospitality_ids = False
        self.vender_id = False
        self.service_id = False

        # for line in self.hospitality_line_ids:
        #     line._onchange_hospitality_ids()

    @api.onchange('stage')
    def _onchange_stage_manager_report(self):
        if self.ids:
            utensils_rec = self.env['utensils.mst'].search([('function_id','=', self.ids[0]),('stage','=','draft')])
            if utensils_rec:
                if self.stage not in("manager_report","invoice"):
                    model_ids = tuple(utensils_rec.ids)
                    query = "DELETE FROM utensils_mst WHERE id IN %s"
                    self.env.cr.execute(query, [model_ids])

        # if self.stage == "manager_report":
        line_list = []
        for record in self.fuction_line_ids:
            line_list.append((0,0, {
                'category_id': record.category_id.id,
                'item_id': record.item_id.id,
                'no_of_pax': record.no_of_pax,
                'per_qty': record.per_qty,
                'qty': record.qty,
                'uom': record.uom.id,
                'insider_id':record.insider_id.id,
                'out_sider_id':record.out_sider_id.id,
                'cost':record.cost,
                'rate':record.rate,
                'instruction':record.instruction,
            }))
            
        utensils_list = []
        for line in self.utensils_line_ids:
            utensils_list.append((0,0, {
                'utensils_id': line.utensils_id.id,
                'uom': line.uom.id,
                'utensils_type': line.utensils_type,
                'qty': line.qty,
                'uten_cost': line.uten_cost,
            }))

        check = self.env['utensils.mst'].search([('function_id','=', self.ids[0])])
        if not check:
            rec = self.env['utensils.mst'].create({
                    'name':self.name,
                    'function_id': self.ids[0],
                    'venue_address': self.venue_address,
                    'fuction_name_id': self.fuction_name_id.id,
                    'meal_type': self.meal_type,
                    'time': self.time,
                    'am_pm': self.am_pm,
                    'date': self.date,
                    'remarks': self.remarks,
                    'no_of_pax': self.no_of_pax,
                    'manager_name_id': self.manager_name_id.id,
                    'fuction_line_ids': line_list,
                    'utensils_line_ids': utensils_list,
                })     

    @api.depends('lead_order_count')
    def _cumpute_lead_order_count(self):
        for i in self:
            record = self.env['hop.lead'].search([('hop_funtion_id','=',i.id)])
            i.lead_order_count = len(record)


        # print(".............calendar_id................",calendar_id)
    def lead_order_open(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lead Order',
            'view_mode': 'tree,form',
            'res_model': 'hop.lead',
            'domain': [('hop_funtion_id','=', self.id)],
            'context': "{'create': False}"
        }
    
    @api.depends('quotation_count')
    def _compute_quotation_count(self):
        for i in self:
            record = self.env['sale.order'].search([('lead_id','=',i.hop_lead_id.id)])
            i.quotation_count = len(record)


    def quotation_open(self):
       
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotations',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('lead_id','in', self.hop_lead_id.ids)],
            'context': "{'create': False}"
        }
    
    def _compute_po_count(self):
        for i in self:
            po_out  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','out_source'),('state','!=','cancel')])
            i.out_source = len(po_out)
            po_in  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','in_house'),('state','!=','cancel')])
            i.in_house = len(po_in)
            po_ser  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','service'),('state','!=','cancel')])
            i.service =len(po_ser)
            po_add  = self.env['purchase.order'].search([('fuction_id_rec','=',i.id),('po_type','=','addons'),('state','!=','cancel')])
            i.addons = len(po_add)

    @api.onchange('material_line_ids')
    def _onchange_material_line_ids(self):
        for i in self:
            if len(i.material_line_ids) >= 1:
                i.visible_raw_material = True
            else:
                i.visible_raw_material = False
            i._compute_file_completed()

    @api.onchange('hospitality_line_ids')
    def _onchange_hospitality_line_ids(self):
        for i in self:
            if len(i.hospitality_line_ids) >= 1:
                i.visible_labour = True
            else:
                i.visible_labour = False
            i._compute_po_labour()
            i._compute_file_completed()

    @api.onchange('extra_service_line_ids')
    def _onchange_extra_service_line_ids(self):
        for i in self:
            if len(i.extra_service_line_ids) >= 1:
                i.visible_addons = True
            else:
                i.visible_addons = False
            i._compute_po_addons()
            i._compute_file_completed()
        
class HopFunctionLine(models.Model):
    _name = "hop.fuction.line"

    fuction_id = fields.Many2one('hop.function',string="Function", ondelete='cascade', log_access=True)

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
    type = fields.Selection([('in','In'),('out','Out')],string="Type")
    helper = fields.Integer(string="Helper")
    chief = fields.Integer(string="Chef")
    jobwork_type = fields.Selection([('in_house','In-House'),('out_source','Out-Source')],string="Work Type")
    total_cost = fields.Float('Total Cost')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    # website = fields.Char('Website URL', compute='_compute_website_url')

    # def _compute_website_url(self):
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     for record in self:
    #         record.website = f'{base_url}/my-page/{record.id}'
    def po_valication(self):
        if self.ids != []:
            records  = self.env['purchase.order.line'].search([('fuction_line_id','=',self.ids[0])])
            for record in records:
                if record.state != 'cancel':
                        if record :
                            if self.insider_id:
                                raise UserError("In-house PO already generate...")
                            elif self.out_sider_id:
                                raise UserError("Out Source PO already generate...")
            
    def unlink(self):
        self.po_valication()
        return super().unlink()

    @api.onchange('category_id','no_of_pax')
    def _onchange_category_id(self):
        self.po_valication()
    @api.onchange('insider_id','out_sider_id')
    def _onchange_no_of_pax(self):
        self.po_valication()
        if self.insider_id:
            # for rec in self.fuction_id:name
            self.no_of_pax = self.fuction_id.no_of_pax
            self.type = 'in'
            self.per_qty = 1
        else:
            self.type = 'out'
            # self.no_of_pax = 0
            # self.per_qty = 0
            self.per_qty = 1
            self.no_of_pax = self.fuction_id.no_of_pax

    @api.onchange('per_qty','no_of_pax')
    def _onchange_per_qty(self):
        self.po_valication()
        if self.insider_id and self.item_id:
            total_sum = sum(self.item_id.raw_materials_ids.mapped('price'))/self.item_id.qty
            self.cost = self.qty * total_sum

        if self.per_qty:
            self.qty = self.no_of_pax * self.per_qty
        else:
            self.qty = 0

    @api.onchange('insider_id')
    def _onchange_insider_id(self):
        if self.insider_id:
            if self.out_sider_id:
                raise UserError("You Can Select Insider As You Already Selected The Outsider!!!")
            if not self.item_id.raw_materials_ids:
                action = self.env.ref('ct_inventory_v15.hop_recipes_action')
                msg = _('Can not create menu until you Create recipes Raw Materials.!!!')
                context = {
                    # 'default_res_id': self.item_id.id,
                    # 'active_id': self.item_id.id,
                    # 'active_ids': [self.item_id.id]
                }
                action['context'] = context
                raise RedirectWarning(msg, action.id, _('Go to Recipes'))
            total_rec_value = sum(self.item_id.raw_materials_ids.mapped('price'))
            self.cost = (self.qty * total_rec_value)/100 
       
    @api.onchange('qty')
    def _onchange_qty(self):
        self.po_valication()
        if self.insider_id:
            total_rec_value = sum(self.item_id.raw_materials_ids.mapped('price'))
            self.cost = (self.qty * total_rec_value)/100 
        if self.item_id.rate>0:
            self.rate = (self.item_id.rate*self.qty)/self.item_id.qty
        # if self.qty:
        #     if self.qty == 0.00:
        #         raise UserError("You can select Quantiy!!!")

    @api.onchange('out_sider_id')
    def _onchange_out_sider_id(self):
        if self.insider_id:
            raise UserError("You Can Select Outsider As You Already Selected The Insider!!!")        
        
        
    @api.onchange('item_id')
    def _onchange_item_id(self):
        self.po_valication()
        if self.item_id:
            if not self.item_id.uom:
                raise UserError('Select UoM First in %s'%self.item_id.name)            
            self.uom = self.item_id.uom.id
        
    def open_rm_list(self):
        record = self.env['hop.recipe.rm'].search([('function_id','=',self.fuction_id.ids[0]),('recipe_id','=',self.item_id.id)])
        if record:           
            return {
            'type': 'ir.actions.act_window',
            'name': 'Raw Materials',
            'view_mode': 'form',
            'res_model': 'hop.recipe.rm',
            'res_id': record.id,
            'target':'new',
        }   
    
    # def open_rm_list(self):
    #     rm_list = []
    #     for rec in self.item_id.raw_materials_ids:            
    #         req_wt = (rec.weight*self.qty)/rec.recipes_category_id.qty
    #         rm_list.append((0,0, {
    #                 'product_id': rec.item_id.id,
    #                 'uom': rec.uom.id,
    #                 'weight':req_wt
    #             }))
    #     return{
    #         'name': 'Raw Materials',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'hop.recipe.rm',
    #         'context': {'default_recipe_id':self.item_id.id,'default_fun_date':self.fuction_id.date,
    #                     'default_venue_address':self.fuction_id.venue_address,'default_rec_rm_ids':rm_list},
    #         'target':'new',
    #     }

class RawMaterial(models.Model):
    _name = 'hop.raw.materal'
    _description = 'function.raw.material'

    fuction_id = fields.Many2one('hop.function',string="Function", ondelete='cascade', log_access=True)

    recipe_id = fields.Many2one('product.product', string='Raw Material',track_visibility='onchange')
    sequence = fields.Integer()
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name=fields.Text('Raw Materials')
    uom = fields.Many2one('uom.uom',string="Uom",track_visibility='onchange')
    weight = fields.Float(string="Quantity",track_visibility='onchange',digits='Stock Weight')
    req_weight = fields.Float(string="Change in Quantity",track_visibility='onchange',digits='Stock Weight')
    cost_price = fields.Float(string="Cost Price",track_visibility='onchange')
    item_cost = fields.Float(string="Item Cost",track_visibility='onchange', compute="_compute_req_weight")
    sequence = fields.Integer(string='Sequence')
    vender_id = fields.Many2one('res.partner',string="Vendor",track_visibility='onchange',domain=[('is_vender','=',True)])
    rm_vender_id = fields.Many2one('res.partner',string="RM Vendor",track_visibility='onchange',domain=[('is_vender','=',True)])
    recipes_id = fields.Many2one('hop.recipes', string='Recipe Name')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)


    
    @api.onchange('recipe_id')
    def _onchange_recipe_id(self):
        if self.recipe_id.description:
            self.name = self.recipe_id.description
        else:
            self.name = self.recipe_id.name
    
    @api.depends('req_weight','cost_price','req_weight')
    def _compute_req_weight(self):
        for rec in self:
            if rec.req_weight > 0:
                rec.item_cost = rec.req_weight*rec.cost_price
            else:
                rec.item_cost = rec.weight*rec.cost_price

    # @api.model
    # def create(self, vals):
    #     if not  vals.get('name',False):
    #         vals.update({'name':''})
      
    #     res = super(RawMaterial, self).create(vals)
    #     return res

class UtensilsMst(models.Model):
    _name = 'hop.utensils'
    _description = 'function.utensils'

    fuction_id = fields.Many2one('hop.function',string="Function", ondelete='cascade', log_access=True)

    utensils_id = fields.Many2one('product.product', string='Utensils',track_visibility='onchange', domain=[('utility_type','=','utensils')])
    uom = fields.Many2one('uom.uom',string="Uom",track_visibility='onchange')
    utensils_type = fields.Selection([('ground','Ground'),('kitche','Kitchen'),('disposable','Disposable'),('decoration','Decoration')],string="Utensils Type",tracking=True)
    qty = fields.Float(string="Quantity",track_visibility='onchange')
    uten_cost = fields.Float(string="Utensil Cost",track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)


    @api.onchange('utensils_id')
    def _onchange_utensils_id(self):
        if self.utensils_id:
            self.uom = self.utensils_id.uom_id.id
            self.utensils_type = self.utensils_id.utensils_type
            self.uten_cost = self.utensils_id.standard_price

        
class HospitalityShiftLine(models.Model):
    _name = 'hospitality.shift.line'
    _description = 'Hospitality Shift Line'


    hs_id = fields.Many2one('hop.function',string="Hospitality", ondelete='cascade', log_access=True)

    vender_id = fields.Many2one('res.partner',string="Vender Name",domain=[('is_vender','=',True)] ,tracking=True)
    service_id = fields.Many2one('product.product', string='Vendor Category',track_visibility='onchange')
    hospitality_ids = fields.Many2one('ct.hospitality.shift',string="Hospitality Shift",tracking=True)
    # morning = fields.Datetime(string="Morrning Shift",)
    # evening = fields.Datetime(string="Evening Shift")
    # night = fields.Datetime(string="Night Shift")
    # early_morning = fields.Datetime(string="Early Morrning Shift")
    cost = fields.Float(string="Cost",track_visibility='onchange')
    rate = fields.Float(string="Rate",track_visibility='onchange')
    shift_date = fields.Date(string="Shift Date")
    shift_time = fields.Float(string="Shift Time")
    remarks = fields.Char(string="Shift Remarks")
    location = fields.Selection([
        ('add_venue', "At Venue"),
        ('add_godown', "At Godown")], default=False, string="Location")
    qty_person = fields.Float(string="Quantity/Person")
    uom_id = fields.Many2one('uom.uom', string="UOM")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    # is_morning = fields.Boolean(string="Is Morning")
    # is_evening = fields.Boolean(string="Is evening")
    # is_night = fields.Boolean(string="Is night")
    # is_early_morning = fields.Boolean(string="Is Early Morning")
    def po_valication(self):
        if self.ids != []:
            records  = self.env['purchase.order.line'].search([('labour_line_id','=',self.ids[0])])
            for record in records:
                if record.state != 'cancel':
                    if record :
                        print("*********************************",record,record.order_id)
                        raise UserError("Labour PO already generate...")

    @api.onchange('vender_id','service_id','qty_person','shift_date','shift_time','location')
    def _onchange_vender_id(self):
        self.po_valication()       
            
    def unlink(self):
        self.po_valication()
        return super().unlink()


    @api.onchange('qty_person')
    def _onchange_(self):
        self.po_valication()
        if self.qty_person <1 and self.service_id:
            raise UserError('Add First Quantity/Person!!!!')

    @api.onchange('hospitality_ids')
    def _onchange_hospitality_ids(self): 
        self.po_valication()
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


    # @api.onchange('hospitality_ids')
    # def _onchange_hospitality_ids(self):
    #     mrng = self.env.ref('ct_function_v15.shift1').id
    #     eve = self.env.ref('ct_function_v15.shift2').id
    #     night = self.env.ref('ct_function_v15.shift3').id
    #     er_mrng = self.env.ref('ct_function_v15.shift4').id
       
    #     if mrng:
    #         if mrng in self.hospitality_ids.ids:
    #             self.is_morning = True
    #         else:
    #             self.is_morning = False

    #     if eve:
    #         if eve in self.hospitality_ids.ids:
    #             self.is_evening = True
    #         else:qty_person
    #             self.is_evening = False
        
    #     if night:
    #         if night in self.hospitality_ids.ids:
    #             self.is_night = True
    #         else:
    #             self.is_night = False
        
    #     if er_mrng:
    #         if er_mrng in self.hospitality_ids.ids:
    #             self.is_early_morning = True
    #         else:
    #             self.is_early_morning = False

class HospitalityShiftLine(models.Model):
    _name = 'hop.extra.service.line'
    _description = 'Extra Service Line'


    vender_id = fields.Many2one('res.partner',string="Vender Name",domain=[('is_vender','=',True)] ,tracking=True)
    extra_service_id = fields.Many2one('hop.function',string="Hospitality", ondelete='cascade', log_access=True)

    service_id = fields.Many2one('product.product', string='Vendor Category',track_visibility='onchange',required=True)
    qty_ids = fields.Float(string="Quantity/Person",tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UoM')
    price = fields.Float(string="Price",tracking=True)
    cost = fields.Float(string="Cost",tracking=True)
    date = fields.Date(string="Date")
    time = fields.Float(string="Time")
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    instruction = fields.Char(string="Instruction",track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    def po_valication(self):
        if self.ids != []:
            records  = self.env['purchase.order.line'].search([('service_line_id','=',self.ids[0])])
            for record in records:
                if record.state != 'cancel':
                    if record :
                        raise UserError("Add-ons PO already generate...")
        
    @api.onchange('vender_id')
    def _onchange_vender_id(self):
        self.po_valication()

    def unlink(self):
        self.po_valication()
        return super().unlink()

    @api.onchange('date')
    def _onchange_date(self):  
        current_date = datetime.now().date()
        if  self.date:
            if  self.date < current_date:
                raise UserError("Can't Select Previous Date!!!!")

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.price, self.uom_id = self.service_id.standard_price, self.service_id.uom_id
            
class AccomplishmentLine(models.Model):
    _name="hop.accomplishment.line"

    function_id = fields.Many2one('hop.function',string="Function")

    item_id = fields.Many2one('hop.recipes',string="Item Name")

    accomplishment_id = fields.Many2many('hop.recipes','function_accomplishment_id_ref',string="Accomplishment Item",
                      domain=lambda self: "[('category_id', '=', %s)]" % self.env.ref('ct_function_v15.rec_cat_1').id)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
    
class Inventory(models.Model):
    _name = 'hop.inventory'

    inventory_id = fields.Many2one('hop.function',string="Inventory")
    type = fields.Selection([('issue','Issue'),('return','Return')],string="Type")
    product_id = fields.Many2one('product.product',string="Product")
    qty = fields.Float(string="Qty")
    uom_id = fields.Many2one('uom.uom',string="Uom")
    cost = fields.Float(string="Cost",tracking=True)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    @api.onchange('product_id','qty')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.cost = self.qty * self.product_id.standard_price

class AccountPayment(models.Model):
    _inherit = "account.payment"
    create_type = fields.Selection([('normal','Normal'),('bill','Bill')],string="Type")
    remarks = fields.Text(string="Remarks")
    phone = fields.Char(related='partner_id.phone',string="Whatsapp Mo.") 

    @api.model
    def create(self, vals):
        print("*************",vals)
        res =  super(AccountPayment, self).create(vals)
        if res.create_type == 'normal':
            res.action_post()
        return res