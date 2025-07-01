from odoo import api, models, fields

class HopVenue(models.Model):
    _name = "hop.venue"
    _inherit = ['mail.thread']
    _description = "Venue"

    name = fields.Char(string="Name",tracking=True)
    venue_add = fields.Text(string="Venue Address",tracking=True) 