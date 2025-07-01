from odoo import api, models, fields

class HopSeasonRecipe(models.Model):
    _name = "hop.season.recipe"
    _description = "SeasonRecipe"
    _inherit = ['mail.thread']

    image = fields.Binary('Image', )
    season_id = fields.Many2one('hop.season.master',string="Name",tracking=True)
    recipe_id = fields.Many2one('hop.recipes',string="Recipe",tracking=True)
    description = fields.Char(string="Description",tracking=True)
