from odoo import api, models, fields,_
from datetime import date, datetime
from odoo.exceptions import UserError,ValidationError

class InventoryAdjustment(models.Model):
    _name = 'hop.inventory.adj'
    _inherit = ['mail.thread']
    _description = "Inventory Adjustment"

    name = fields.Char(string="Number", copy=False, default='New',tracking=True)
    company_id = fields.Many2one('res.company',string="Company" , default=lambda self: self.env.company,tracking=True)
    date = fields.Date(string="Date",default=fields.Date.context_today,tracking=True)
    state = fields.Selection([('draft','Draft'),('done','Done')],string="State",default="draft",tracking=True) 
    remarks = fields.Text(string='Remarks',tracking=True)
    stock_type = fields.Selection([('add','Add in Stock'),('replace','Replace')],string="Stock")
    line_ids = fields.One2many('hop.inventory.adj.line','adj_id',string="Line",tracking=True)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hop.inv.adj') or _('New')
        return super(InventoryAdjustment, self).create(vals)
    
    def write(self, vals):
        print("-----------",vals)

        if vals.get('line_ids'):
            data_text = ""
            for i in vals.get('line_ids'):
                if i[2]:
                    data_text += str(i[2]) + ","
            message = _("Inventory Adjustment Line %s ",data_text if data_text else "Delete")
            self.message_post(body=message,message_type='comment')
        return super().write(vals)

    def action_done(self):
        # Frist Less From Stock
        if self.stock_type == 'replace':
            src_location = self.env['stock.warehouse'].search([('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
            dest_wh_location = self.env['stock.location'].search( [('usage', '=', 'customer') , ('company_id', 'in', [self.env.user.company_id.id, False] )], limit=1)
            if dest_wh_location:
                line_list = []
                for i in self.line_ids:
                    if i.qty:
                        
                        line_list.append((0,0, {'product_id': i.product_id.id,
                                            'location_id': src_location.lot_stock_id.id,
                                            'location_dest_id': dest_wh_location.id,
                                            'product_uom_qty': i.qty, 
                                            'quantity_done': i.qty,
                                            'product_uom': i.product_id.uom_id.id,
                                            'name': i.product_id.name,'origin': "Less INV ADJ"+ str(self.name) ,
                                            'date': fields.datetime.now(), }))
                print("---------------------line_list less ")

                warehouse_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing'),('warehouse_id.company_id','=',self.env.user.company_id.id)])
                picking_id = ""
                if line_list:
        
                    picking_id = self.env['stock.picking'].create({
                        # 'partner_id': self.agent_id.id,
                        'location_id': src_location.lot_stock_id.id,
                        'location_dest_id': dest_wh_location.id,
                        'origin': "Less INV ADJ"+ str(self.name),
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

        # Add New Stock
        src_location = self.env['stock.warehouse'].search([('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
        dest_wh_location = self.env['stock.location'].search( [('usage', '=', 'supplier') , ('company_id', 'in', [self.env.user.company_id.id, False] )], limit=1)

        if dest_wh_location:
            line_list = []

            for i in self.line_ids:
                if i.new_qty:
                    line_list.append((0,0, {'product_id': i.product_id.id, 
                                        'location_id': dest_wh_location.id,
                                        'location_dest_id': src_location.lot_stock_id.id,
                                        'product_uom_qty': i.new_qty, 
                                        'quantity_done':  i.new_qty,
                                        'product_uom': i.product_id.uom_id.id,
                                        'name': i.product_id.name,'origin': "Add INV ADJ"+ str(self.name) ,
                                        'date': fields.datetime.now(), }))
            print("---------------------line_list add ")

            warehouse_id = self.env['stock.picking.type'].search([('code', '=', 'incoming'),('warehouse_id.company_id','=',self.env.user.company_id.id)])

            if line_list:
            
                picking_id = self.env['stock.picking'].create({
                    # 'partner_id': self.agent_id.id,
                    'location_id': dest_wh_location.id,
                    'location_dest_id': src_location.lot_stock_id.id,
                    'origin':  "Add INV ADJ"+ str(self.name) ,
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

        self.state = "done"
        

class InventoryAdjustmentLine(models.Model):
    _name = 'hop.inventory.adj.line'

    adj_id = fields.Many2one('hop.inventory.adj',string="Adjustment",ondelete='cascade', log_access=True)
    product_id = fields.Many2one('product.product', string='Raw Material',track_visibility='onchange')
    qty = fields.Float(string="Quantity",store=True,track_visibility='onchange')
    new_qty = fields.Float(string="New Quantity",track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.qty = self.product_id.qty_available