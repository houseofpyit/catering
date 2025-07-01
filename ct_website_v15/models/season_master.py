from odoo import api, models, fields

class HopSeasonMaster(models.Model):
    _name = "hop.season.master"
    _description = "SeasonMaster"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name",tracking=True)
