from odoo import api, models, fields
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from odoo.exceptions import UserError,ValidationError,RedirectWarning

class HopCategory(models.Model):
    _name = "hop.category"
    _inherit = ['mail.thread']
    _description = "Category"

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

    def unlink(self):
        if self.env.ref('ct_contact_v15.manager_category').id == self.id:
            raise UserError("You cannot delete this record..")
        return super().unlink()


    def button_create(self):
        
        record = self.env['hop.category'].search([])
        for line in record:
            line._onchange_name()
            line._onchange_convert_name()

        record = self.env['res.partner'].search([])
        for line in record:
            line._onchange_name()
            line._onchange_convert_name()

        record = self.env['hop.function.mst'].search([])
        for line in record:
            line._onchange_name()
            line._onchange_convert_name()

        record = self.env['product.template'].search([])
        for line in record:
            line._onchange_name()
            line._onchange_convert_name()
        
        record = self.env['product.category'].search([])
        for line in record:
            line._onchange_name()
            line._onchange_convert_name()
        record = self.env['hop.recipes.category'].search([])
        for line in record:
            line._onchange_name()
            line._onchange_convert_name()
        
        record = self.env['hop.recipes'].search([])
        for line in record:
            line._onchange_name()
            line._onchange_convert_name()


