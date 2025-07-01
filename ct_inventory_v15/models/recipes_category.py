from odoo import api, models, fields
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

class HopRecipesCategory(models.Model):
    _name = "hop.recipes.category"
    _inherit = ['mail.thread']
    _description = "Recipes Category"

    name = fields.Char(string="Name",tracking=True)
    convert_name = fields.Char(string="Convert Name",tracking=True)
    gujarati = fields.Char('Gujarati')
    hindi = fields.Char('Hindi')
    
    # @api.onchange('name')
    # def _onchange_name(self):
    #     name_vals = self.name
    #     if name_vals:
    #         self.convert_name = name_vals.lower()

    @api.onchange('convert_name')
    def _onchange_convert_name(self):
        if self.convert_name:
            name = self.convert_name
            self.gujarati = transliterate(name.lower(), sanscript.ITRANS, sanscript.GUJARATI)
            self.hindi = transliterate(name.lower(), sanscript.ITRANS, sanscript.DEVANAGARI)
        else:
            self.gujarati = False
            self.hindi = False