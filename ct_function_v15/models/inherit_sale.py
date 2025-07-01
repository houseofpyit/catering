from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged
import json

class InheritSaleOrder(models.Model):
    _inherit = "sale.order"

    date = fields.Date(string="Date",default=fields.Date.context_today,tracking=True,readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    remarks = fields.Text(string="Remarks",tracking=True,readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    lead_id = fields.Many2one('hop.lead',string="Lead",readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    note = fields.Text('Terms and conditions',readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    send_email = fields.Boolean(string="Send Email",default=False,readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}) 
    confirm_date = fields.Date(string="Confirm Date")
    fun_date = fields.Date(string="Function Date",tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type",tracking=True,readonly=True,states={'draft': [('readonly', False)]})
    venue_address = fields.Text('Venue Address')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3)
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")
    @api.model
    def create(self,vals):
        record = self.env['sale.order'].search([('lead_id','=',vals.get('lead_id'))],order="id asc")
        if record:
            vals.update({'name':record[0].name + ' - '+str(len(record))})
        return super(InheritSaleOrder,self).create(vals)
    
    def action_confirm(self):
            rec = super(InheritSaleOrder,self).action_confirm()
            
            for i in self.order_line:
                # if not i.product_uom_qty:
                #     raise UserError(('Please Enter Quantity !!!'))
            
                picking_id = self.env['stock.move'].search([('sale_line_id','=',i.id)])
                for line in picking_id:
                     line.product_id = i.product_id

            for picking in self.picking_ids:
                receipt = picking
                wiz = receipt.button_validate()
                if receipt._check_immediate():
                    wiz = Form(self.env['stock.immediate.transfer'].with_context(wiz['context'])).save().process()
                if receipt._check_backorder():
                    wiz = Form(self.env['stock.backorder.confirmation'].with_context(wiz['context'])).save().process_cancel_backorder()

            return rec 
    
    def get_gst(self,line):
        print(self)
        tax_list = ""
        for gst in line.tax_id:
            tax_list += gst.name  + " , "
        return tax_list
    
    def get_gst_amount(self):
        gst={}
        sgst=0
        igst=0
        cgst=0
        for fun in self:
            to_compare = json.loads(fun.tax_totals_json)
            for groups in to_compare['groups_by_subtotal'].values():
                for line in groups:
                    if line.get('tax_group_name') == 'SGST':
                        sgst =+ line.get('tax_group_amount')
                    if line.get('tax_group_name') == 'CGST':
                        cgst =+ line.get('tax_group_amount')
                    if line.get('tax_group_name') == 'IGST':
                        igst =+ line.get('tax_group_amount')
        if sgst >0:
            gst.update({'sgst':sgst})
        if cgst >0:
            gst.update({'cgst':cgst})
        if igst >0:
            gst.update({'igst':igst})
        return gst
    
    

    @api.model
    def action_cancel(self):
        for line in self:
            account_move = self.env['account.move.line'].search([('sale_id','=',line.id)])
            if account_move.move_id.state == 'posted':
                raise UserError("Invoice already generated...")
        for line in self:
            function_rec = self.env['hop.function'].search([('hop_lead_id','=',line.lead_id.id),('stage','!=','cancel')])
            if function_rec:
                raise ValidationError("You Can not cancel the confirmed Menu Order!!! ")

        return super(InheritSaleOrder,self).action_cancel()
    
    def print(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ct_function_v15.action_print")
        action['context'] = {'active_id': self.env.context['active_ids'],
                             'active_model': self.env.context['active_model']}
        return action
    
class InheritSaleOrderLine(models.Model):
    _inherit = "sale.order.line" 

    is_manu_planner = fields.Boolean(string="Create From Menu Planner",default=False) 
    name = fields.Text(string='Instruction', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False}, check_company=True)