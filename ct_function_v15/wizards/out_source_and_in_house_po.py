from odoo import api, models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning
class HopFunctionwizard(models.TransientModel):
    _name = "hop.fuction.out.source.and.in.house.wizard"

    delivery_date = fields.Date('Delivery Date')
    delivery_time = fields.Float('Delivery Time')
    delivery_am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM")
    function_date = fields.Date('function Date')
    vender_id = fields.Many2one('res.partner',string="Vendor")
    vender_ids = fields.Many2many('res.partner','ref_in_hose_out_source_vender_ids',string="Vendors")
    line_ids = fields.One2many('hop.fuction.out.source.and.in.house.line.wizard','mst_id', string="Function")

    @api.onchange('delivery_date')
    def _onchange_delivery_date(self):  
        if  self.delivery_date:
            if  self.delivery_date > self.function_date:
                raise UserError("Can't Select This Date!!!!")
            
    def action_apply_all(self):
        self.ensure_one()
        if self.env.context.get('type',False) == 'out':
            filter = lambda l: l.out_sider_id.id == self.vender_id.id
        else:
            filter = lambda l: l.insider_id.id == self.vender_id.id
        print(self.line_ids.filtered(filter),"-----------------------")

        for line in self.line_ids.filtered(filter):
            line.delivery_date = self.delivery_date
            line.delivery_time = self.delivery_time
            line.delivery_am_pm = self.delivery_am_pm
        return {
        'context': self.env.context,
        # 'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'hop.fuction.out.source.and.in.house.wizard',
        'res_id': self.id,
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target': 'new',
    }
    
    @api.model
    def default_get(self, fields):
        res = super(HopFunctionwizard, self).default_get(fields)
        
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        raw_rec = self.env[active_model].browse(active_id)
        line_list = []
        vender_list = []
        if self.env.context.get('type',False) == 'out':
            purchase = []
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('state','!=','cancel'),('po_type','=','out_source')])
            for order in purchase_record:
                for line in order.order_line:
                    if line.fuction_line_id:
                        purchase.append(line.fuction_line_id.id)           
            for i in raw_rec.fuction_line_ids.mapped('out_sider_id'):
                if i.id in raw_rec.fuction_line_ids.filtered(lambda l: l.out_sider_id.id == i.id and l.id not in purchase).mapped('out_sider_id').ids:
                    line_list.append((0,0, {
                                'name': i.name,
                                'display_type': 'line_section',
                            }))
                for record in raw_rec.fuction_line_ids.filtered(lambda l: l.out_sider_id.id == i.id and l.id not in purchase):
                    # for record in self.fuction_line_ids:
                    line_list.append((0,0, {
                            'display_type': False,
                            'name': i.name,
                            'category_id': record.category_id.id,
                            'item_id': record.item_id.id,
                            'no_of_pax': record.no_of_pax,
                            'per_qty': record.per_qty,
                            'qty': record.qty,
                            'uom': record.uom.id,
                            'out_sider_id': record.out_sider_id.id,
                            'cost': record.cost,
                            'rate': record.rate,
                            'instruction': record.instruction,
                            'type':'out'     
                            }))
            vender_list = raw_rec.fuction_line_ids.mapped('out_sider_id').ids
        elif self.env.context.get('type',False) == 'in':
            purchase = []
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('state','!=','cancel'),('po_type','=','in_house')])
            for order in purchase_record:
                for line in order.order_line:
                    if line.fuction_line_id:
                        purchase.append(line.fuction_line_id.id) 
            for i in raw_rec.fuction_line_ids.mapped('insider_id'):
                if i.id in raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id == i.id and l.id not in purchase).mapped('insider_id').ids:
                    line_list.append((0,0, {
                                'name': i.name,
                                'display_type': 'line_section',
                            }))
                for record in raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id == i.id and l.id not in purchase):
                    # for record in self.fuction_line_ids:
                    line_list.append((0,0, {
                            'display_type': False,
                            'name': i.name,
                            'category_id': record.category_id.id,
                            'item_id': record.item_id.id,
                            'no_of_pax': record.no_of_pax,
                            'per_qty': record.per_qty,
                            'qty': record.qty,
                            'uom': record.uom.id,
                            'insider_id': record.insider_id.id,
                            'cost': record.cost,
                            'rate': record.rate,
                            'instruction': record.instruction,   
                            'type':'in' 
                            }))
            vender_list = raw_rec.fuction_line_ids.mapped('insider_id').ids
        res['vender_ids'] = vender_list
        res['line_ids'] = line_list
        res['function_date'] = raw_rec.date
        res['delivery_date'] = raw_rec.date
        return res

    def action_confirm(self):
        # for line in self.line_ids:
        #     if line.out_sider_id or line.insider_id: 
        #         if not line.delivery_date or not line.delivery_time or not line.delivery_am_pm:
        #             raise UserError("Frist Select Delivery Date, Delivery Time and AM-PM.... ")
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        raw_rec = self.env[active_model].browse(active_id)
        if self.env.context.get('type',False) == 'out':
            purchase = []
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('state','!=','cancel'),('po_type','=','out_source')])
            for order in purchase_record:
                for line in order.order_line:
                    if line.fuction_line_id:
                        purchase.append(line.fuction_line_id.id)
            for i in raw_rec.fuction_line_ids.mapped('out_sider_id'):
                line_list = []
                if i.id in raw_rec.fuction_line_ids.filtered(lambda l: l.out_sider_id.id == i.id and l.id not in purchase).mapped('out_sider_id').ids:
                    for record in raw_rec.fuction_line_ids.filtered(lambda l: l.out_sider_id.id == i.id and l.id not in purchase):
                        price_unit = 1
                        inhouse_outsource_po_master_rate = self.env['ir.config_parameter'].sudo().get_param('inhouse_outsource_po_master_rate')
                        if inhouse_outsource_po_master_rate:
                            if i.cost:
                                price_unit = record.item_id.product_id.standard_price
                            else:
                                price_unit = 1
                        line_list.append((0,0, {
                                'product_id': record.item_id.product_id.id,
                                'name':'',
                                'helper':record.helper,
                                'chief':record.chief,
                                'no_of_pax': record.no_of_pax,
                                'order_qty': record.qty,
                                'product_qty': 1,
                                'price_unit':price_unit,
                                'product_uom':record.item_id.product_id.uom_id.id,
                                'fuction_line_id': record.id,
                                'category_id':record.category_id.id,
                                'instruction':record.instruction,
                        }))
                    rec = self.line_ids.filtered(lambda l: l.out_sider_id.id == i.id)
                    delivery_date = False
                    delivery_am_pm = False
                    delivery_time = False
                    for x in rec:
                        delivery_date = x.delivery_date
                        delivery_time = x.delivery_time
                        delivery_am_pm = x.delivery_am_pm
                        break
                    self.env['purchase.order'].create({
                                'partner_id': i.id,
                                'fuction_id_rec': raw_rec.id,
                                'is_out_sider': True,
                                'venue_address': raw_rec.venue_address,
                                'order_line': line_list,
                                'po_type':'out_source',
                                'remarks': raw_rec.remarks,
                                'date': raw_rec.date,
                                'time': raw_rec.time,
                                'am_pm': raw_rec.am_pm,
                                'meal_type': raw_rec.meal_type,
                                'manager_name_id': raw_rec.manager_name_id.id,
                                'delivery_date':delivery_date,
                                'delivery_time':delivery_time,
                                'delivery_am_pm':delivery_am_pm,
                            })
        elif self.env.context.get('type',False) == 'in':
            purchase = []
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('state','!=','cancel'),('po_type','=','in_house')])
            print(purchase_record)
            for order in purchase_record:
                for line in order.order_line:
                    if line.fuction_line_id:
                        purchase.append(line.fuction_line_id.id)
            for i in raw_rec.fuction_line_ids.mapped('insider_id'):
                line_list = []
                if i.id in raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id == i.id and l.id not in purchase).mapped('insider_id').ids:
                    for record in raw_rec.fuction_line_ids.filtered(lambda l: l.insider_id.id == i.id and l.id not in purchase):
                        line_list.append((0,0, {
                                'product_id': record.item_id.product_id.id,
                                'name':'',
                                'helper':record.helper,
                                'chief':record.chief,
                                'no_of_pax': record.no_of_pax,
                                'order_qty': record.qty,
                                'product_qty': 1,
                                'price_unit':1,
                                'category_id':record.category_id.id,
                                'instruction':record.instruction,
                                'product_uom':record.item_id.product_id.uom_id.id,
                                'no_of_pax':record.no_of_pax,
                                'fuction_line_id': record.id,
                                'instruction':record.instruction,
                        }))
                    rec = self.line_ids.filtered(lambda l: l.insider_id.id == i.id)
                    delivery_date = False
                    delivery_am_pm = False
                    delivery_time = False
                    for x in rec:
                        delivery_date = x.delivery_date
                        delivery_time = x.delivery_time
                        delivery_am_pm = x.delivery_am_pm
                        break
                    purc_rec = self.env['purchase.order'].create({
                                'partner_id': i.id,
                                'fuction_id_rec': raw_rec.id,
                                'is_out_sider': True,
                                'venue_address': raw_rec.venue_address,
                                'order_line': line_list,
                                'po_type':'in_house',
                                'remarks': raw_rec.remarks,
                                'date': raw_rec.date,
                                'time': raw_rec.time,
                                'am_pm': raw_rec.am_pm,
                                'meal_type': raw_rec.meal_type,
                                'manager_name_id': raw_rec.manager_name_id.id,
                                'delivery_date':delivery_date,
                                'delivery_time':delivery_time,
                                'delivery_am_pm':delivery_am_pm,
                            })


class HopFunctionLine(models.TransientModel):
    _name = "hop.fuction.out.source.and.in.house.line.wizard"

    mst_id = fields.Many2one('hop.fuction.out.source.and.in.house.wizard',string="Function", ondelete='cascade')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name=fields.Text('Vender')
    category_id = fields.Many2one('hop.recipes.category',string="Category")
    item_id = fields.Many2one('hop.recipes',string="Item Name")
    no_of_pax = fields.Integer(string="No Of Pax")
    per_qty = fields.Float(string="Per Head Qty")
    qty = fields.Float(string="Qty")
    uom = fields.Many2one('uom.uom',string="Uom")
    out_sider_id = fields.Many2one('res.partner',string="Out-Source",domain=[('is_vender','=',True)])
    insider_id = fields.Many2one('res.partner',string="In-House",domain=[('is_vender','=',True)] )
    cost = fields.Float(string="Cost")
    rate = fields.Float(string="Rate")
    instruction = fields.Char(string="Instruction")
    type = fields.Selection([('in','IN'),('out','Out')],string="Type")
    delivery_date = fields.Date('Delivery Date')
    delivery_time = fields.Float('Delivery Time')
    delivery_am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM")