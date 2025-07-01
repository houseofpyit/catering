from odoo import api, models, fields, _
from odoo.tests import Form, tagged
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date


class InheritPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    venue_address = fields.Text('Venue Address')
    fuction_id_rec = fields.Many2one('hop.function',string="Function",readonly=True,states={'draft': [('readonly', False)]}) 
    is_out_sider = fields.Boolean(string="Is Outsider",readonly=True,states={'draft': [('readonly', False)]}) 
    po_type = fields.Selection([('row_material','Raw Material PO'),('out_source','Out-Source PO'),
                                ('in_house','In-House PO'),('service','Service PO'),('addons','Add-ons PO'),('normal','Normal')],default='normal',string="PO Type",readonly=True,states={'draft': [('readonly', False)]})
    create_bill = fields.Boolean(string="invoice create",compute='_compute_create_bill',readonly=True,states={'draft': [('readonly', False)]})
    remarks = fields.Text(string="Remarks",tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    manager_name_id = fields.Many2one('res.partner',string="Manager Name",domain=[('is_vender','=',True)] ,tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type",tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    time = fields.Float(string="Time",tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    date = fields.Date(string="Function Date",default=fields.Date.context_today,tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    notes = fields.Text('Terms and Conditions',readonly=True,states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, tracking=True)
    send_email = fields.Boolean(string="Send Email",default=False,readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}) 
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")
    delivery_date = fields.Date('Delivery Date')
    delivery_time = fields.Float('Delivery Time')
    delivery_am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM")
    total_qty = fields.Float(string='Total Qty')
    category_id = fields.Many2many('product.category')

    def selection_meal_type(self):
        ret =''
        if self.meal_type:
            ret =  dict(self._fields['meal_type'].selection).get(self.meal_type)
        return ret
    
    def print(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ct_function_v15.action_print")
        action['context'] = {'active_id': self.env.context['active_id'],
                             'active_model': self.env.context['active_model']}
        return action
    
    def action_print(self):
        print("------------------ call for print -------------")
        action = self.env["ir.actions.actions"]._for_xml_id("ct_function_v15.action_po_print_report_wizard")
        action['context'] = {'active_id': self.ids,
                             'active_model': self.env.context['active_model'],
                             'default_po_ids':self.ids}
        print("---------------------action",action)
        return action
    
    @api.depends('create_bill')
    def _compute_create_bill(self):
        for i in self:
            i.total_qty = sum(i.order_line.mapped('product_qty'))
            record = self.env['account.move.line'].search([('purchase_id','=',i.id)])
            if record:
                i.create_bill = True
            else:
                i.create_bill = False 

    def button_confirm(self):
        rec = super(InheritPurchaseOrder,self).button_confirm()
        
        for i in self.order_line:
            if not i.product_qty:
                raise UserError(('Please Enter Quantity !!!'))
            if i.product_id:
                po_rec  = self.env['purchase.order.line'].search([('product_id','=',i.product_id.id)])

                pu = sum(po_rec.mapped('price_unit'))
                new_pu = pu/ len(po_rec)

                i.product_id.standard_price = new_pu
            
            picking_id = self.env['stock.move'].search([('purchase_line_id','=',i.id)])
            for line in picking_id:
                line.product_id = i.product_id

        # for picking in self.picking_ids:
        #     receipt = picking
        #     wiz = receipt.button_validate()
        #     wiz = Form(self.env['stock.immediate.transfer'].with_context(wiz['context'])).save().process()

        return rec 
    
    def get_print_report_name(self):
        for order in self:
            if order.meal_type:
                meal_type = dict(order._fields['meal_type'].selection).get(order.meal_type)
                return f"{order.venue_address[:10]} - {order.date} - {order.partner_id.name} - {meal_type}"
            elif order.venue_address:
                return f"{order.venue_address[:10]} - {order.date} - {order.partner_id.name}"
            else:
                return f"{order.date} - {order.partner_id.name}"

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            if '-' in self.name:
                lst_str =self.name.split('-')[1]
                fst_str =self.name.split('-')[0]
                default['name'] = fst_str + '-' + str(int(lst_str)+1)

            else:
                default['name'] = self.name + '-' + str(1)
        
        return super(InheritPurchaseOrder, self).copy(default=default)
    
    @api.model
    def action_all_order_cancel(self):
        if not self.env.context.get('edit_purchase',False):
            if self.fuction_id_rec.stage == 'invoice':
                raise UserError("You cannot cancel PO..")
        for order in self:
            account_move = self.env['account.move.line'].search([('purchase_id','=',order.id)])
            if account_move.move_id.state == 'posted':
                if account_move.move_id.state != 'cancel':
                    raise UserError("Invoice already generated...")
        for order in self:
            for line in order.order_line:
                if not self.env.context.get('no_of_pax_chnage',False):
                    if line.fuction_line_id:
                        if line.fuction_line_id.insider_id:
                            line.fuction_line_id.insider_id = False
                        elif line.fuction_line_id.out_sider_id:
                            line.fuction_line_id.out_sider_id = False
                    elif line.labour_line_id:
                        line.labour_line_id.vender_id = False
                    elif line.service_line_id:
                        line.service_line_id.vender_id = False
            
            if order.state != "cancel":
                # line.button_cancel()
                order.state = 'cancel'
            order.unlink()
      
    def action_all_order_confirm(self):
        for line in self:
            if line.state != "confirm":
                line.button_confirm()
    
    def write(self, vals):
        res =  super(InheritPurchaseOrder,self).write(vals)
        for line in self.order_line:
            if line.fuction_line_id:
                if line.fuction_line_id.insider_id:
                    line.fuction_line_id.insider_id = line.order_id.partner_id.id
                elif line.fuction_line_id.out_sider_id:
                    line.fuction_line_id.out_sider_id = line.order_id.partner_id.id
            elif line.labour_line_id:
                line.labour_line_id.vender_id = line.order_id.partner_id.id
            elif line.service_line_id:
                line.service_line_id.vender_id = line.order_id.partner_id.id
        return res
    
    # @api.depends('total_qty')
    # def _cumpute_total_qty(self):
    #     for i in self:
    #         i.total_qty = sum(i.order_line.mapped('product_qty'))
     
class InheritPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[(1, '=', 1)]")
    name = fields.Text(string='Remark',readonly=True,states={'draft': [('readonly', False)]})
    no_of_pax = fields.Integer(string="No Of Pax",readonly=True,states={'draft': [('readonly', False)]})
    order_qty = fields.Integer(string="Total Qty",readonly=True,states={'draft': [('readonly', False)]})
    qty_cal_type = fields.Selection([('no_of_pax','No Of Pax'),('total_qty','Total Qty'),('helper','Helper')],string="Type",tracking=True)
    helper = fields.Integer(string="Helper",readonly=True,states={'draft': [('readonly', False)]})
    chief = fields.Integer(string="Chief",readonly=True,states={'draft': [('readonly', False)]})

    # for Service
    hospitality_ids = fields.Many2one('ct.hospitality.shift',string="Hospitality Shift",tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    shift_date = fields.Date(string="Shift Date",readonly=True,states={'draft': [('readonly', False)]})
    shift_time = fields.Float(string="Shift Time",readonly=True,states={'draft': [('readonly', False)]})
    remarks = fields.Char(string="Shift Remarks",readonly=True,states={'draft': [('readonly', False)]})
    location = fields.Selection([
        ('add_venue', "At Venue"),
        ('add_godown', "At Godown")], default=False, string="Location",readonly=True,states={'draft': [('readonly', False)]})
    
    # for addons
    date = fields.Date(string="Date",readonly=True,states={'draft': [('readonly', False)]})
    time = fields.Float(string="Time",readonly=True,states={'draft': [('readonly', False)]})
    am_pm = fields.Selection([('am','AM'),('pm','PM')],readonly=True,string="AM-PM",tracking=True,states={'draft': [('readonly', False)]})
    category_id = fields.Many2one('hop.recipes.category',string="Category",track_visibility='onchange',readonly=True,states={'draft': [('readonly', False)]})
    instruction = fields.Char(string="Instruction",track_visibility='onchange',readonly=True,states={'draft': [('readonly', False)]})
    fuction_line_id = fields.Many2one('hop.fuction.line',string="Function Line")
    labour_line_id = fields.Many2one('hospitality.shift.line',string="Labour Line")
    service_line_id = fields.Many2one('hop.extra.service.line',string="Add-ons Line")
    materal_line_id = fields.Many2one('hop.raw.materal',string="Materal Line")


    def selection_name(self):
        ret =''
        if self.location:
            ret =  dict(self._fields['location'].selection).get(self.location)
        return ret

    def unlink(self):
        for record in self:
            if record.order_id.state != 'cancel':
                if record.fuction_line_id:
                    if record.fuction_line_id.insider_id:
                        record.fuction_line_id.insider_id = False
                    elif record.fuction_line_id.out_sider_id:
                        record.fuction_line_id.out_sider_id = False
                elif record.labour_line_id:
                    record.labour_line_id.vender_id = False
                elif record.service_line_id:
                    record.service_line_id.vender_id = False
        return super().unlink()
    
    @api.onchange('qty_cal_type','no_of_pax','order_qty','price_unit','helper')
    def _onchange_qty_cal_type(self):
        if self.order_id.po_type in ('in_house','out_source'):
            if self.qty_cal_type == 'no_of_pax':
                self.product_qty = self.no_of_pax
            elif self.qty_cal_type == 'helper':
                self.product_qty = self.helper
            else:
                self.product_qty = self.order_qty
            inhouse_outsource_po_master_rate = self.env['ir.config_parameter'].sudo().get_param('inhouse_outsource_po_master_rate')
            if inhouse_outsource_po_master_rate:
                if self.price_unit == 0:
                    if self.order_id.partner_id.cost:
                        self.price_unit = self.order_id.partner_id.cost
                    else:
                        self.price_unit = 1
            if not self.qty_cal_type and self.product_id:
                raise UserError("First select Type... ")

    @api.model
    def create(self, vals):
        if not vals.get('product_qty') and vals.get('product_id'):
            raise UserError(_('Please Enter Quantity !!!'))
        
        new_line = super(InheritPurchaseOrderLine, self).create(vals)
        self.update_product_standard_price(new_line.product_id)
        return new_line
    
    def write(self, vals):
        if 'product_qty' in vals and not vals['product_qty']:
            raise UserError(_('Please Enter Quantity !!!'))
        
        updated_lines = super(InheritPurchaseOrderLine, self).write(vals)
        for line in self:
            self.update_product_standard_price(line.product_id)
        return updated_lines
    
    def update_product_standard_price(self, product):
        if self.product_id.product_tmpl_id.utility_type == 'row_material':
            po_lines = self.search([('product_id', '=', product.id)])
            total_subtotal = sum(po_lines.mapped('price_subtotal'))
            total_qty = sum(po_lines.mapped('product_qty'))
            
            new_standard_price = total_subtotal / total_qty if total_qty != 0 else 0
            product.standard_price = new_standard_price