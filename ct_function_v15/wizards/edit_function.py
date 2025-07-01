from odoo import api, models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from datetime import datetime, date ,timedelta


class EditFunction(models.TransientModel):
    _name='hop.edit.function'

    # edit_menu = fields.Boolean(string="Edit Or Replace Menu")
    # edit_addons = fields.Boolean(string="Edit Or Replace Add-ons")
    # edit_no_of_pax = fields.Boolean(string="Edit No Of Pax")

    edit_type = fields.Selection([
        ('add_menu', "Add Menu"),
        ('replace_menu', "Replace Menu"),
        ('remove_menu', "Remove Menu"),
        ('add_edit_addons', "Add or Edit Addons"),
        ('edit_no_of_pax', "Change No of Pax")
        ], default=False, help="Type")
    
    add_recipes_id = fields.Many2one('hop.recipes',string="Add Item Name",track_visibility='onchange')
    replace_recipes_id = fields.Many2one('hop.recipes',string="Replace Item Name",track_visibility='onchange')
    remove_recipes_id = fields.Many2one('hop.recipes',string="Remove Item Name",track_visibility='onchange')
    new_recipes_id = fields.Many2one('hop.recipes',string="New Item Name",track_visibility='onchange')
    menu_recipes_ids = fields.Many2many('hop.recipes','edit_function_menu_recipes_ids_ref',string="Order Menu Items",track_visibility='onchange')
    no_of_pax = fields.Integer(string="No Of Pax")
    addons_line_ids = fields.One2many('hop.edit.function.addons', 'mst_id',string="Add-ons Line")

    def confirm(self):
        active_model = self.env.context.get('model')
        active_id = self.env.context.get('id')
        raw_rec = self.env[active_model].browse(active_id)
        if self.edit_type == 'edit_no_of_pax':
            if self.no_of_pax == 0:
                raise UserError("Kindly Enter The No. Of Pax First!!!")
            purchase = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id)])
            for line in purchase:
                line.with_context(edit_purchase=True,no_of_pax_chnage=True).action_all_order_cancel()
            raw_rec.no_of_pax =  self.no_of_pax
            for line in raw_rec.fuction_line_ids:
                if line.insider_id:
                    line.no_of_pax = self.no_of_pax
                    line._onchange_per_qty()
                else:
                    line.no_of_pax = 0
                    line.qty = 0
            query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(raw_rec.ids[0])
            self._cr.execute(query)
            record = self.env['hop.recipe.rm'].search([('function_id','=',raw_rec.ids[0])])
            for line in record:
                sql = "delete from hop_rec_rm_line WHERE recipe_rm_id = "+ str(line.ids[0])
                self._cr.execute(sql)

            query = "DELETE FROM hop_recipe_rm WHERE function_id =" + str(raw_rec.ids[0])
            raw_rec.sudo().with_context(reset_to_draft=True).write({'stage':'confirm_menu'})
            raw_rec.hop_lead_id.no_of_pax =  self.no_of_pax
            raw_rec.hop_lead_id.calendar_line_id.no_of_pax =  self.no_of_pax
            for line in raw_rec.hop_lead_id.fuction_line_ids:
                line._onchange_jobwork_type()
            raw_rec.hop_lead_id.create_quotation()
            
            quot_count = self.env['sale.order'].search([('lead_id','=',raw_rec.hop_lead_id.id)])
            if quot_count:
                vals = {'sale_id':quot_count.id}
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Confirm',
                    'view_mode': 'form',
                    'res_model': 'hop.quotation.open',
                    'target':'new',
                    'context':vals
                }
        elif self.edit_type == 'add_edit_addons' :
            purchase_record = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.id),('state','!=','cancel'),('po_type','=','addons')])
            for pur in purchase_record:
                account_move = self.env['account.move.line'].search([('purchase_id','=',pur.id)])
                if account_move.move_id.state == 'posted':
                    raise UserError("Invoice already generated...")
            raw_rec.sudo().with_context(reset_to_draft=True).write({'stage':'confirm_menu'})
            for line in purchase_record:
                line.with_context(edit_purchase=True).action_all_order_cancel()
            raw_rec.extra_service_line_ids =  False
            line_list = []
            for record in self.addons_line_ids:
                line_list.append((0,0, {
                    'vender_id':record.vender_id.id,
                    'service_id':record.service_id.id,
                    'qty_ids':record.qty_ids,
                    'uom_id':record.uom_id.id,
                    'price':record.price,
                    'cost':record.cost,
                    'date':record.date,
                    'time':record.time,
                    'am_pm':record.am_pm,
                    'instruction':record.instruction,
                    'company_id':record.company_id.id
                }))
            raw_rec.extra_service_line_ids = line_list
            raw_rec.hop_lead_id.extra_service_line_ids = False
            ser_list = []
            for q in self.addons_line_ids:
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
            raw_rec.skip_addons = False
            raw_rec.hop_lead_id.extra_service_line_ids = ser_list
            raw_rec.hop_lead_id.create_quotation()

            quot_count = self.env['sale.order'].search([('lead_id','=',raw_rec.hop_lead_id.id)])
            if quot_count:
                vals = {'sale_id':quot_count.id}
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Confirm',
                    'view_mode': 'form',
                    'res_model': 'hop.quotation.open',
                    'target':'new',
                    'context':vals
                }
        elif self.edit_type == 'add_menu' :
            if self.add_recipes_id:
                po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.ids[0]),('po_type','=','row_material')])
                for line in po_rec:
                    line.with_context(edit_purchase=True).action_all_order_cancel()
                query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(raw_rec.ids[0])
                self._cr.execute(query)
                record = self.env['hop.recipe.rm'].search([('function_id','=',raw_rec.ids[0])])
                for line in record:
                    sql = "delete from hop_rec_rm_line WHERE recipe_rm_id = "+ str(line.ids[0])
                    self._cr.execute(sql)

                query = "DELETE FROM hop_recipe_rm WHERE function_id =" + str(raw_rec.ids[0])
                raw_rec.sudo().with_context(reset_to_draft=True).write({'stage':'confirm_menu'})
                line_list = []
                line_list.append((0,0,{
                    'category_id': self.add_recipes_id.category_id.id,
                    'item_id': self.add_recipes_id.id,
                    'uom': self.add_recipes_id.uom.id,
                }))
                raw_rec.fuction_line_ids = line_list
                raw_rec.hop_lead_id.fuction_line_ids = line_list
                quot_count = self.env['sale.order'].search([('lead_id','=',raw_rec.hop_lead_id.id)])
                if quot_count:
                    vals = {'sale_id':quot_count.id}
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Confirm',
                        'view_mode': 'form',
                        'res_model': 'hop.quotation.open',
                        'target':'new',
                        'context':vals
                    }
            else:
                raise UserError("Kindly Enter The Item Name First!!!")
        elif self.edit_type == 'replace_menu' :
            record = raw_rec.fuction_line_ids.filtered(lambda l: l.item_id.id == self.replace_recipes_id.id)
            if record:
                purchase_line  = self.env['purchase.order.line'].search([('fuction_line_id','=',record.id)])
                if purchase_line.order_id:
                    account_move = self.env['account.move.line'].search([('purchase_id','=',purchase_line.order_id.id)])
                    if account_move.move_id.state == 'posted':
                        raise UserError("Invoice already generated...")
            if self.new_recipes_id and self.replace_recipes_id:
                po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.ids[0]),('po_type','=','row_material')])
                for line in po_rec:
                    line.with_context(edit_purchase=True).action_all_order_cancel()
                query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(raw_rec.ids[0])
                self._cr.execute(query)
                rm_record = self.env['hop.recipe.rm'].search([('function_id','=',raw_rec.ids[0])])
                for line in rm_record:
                    sql = "delete from hop_rec_rm_line WHERE recipe_rm_id = "+ str(line.ids[0])
                    self._cr.execute(sql)

                query = "DELETE FROM hop_recipe_rm WHERE function_id =" + str(raw_rec.ids[0])
                raw_rec.sudo().with_context(reset_to_draft=True).write({'stage':'confirm_menu'})
                if record:
                    if len(purchase_line.order_id.order_line) == 1:
                        purchase_line.order_id.with_context(edit_purchase=True).action_all_order_cancel()
                    else:
                        purchase_line.unlink()
                record.unlink()
                line_list = []
                line_list.append((0,0,{
                    'category_id': self.new_recipes_id.category_id.id,
                    'item_id': self.new_recipes_id.id,
                    'uom': self.new_recipes_id.uom.id,
                }))
                raw_rec.fuction_line_ids = line_list
                record = raw_rec.hop_lead_id.fuction_line_ids.filtered(lambda l: l.item_id.id == self.replace_recipes_id.id)
                if record:
                    record.write({
                    'category_id': self.new_recipes_id.category_id.id,
                    'item_id': self.new_recipes_id.id,
                    'uom': self.new_recipes_id.uom.id,
                })

                quot_count = self.env['sale.order'].search([('lead_id','=',raw_rec.hop_lead_id.id)])
                if quot_count:
                    vals = {'sale_id':quot_count.id}
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Confirm',
                        'view_mode': 'form',
                        'res_model': 'hop.quotation.open',
                        'target':'new',
                        'context':vals
                    }
            else:
                raise UserError("Kindly Enter The New Item Name First!!!")
        elif self.edit_type == 'remove_menu':
            record = raw_rec.fuction_line_ids.filtered(lambda l: l.item_id.id == self.remove_recipes_id.id)
            if record:
                if record.insider_id:
                    purchase_line  = self.env['purchase.order.line'].search([('fuction_line_id','=',record.id)])
                    po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',raw_rec.ids[0]),('po_type','=','row_material')])
                    for line in po_rec:
                        line.with_context(edit_purchase=True).action_all_order_cancel()
                    query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(raw_rec.ids[0])
                    self._cr.execute(query)
                    rm_record = self.env['hop.recipe.rm'].search([('function_id','=',raw_rec.ids[0])])
                    for line in rm_record:
                        sql = "delete from hop_rec_rm_line WHERE recipe_rm_id = "+ str(line.ids[0])
                        self._cr.execute(sql)

                    query = "DELETE FROM hop_recipe_rm WHERE function_id =" + str(raw_rec.ids[0])
                    raw_rec.sudo().with_context(reset_to_draft=True).write({'stage':'confirm_menu'})
                    if record:
                        if len(purchase_line.order_id.order_line) == 1:
                            purchase_line.order_id.with_context(edit_purchase=True).action_all_order_cancel()
                        else:
                            purchase_line.unlink()
                    record.unlink()
                    remove_record = raw_rec.hop_lead_id.fuction_line_ids.filtered(lambda l: l.item_id.id == self.remove_recipes_id.id)
                    if remove_record:
                        remove_record.unlink()
                else:
                    purchase_line  = self.env['purchase.order.line'].search([('fuction_line_id','=',record.id)])
                    if record:
                        if len(purchase_line.order_id.order_line) == 1:
                            purchase_line.order_id.with_context(edit_purchase=True).action_all_order_cancel()
                        else:
                            purchase_line.unlink()
                    record.unlink()
                    remove_record = raw_rec.hop_lead_id.fuction_line_ids.filtered(lambda l: l.item_id.id == self.remove_recipes_id.id)
                    if remove_record:
                        remove_record.unlink()
                    raw_rec.sudo().with_context(reset_to_draft=True).write({'stage':'confirm_menu'})

                quot_count = self.env['sale.order'].search([('lead_id','=',raw_rec.hop_lead_id.id)])
                if quot_count:
                    vals = {'sale_id':quot_count.id}
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Confirm',
                        'view_mode': 'form',
                        'res_model': 'hop.quotation.open',
                        'target':'new',
                        'context':vals
                    }


    @api.model
    def default_get(self, fields):
        res = super(EditFunction, self).default_get(fields)
        active_model = self.env.context.get('model')
        active_id = self.env.context.get('id')
        raw_rec = self.env[active_model].browse(active_id)
        rm_list =[]
        if raw_rec:
            for i in raw_rec.fuction_line_ids:
                rm_list.append(i.item_id.id)                          
        res['menu_recipes_ids'] = [(6,0, rm_list)]
        line_list = []
        for record in raw_rec.extra_service_line_ids:
            line_list.append((0,0, {
                   'vender_id':record.vender_id.id,
                   'service_id':record.service_id.id,
                   'qty_ids':record.qty_ids,
                   'uom_id':record.uom_id.id,
                   'price':record.price,
                   'cost':record.cost,
                   'date':record.date,
                   'time':record.time,
                   'am_pm':record.am_pm,
                   'instruction':record.instruction,
                   'company_id':record.company_id.id
            }))
        res['addons_line_ids'] = line_list
        return res
    
class HospitalityShiftLine(models.TransientModel):
    _name = 'hop.edit.function.addons'
    _description = 'Extra Service Line'

    vender_id = fields.Many2one('res.partner',string="Vender Name",domain=[('is_vender','=',True)] ,tracking=True)
    mst_id = fields.Many2one('hop.edit.function',string="Hospitality", ondelete='cascade', log_access=True)

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