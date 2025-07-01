from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError,RedirectWarning
class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        total_user = self.env['ir.config_parameter'].sudo().get_param('total_number_of_users')
        total_existing_users = len(self.env['res.users'].search([]))
        if int(total_user) <= total_existing_users:
            raise UserError('You cannot create more user...')
        return super(ResUsers, self).create(vals)
