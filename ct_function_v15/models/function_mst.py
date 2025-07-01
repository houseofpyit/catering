from odoo import api, models, fields
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

class HopFunctionMst(models.Model):
    _name = "hop.function.mst"
    _inherit = ['mail.thread']
    _description = "Function Master"

    name = fields.Char(string="Function Name",tracking=True)
    convert_name = fields.Char(string="Convert Name",tracking=True)
    gujarati = fields.Char('Gujarati')
    hindi = fields.Char('Hindi')
    product_id = fields.Many2one('product.product',string="Product")

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
                
    @api.model
    def create(self,vals):
        res = super(HopFunctionMst,self).create(vals)
        product_rec = self.env['product.product'].create({
            'name':vals['name'],
            'detailed_type':'service',
            'is_funcion':True,
            })
        res.product_id = product_rec.id
        return res
