from odoo import api, models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning

class ctPurchaseWizard(models.TransientModel):
    _name='ct.purchase.wiz'


    ct_category_id = fields.Many2one('product.category',string="Category")
    category_ids = fields.Many2many('product.category','ct_purchase_wiz_category_ids')
    add_category_ids = fields.Many2many('product.category','ct_purchase_wiz_add_category_ids')
    vender_id = fields.Many2one('res.partner',string="Vendor",domain=[('is_vender','=',True)])
    line_ids = fields.One2many('ct.purchase.wiz.line','mst_id', string="Raw Materials")
    function_date = fields.Date('function Date')
    delivery_date = fields.Date('Delivery Date')
    delivery_time = fields.Float('Delivery Time')
    delivery_am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM")

    @api.onchange('delivery_date')
    def _onchange_delivery_date(self):  
        if  self.delivery_date:
            if  self.delivery_date > self.function_date:
                raise UserError("Can't Select This Date!!!!")
            
    @api.model
    def default_get(self, fields):
        res = super(ctPurchaseWizard, self).default_get(fields)
        
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        raw_rec = self.env[active_model].browse(active_id)
        line_list = []
        rm_list = []
        cate_list = [] 
        recipe_list = []
        # if raw_rec:
        #     for i in raw_rec.material_line_ids:
        #         rm_ids = self.env['hop.raw.materal'].search([('fuction_id','=',raw_rec.id),('recipe_id','=',i.recipe_id.id)])
        #         if i.display_type == False:
        #             if i.recipe_id:
        #                 if i.recipe_id.id not in recipe_list:
        #                     rm_list.append({
        #                         'recipe_id':i.recipe_id.id,
        #                         'category_id': i.recipe_id.categ_id.id,
        #                         'no_of_time':([format(float(num), ".2f") for num in rm_ids.mapped('weight')]),
        #                         'weight': sum(rm_ids.mapped('weight')),
        #                         'req_weight':sum(rm_ids.mapped('weight')),
        #                         'uom':i.recipe_id.uom_id.id,
        #                         'product_name':i.recipe_id.name,
        #                         'cost_price': i.cost_price,
        #                     })
                            
        #                     recipe_list.append(i.recipe_id.id)
        #                 cate_list.append(i.recipe_id.categ_id.id)

        #     # record = self.env['hop.recipe.rm'].search([('function_id','in',raw_rec.ids)])
        #     # rec_rm = self.env['hop.rec_rm.line'].search([('recipe_rm_id','in',record.ids)])
        #     # for cat in rec_rm.mapped('product_id.categ_id'):
        #     #     product_record = rec_rm.filtered(lambda l: l.product_id.categ_id.id == cat.id)
        #     #     for i in product_record:
        #     #         if i.product_id.id not in recipe_list:
        #     #             print("............",i.product_id.name)
        #     #             rm_list.append({
        #     #                 'recipe_id':i.product_id.id,
        #     #                 'category_id': i.product_id.categ_id.id,
        #     #                 'no_of_time':([format(float(num), ".2f") for num in product_record.filtered(lambda l: l.product_id.id == i.product_id.id).mapped('weight')]),
        #     #                 'weight': sum(product_record.filtered(lambda l: l.product_id.id == i.product_id.id).mapped('weight')),
        #     #                 'req_weight':sum(product_record.filtered(lambda l: l.product_id.id == i.product_id.id).mapped('weight')),
        #     #                 'uom':i.uom.id,
        #     #                 'product_name':i.product_id.name,
        #     #                 'cost_price': i.product_id.standard_price,
        #     #             })
                        
        #     #             recipe_list.append(i.product_id.id)
        #     #     cate_list.append(i.product_id.categ_id.id)
        
        
        # for cate_id in list(set(cate_list)):
        #     category_id = self.env['product.category'].search([('id','=',cate_id)])
        #     line_list.append((0,0, {
        #                 'name': category_id.name,
        #                 'display_type': 'line_section',
        #             }))
        #     for rm in rm_list:
        #         if cate_id == rm.get('category_id'):
        #             line_list.append((0,0, {
        #                 'recipe_id': rm.get('recipe_id'),
        #                 'display_type': False,
        #                 'category_id': rm.get('category_id'),
        #                 'no_of_time': '+'.join(rm.get('no_of_time')),
        #                 'name': rm.get('product_name'),
        #                 'uom': rm.get('uom'),
        #                 'weight': rm.get('weight'),
        #                 'req_weight': rm.get('req_weight'),
        #                 'cost_price': rm.get('cost_price'),
        #                 # 'item_cost': rm.get('item_cost'),
        #                 # 'sequence': i.sequence,
        #                 # 'vender_id': i.vender_id.id,
        #                 }))
        # print("==================",list(set(cate_list)))
        # res['line_ids'] = line_list
        # res['category_ids'] = [(6,0, list(set(cate_list)))]
        # res['function_date'] = raw_rec.date
        # res['delivery_date'] = raw_rec.date
                
        # for cat_id in raw_rec.material_line_ids.mapped('recipe_id.categ_id'):
        #     line_list.append((0, 0, {
        #         'name': cat_id.name,
        #         'display_type': 'line_section',
        #     }))
        #     filtered_lines = raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.categ_id.id == cat_id.id and l.display_type == False)
        #     for i in filtered_lines:
        #         if i.recipe_id.id not in recipe_list:
        #             weights = filtered_lines.filtered(lambda l: l.recipe_id.id == i.recipe_id.id).mapped('weight')
        #             line_list.append((0, 0, {
        #                 'recipe_id': i.recipe_id.id,
        #                 'display_type': False,
        #                 'category_id': i.recipe_id.categ_id.id,
        #                 'no_of_time': '+'.join([format(float(num), ".3f") for num in weights]),
        #                 'weight': sum(weights),
        #                 'req_weight': sum(weights),
        #                 'uom': i.recipe_id.uom_id.id,
        #                 'name': i.recipe_id.name,
        #                 'cost_price': i.cost_price,
        #                 'vender_id':i.recipe_id.vender_id.id
        #             }))
        #             recipe_list.append(i.recipe_id.id)

        # res['line_ids'] = line_list

        purchase_cat_list = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('po_type','=','row_material'),('state','!=','cancel')]).mapped('category_id').ids
        cat_list =[]
        for line in raw_rec.material_line_ids.mapped('recipe_id.categ_id').ids:
            if line not in  purchase_cat_list:
                cat_list.append(line)
        res['category_ids'] = [(6, 0, cat_list)]
        res['function_date'] = raw_rec.date
        res['delivery_date'] = raw_rec.date
        return res
    

    @api.onchange('ct_category_id')
    def _onchange_ct_category_id(self):
        if self.ct_category_id:
            line_list = []
            recipe_list = []
            active_model = self.env.context.get('active_model')
            active_id = self.env.context.get('active_id')
            raw_rec = self.env[active_model].browse(active_id)
            for cat_id in self.ct_category_id:
                line_list.append((0, 0, {
                    'name': cat_id.name,
                    'display_type': 'line_section',
                }))
                filtered_lines = raw_rec.material_line_ids.filtered(lambda l: l.recipe_id.categ_id.id == cat_id.id and l.display_type == False)
                for i in filtered_lines:
                    if i.recipe_id.id not in recipe_list:
                        weights = filtered_lines.filtered(lambda l: l.recipe_id.id == i.recipe_id.id).mapped('weight')
                        line_list.append((0, 0, {
                            'materal_line_id':i.id,
                            'recipe_id': i.recipe_id.id,
                            'display_type': False,
                            'category_id': i.recipe_id.categ_id.id,
                            'no_of_time': '+'.join([format(float(num), ".3f") for num in weights]),
                            'weight': sum(weights),
                            'req_weight': sum(weights),
                            'uom': i.recipe_id.uom_id.id,
                            'name': i.recipe_id.name,
                            'cost_price': i.cost_price,
                            'vender_id':i.recipe_id.vender_id.id
                        }))
                        recipe_list.append(i.recipe_id.id)
            self.line_ids =  False
            self.line_ids = line_list

    def action_apply_all(self):
        self.ensure_one()
        category_id = self.env['ct.purchase.wiz.line'].search([('category_id','=',self.ct_category_id.id)])
        for i in category_id:
            if self.vender_id:
                i.vender_id = self.vender_id
            i.delivery_date = self.delivery_date
            i.delivery_time = self.delivery_time
            i.delivery_am_pm  = self.delivery_am_pm
            # if not self.vender_id:
            #     raise UserError("Please Enter Vender First !!!")
        cate_list = []
        for line in self.line_ids:
            if line.vender_id:
                if line.category_id:
                    cate_list.append(line.category_id.id)
        print(cate_list)
        self.add_category_ids = [(6,0, cate_list)]
        self.ct_category_id =  False
        return {
        'context': self.env.context,
        # 'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'ct.purchase.wiz',
        'res_id': self.id,
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target': 'new',
    }

    def action_confirm(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        raw_rec = self.env[active_model].browse(active_id)
        for i in self.line_ids:
            if not i.vender_id:
                if i.recipe_id:
                    raise UserError("Kindly Enter The Vender First!!!")
                
        
        for i in self.line_ids.mapped('vender_id'):
            line_list = []

            for line in self.line_ids.filtered(lambda l: l.vender_id.id == i.id):

                # qty = 0
                # if line.req_weight > 0:
                #     qty = line.req_weight
                # else:
                #     qty = line.weight
                line_list.append((0,0, {
                    'materal_line_id':line.materal_line_id.id,
                    'product_id': line.recipe_id.id,
                    'name': '',
                    # 'product_qty': line.weight,
                    'product_qty': line.req_weight,
                    'product_uom': line.uom.id,
                    'price_unit': line.cost_price,
                    'date': line.delivery_date,
                    'time': line.delivery_time,
                    'am_pm': line.delivery_am_pm,
                }))
                
        
            if line_list:
                for record in raw_rec:
                    rec = self.line_ids.filtered(lambda l: l.vender_id.id == i.id)
                    delivery_date = False
                    delivery_am_pm = False
                    delivery_time = False
                    for x in rec:
                        delivery_date = x.delivery_date
                        delivery_time = x.delivery_time
                        delivery_am_pm = x.delivery_am_pm
                        break
                    purchase =  self.env['purchase.order'].search([('fuction_id_rec','=',record.id),('partner_id','=',i.id),('state','!=','cancel'),('po_type','=','row_material')])
                    if purchase:
                        purchase.order_line = line_list
                        list_catg = []
                        for cat in purchase.category_id:
                            list_catg.append(cat.id)
                        list_catg.append(self.line_ids.mapped('category_id').id)
                        purchase.category_id = False
                        purchase.category_id =[(6,0,list_catg)] 
                    else:
                        self.env['purchase.order'].create({
                                'category_id':[(6,0,self.line_ids.mapped('category_id').ids)] ,
                                'partner_id': i.id,
                                'fuction_id_rec': record.id,
                                'venue_address': record.venue_address,
                                'order_line': line_list,
                                'po_type':'row_material',
                                'remarks': record.remarks,
                                'venue_address': record.venue_address,
                                'date': record.date,
                                'time': record.time,
                                'am_pm': record.am_pm,
                                'meal_type': record.meal_type,
                                'manager_name_id': record.manager_name_id.id,
                                'delivery_date':delivery_date,
                                'delivery_time':delivery_time,
                                'delivery_am_pm':delivery_am_pm,
                            })
                record.is_purchase = True

        # less In Stock
        src_location = self.env['stock.warehouse'].search([('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
        dest_wh_location = self.env['stock.location'].search( [('usage', '=', 'customer') , ('company_id', 'in', [self.env.user.company_id.id, False] )], limit=1)
        
        line_list = []
        for line in self.line_ids:
            if line.recipe_id:
                line_list.append((0,0, {'product_id': line.recipe_id.id, 
                                    'location_id': src_location.lot_stock_id.id,
                                    'location_dest_id': dest_wh_location.id,
                                    'product_uom_qty': line.req_weight if line.req_weight > 0 else line.weight, 
                                    'quantity_done': line.req_weight if line.req_weight > 0 else line.weight,
                                    'product_uom': line.uom.id,
                                    'name': line.recipe_id.name,'origin': "Function " + str(raw_rec.party_name_id.name),
                                    'date': fields.datetime.now(), }))

        print("...........line_list.................",line_list)

        warehouse_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing'),('warehouse_id.company_id','=',self.env.user.company_id.id)])

        print("..............warehouse_id.............",warehouse_id)

        if line_list:

            picking_id = self.env['stock.picking'].create({
                # 'partner_id': self.agent_id.id,
                'location_id': src_location.lot_stock_id.id,
                'location_dest_id':  dest_wh_location.id,
                'origin': "Function " + str(raw_rec.party_name_id.name),
                'picking_type_id': warehouse_id.id,
                'move_ids_without_package': line_list,
                'date': fields.datetime.now(),
            })


            if picking_id:
                picking_id.action_confirm()
                picking_id.action_assign()
                self.env.context = dict(self.env.context)
                self.env.context.update({'skip_backorder': True})
                picking_id.button_validate()
                self.env['stock.immediate.transfer'].create({'pick_ids': [(4, picking_id.id)]}).process()

            

class ctPurchaseWizardLine(models.TransientModel):
    _name='ct.purchase.wiz.line'

    mst_id = fields.Many2one('ct.purchase.wiz')
    
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
    # item_cost = fields.Float(string="Item Cost",track_visibility='onchange', compute="_compute_req_weight")
    sequence = fields.Integer(string='Sequence')
    vender_id = fields.Many2one('res.partner',string="Vendor",track_visibility='onchange',domain=[('is_vender','=',True)])
    category_id = fields.Many2one('product.category')
    no_of_time = fields.Char(string="No of Time Use")
    delivery_date = fields.Date('Delivery Date')
    delivery_time = fields.Float('Delivery Time')
    delivery_am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM")
    materal_line_id = fields.Many2one('hop.raw.materal',string="Materal Line")


    @api.onchange('recipe_id')
    def _onchange_recipe_id(self):
        if self.recipe_id.description:
            self.name = self.recipe_id.description
        else:
            self.name = self.recipe_id.name
    
    # @api.depends('req_weight','cost_price','req_weight')
    # def _compute_req_weight(self):
    #     for rec in self:
    #         if rec.req_weight > 0:
    #             rec.item_cost = rec.req_weight*rec.cost_price
    #         else:
    #             rec.item_cost = rec.weight*rec.cost_price