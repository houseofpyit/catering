
from odoo import api, models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning

class HospitalityShift(models.TransientModel):
    _name = 'hop.extra.service.wizard'

    delivery_date = fields.Date('Delivery Date')
    delivery_time = fields.Float('Delivery Time')
    delivery_am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM")
    function_date = fields.Date('function Date')
    vender_id = fields.Many2one('res.partner',string="Vendor")
    vender_ids = fields.Many2many('res.partner','ref_extra_service_vender_ids',string="Vendors")
    line_ids = fields.One2many('hop.extra.service.line.wizard','mst_id',string="line")

    @api.onchange('delivery_date')
    def _onchange_delivery_date(self):  
        if  self.delivery_date:
            if  self.delivery_date > self.function_date:
                raise UserError("Can't Select This Date!!!!")

    def action_apply_all(self):
        self.ensure_one()
        for line in self.line_ids.filtered(lambda l: l.vender_id.id == self.vender_id.id):
            line.delivery_date = self.delivery_date
            line.delivery_time = self.delivery_time
            line.delivery_am_pm = self.delivery_am_pm
        return {
        'context': self.env.context,
        # 'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'hop.extra.service.wizard',
        'res_id': self.id,
        'view_id': False,
        'type': 'ir.actions.act_window',
        'target': 'new',
    }

    @api.model
    def default_get(self, fields):
        res = super(HospitalityShift, self).default_get(fields)
        
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        raw_rec = self.env[active_model].browse(active_id)
        line_list = []
        purchase = []
        purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('state','!=','cancel'),('po_type','=','addons')])
        for order in purchase_record:
            for line in order.order_line:
                if line.service_line_id:
                    purchase.append(line.service_line_id.id)           
        for i in raw_rec.extra_service_line_ids.mapped('vender_id'):
            if i.id in raw_rec.extra_service_line_ids.filtered(lambda l: l.vender_id.id == i.id and l.id not in purchase).mapped('vender_id').ids:
                line_list.append((0,0, {
                            'name': i.name,
                            'display_type': 'line_section',
                        }))
            for record in raw_rec.extra_service_line_ids.filtered(lambda l: l.vender_id.id == i.id and l.id not in purchase):
                line_list.append((0,0, {
                        'display_type': False,
                        'name': i.name,
                        'vender_id': record.vender_id.id,
                        'service_id': record.service_id.id,
                        'qty_ids': record.qty_ids,
                        'uom_id': record.uom_id.id,
                        'price': record.price,
                        'cost': record.cost,
                        'date': record.date,
                        'time': record.time,
                        'am_pm': record.am_pm,
                        }))
        res['vender_ids'] = raw_rec.extra_service_line_ids.mapped('vender_id').ids
        res['line_ids'] = line_list
        res['function_date'] = raw_rec.date
        res['delivery_date'] = raw_rec.date
        return res
    
    def action_confirm(self):
        # for line in self.line_ids:
        #     if line.vender_id: 
        #         if not line.delivery_date or not line.delivery_time or not line.delivery_am_pm:
        #             raise UserError("Frist Select Delivery Date, Delivery Time and AM-PM.... ")
        active_model = self.env.context.get('active_model')
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        raw_rec = self.env[active_model].browse(active_id)
        purchase = []
        purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('state','!=','cancel'),('po_type','=','addons')])
        for order in purchase_record:
            for line in order.order_line:
                if line.service_line_id:
                    purchase.append(line.service_line_id.id)  
        if raw_rec.extra_service_line_ids:
            for i in raw_rec.extra_service_line_ids.mapped('vender_id'): 
                line_list = []
                if i.id in raw_rec.extra_service_line_ids.filtered(lambda l: l.vender_id.id == i.id and l.id not in purchase).mapped('vender_id').ids:
                    for record in raw_rec.extra_service_line_ids.filtered(lambda l: l.vender_id.id == i.id):
                        line_list.append((0,0, {
                                'product_id': record.service_id.id,
                                'name':'',
                                'no_of_pax': '',
                                'product_qty': record.qty_ids,
                                # 'price_unit': record.service_id.lst_price,    
                                'price_unit': record.cost,    
                                'product_uom':record.uom_id.id,
                                'date': record.date,
                                'time': record.time,
                                'am_pm': record.am_pm,
                                'instruction': record.instruction,
                                'service_line_id':record.id
                        }))
                    rec = self.line_ids.filtered(lambda l: l.vender_id.id == i.id)
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
                            'po_type': 'addons',
                            'remarks': raw_rec.remarks,
                            'venue_address': raw_rec.venue_address,
                            'date': raw_rec.date,
                            'time': raw_rec.time,
                            'am_pm': raw_rec.am_pm,
                            'meal_type': raw_rec.meal_type,
                            'manager_name_id': raw_rec.manager_name_id.id,
                            'order_line': line_list,
                            'delivery_date':delivery_date,
                            'delivery_time':delivery_time,
                            'delivery_am_pm':delivery_am_pm,
                        })
            raw_rec.is_addons_po = True
class HospitalityShiftLine(models.TransientModel):
    _name = 'hop.extra.service.line.wizard'
    _description = 'Extra Service Line'

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name=fields.Text('Vender')
    mst_id = fields.Many2one('hop.extra.service.wizard',string="service line")
    vender_id = fields.Many2one('res.partner',string="Vender Name",domain=[('is_vender','=',True)] ,tracking=True)
    service_id = fields.Many2one('product.product', string='Service',track_visibility='onchange')
    qty_ids = fields.Float(string="Quantity/Person",tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UoM')
    price = fields.Float(string="Sale Praice",tracking=True)
    cost = fields.Float(string="Cost",tracking=True)
    date = fields.Date(string="Date")
    time = fields.Float(string="Time")
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    delivery_date = fields.Date('Delivery Date')
    delivery_time = fields.Float('Delivery Time')
    delivery_am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM")