from odoo import models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning
import base64

class HopCancel(models.TransientModel):
    _name='hop.cancel'

    name = fields.Text('Reason')

    def action_cancel(self):
        if not self.name :
            raise UserError("Please enter the valid reason...")
        if self.env.context.get('model',False) == 'hop.function':
            record = self.env['hop.function'].search([('id','in',self.env.context['id'])])
            for line in record:
                line.cancel(self.name)
            return {
            'type': 'ir.actions.act_window',
            'name': 'Order Details',
            'view_mode': 'tree,form',
            'res_model': 'hop.function',
            'context': "{'create': False}",
            'target':'main',
        }
        elif self.env.context.get('model',False) == 'hop.lead':
            record = self.env['hop.lead'].search([('id','in',self.env.context['id'])])
            for line in record:
                line.cancel(self.name)
            return {
            'type': 'ir.actions.act_window',
            'name': 'Menu Planner',
            'view_mode': 'tree,form',
            'res_model': 'hop.lead',
            'context': "{'create': False}",
            'target':'main',
        }
            
        elif self.env.context.get('model',False) == 'hop.calendar':
            record = self.env['hop.calendar'].search([('id','in',self.env.context['id'])])
            for line in record:
                line.cancel(self.name)
            return {
            'type': 'ir.actions.act_window',
            'name': 'Event Inquiry',
            'view_mode': 'tree,form',
            'res_model': 'hop.calendar',
            'context': "{'create': False}",
            'target':'main',
        }

class HopConfirm(models.TransientModel):
    _name='hop.confirm'

    def action_confirm(self):
        if self.env.context.get('model',False) == 'hop.function':
            record = self.env['hop.function'].search([('id','in',self.env.context['id'])])
            for line in record:
                line.unlink()
            return {
            'type': 'ir.actions.act_window',
            'name': 'Order Details',
            'view_mode': 'tree,form',
            'res_model': 'hop.function',
            'context': "{'create': False}",
            'target':'main',
        }

class HopQuotationOpen(models.TransientModel):
    _name='hop.quotation.open'

    def action_confirm(self):
        return {
                'name': 'Quotations',
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'form',
                'res_id':self.env.context['sale_id'],
                'target':'current',
            }  
