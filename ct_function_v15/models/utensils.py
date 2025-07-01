from odoo import api, models, fields, _ 
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from datetime import date

class UtensilsMaster(models.Model):
    _name = "utensils.mst"
    _inherit = ['mail.thread']
    _description = "Utensils Master"
    _rec_name = "function_id"

    name = fields.Char(string="Number",readonly=True, copy=False, default='New',tracking=True)
    stage = fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')],string="Stage",default="draft",tracking=True,readonly=True)
    function_id = fields.Many2one('hop.function',string="Function",tracking=True,readonly=True)
    # mobile_num = fields.Char(string="Mobile Number",tracking=True)
    fuction_name_id = fields.Many2one('hop.function.mst',string="Function Name",tracking=True,readonly=True)
    date = fields.Date(string="Function Date",default=fields.Date.context_today,tracking=True,readonly=True)
    # emergency_contact = fields.Text(string="Emergency Contact")
    remarks = fields.Text(string="Remarks",tracking=True,readonly=True)
    manager_name_id = fields.Many2one('res.partner',string="Manager Name",domain=[('is_vender','=',True)] ,tracking=True)
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type",tracking=True, default="early_morning_tea",readonly=True)
    no_of_pax = fields.Integer(string="No Of Pax",tracking=True,readonly=True)
    time = fields.Float(string="Time",tracking=True,readonly=True)
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True,readonly=True)
    venue_address = fields.Text('Venue Address')
    po_count = fields.Integer(string='PO Count',compute='_count_po_rec',readonly=True)
    vender_id = fields.Many2one('res.partner',string="Vendor",domain=[('is_vender','=',True)],readonly=True)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)


    fuction_line_ids = fields.One2many('utensils.mst.line', 'fuction_id',string="Function Line",tracking=True,readonly=True)
    utensils_line_ids = fields.One2many('utensils.mst.page', 'fuction_id',string="Utensils Line",tracking=True)


    create_raw_utensils = fields.Boolean(string="Create Raw Utensils" , compute="compute_create_raw_utensils")

    @api.onchange('manager_name_id')
    def _onchange_manager_name_id(self):
        print("--------------------------",self.function_id.id,self.function_id.ids)
        function_id = self.env['hop.function'].search([('id','=',self.function_id.id)])
        if function_id:
            function_id.manager_name_id = self.manager_name_id.id
        pass
    
    @api.depends('create_raw_utensils')
    def compute_create_raw_utensils(self):
        for i in self:
            record = self.env['hop.add.utensils'].search([('id','not in',self.env['product.product'].search([('utility_type', '=','utensils')]).ids)])
            if record:
                record.unlink()
            for record in self.env['product.product'].search([('id', 'not in',self.env['hop.add.utensils'].search([]).ids),('utility_type', '=','utensils')]) :
                self.env['hop.add.utensils'].create({
                        'item_id' : record.id,
                        'utensils_id': self.id,
                        'utensils_type':record.utensils_type,
                        }) 
                
            sql = "update hop_add_utensils set utensils_id=%d ;" % self.id
            self._cr.execute(sql)
            if self.utensils_line_ids:
                if self.utensils_line_ids.mapped('utensils_id').ids != []:
                    sql = "delete from hop_add_utensils where item_id in %s ;" % self.tuple_return(self.utensils_line_ids.mapped('utensils_id').ids)
                    self._cr.execute(sql)
            i.create_raw_utensils = True

    def tuple_return(self,cut_list):
        typle_list=''
        for i in cut_list:
            if typle_list == '':
                typle_list += '(' + str(i)
            else:
                typle_list += ',' + str(i)
        typle_list +=')'
        return typle_list
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

    @api.model
    def create(self, vals):
        if vals.get('time') == 0:
            raise UserError("Please Enter Time First!!!")
        if vals.get('no_of_pax') == 0:
            raise UserError("No. of Pax field is required!!!")
        res = super(UtensilsMaster, self).create(vals)
        return res
    
    @api.onchange('fuction_line_ids')
    def _onchange_fuction_line_ids(self):
        if self.fuction_line_ids:
            if self.no_of_pax == 0:
                raise UserError("Kindly Enter The No. Of Pax First!!!")
        
        # if self.no_of_pax:
        #     self.fuction_line_ids.no_of_pax = self.no_of_pax
    
    # @api.onchange('no_of_pax')
    # def _onchange_no_of_pax(self):
    #     if self.no_of_pax > 0:
    #         for rec in self.fuction_line_ids:
    #             rec.no_of_pax = self.no_of_pax
        

    def set_to_drafr(self):
        self.stage = 'draft'

    def action_confirm_utensils(self):
        line_list = []
        for i in self.utensils_line_ids:
            line_list.append((0,0, {
                    'fuction_id': self.function_id,
                    'utensils_id': i.utensils_id.id,
                    'uom': i.uom.id,
                    'utensils_type': i.utensils_type,
                    'qty': i.qty,
                    'uten_cost': i.uten_cost,
                }))
            print("/////////////line_list",line_list)
        
        if not line_list:
            raise UserError('You can not confirm the Utensils! Please Enter the utensisls first.')
        if line_list:
            self.function_id.utensils_line_ids = line_list
        self.stage = 'confirm'
     

    def action_outsource_po(self):
        line_list = []
        for i in self.fuction_line_ids.mapped('out_sider_id'):
            for record in self.fuction_line_ids.filtered(lambda l: l.out_sider_id.id == i.id):
                # for record in self.fuction_line_ids:
                line_list.append((0,0, {
                        'product_id': record.item_id.product_id.id,
                        'name':'',
                        'no_of_pax': record.no_of_pax,
                        'product_qty': 1,
                        'price_unit':1,
                        'product_uom':record.item_id.product_id.uom_id.id,
                }))
            purc_rec = self.env['purchase.order'].create({
                        'partner_id': i.id,
                        'fuction_id_rec': self.id,
                        'is_out_sider': record.is_outsource,
                        'venue_address': self.venue_address,
                        'order_line': line_list
                    })


   
class UtensilsMasterLine(models.Model):
    _name = "utensils.mst.line"

    fuction_id = fields.Many2one('utensils.mst',string="Function", ondelete='cascade', log_access=True)

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
    is_outsource = fields.Boolean(string="Is Service po",default=False)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
    
    # website = fields.Char('Website URL', compute='_compute_website_url')

    # def _compute_website_url(self):
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     for record in self:
    #         record.website = f'{base_url}/my-page/{record.id}'

    @api.onchange('insider_id','out_sider_id')
    def _onchange_no_of_pax(self):
        if self.insider_id:
            # for rec in self.fuction_id:name
            self.no_of_pax = self.fuction_id.no_of_pax
        else:
            self.no_of_pax = 0
        
        if self.out_sider_id:
            self.is_outsource = True

    @api.onchange('per_qty')
    def _onchange_per_qty(self):
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
        if self.item_id:
            if not self.item_id.uom:
                raise UserError('Select UoM First in %s'%self.item_id.name)            
            self.uom = self.item_id.uom.id
        
        
    
    def open_rm_list(self):
        rm_list = []
        for rec in self.item_id.raw_materials_ids:            
            req_wt = (rec.weight*self.qty)/rec.recipes_category_id.qty
            rm_list.append((0,0, {
                    'product_id': rec.item_id.id,
                    'uom': rec.uom.id,
                    'weight':req_wt
                }))
        return{
            'name': 'Raw Materials',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hop.recipe.rm',
            'context': {'default_recipe_id':self.item_id.id,'default_fun_date':self.fuction_id.date,
                        'default_venue_address':self.fuction_id.venue_address,'default_rec_rm_ids':rm_list},
            'target':'new',
        }


class UtensilsMstPage(models.Model):
    _name = 'utensils.mst.page'
    _description = 'function.utensils'

    fuction_id = fields.Many2one('utensils.mst',string="Function", ondelete='cascade', log_access=True)

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
            