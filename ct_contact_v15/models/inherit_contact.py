from odoo import api, models, fields
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

class ContactInherit(models.Model):
    _inherit = "res.partner"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique ! !'),
        ('mobile_uniq', 'unique(mobile)', 'Alternative Number must be unique !'),
        ('phone_uniq', 'unique(phone)', 'Phone Number must be unique !')
    ]

    ct_category_id = fields.Many2one('hop.category',string="Category",tracking=True)
    convert_name = fields.Char(string="Convert Name",tracking=True)
    gujarati = fields.Char('Gujarati')
    hindi = fields.Char('Hindi')
    is_vender = fields.Boolean(string="Is Vendor", copy=False )
    is_customer = fields.Boolean(string="Is Customer", copy=False)
    mobile = fields.Char(string="Alternative Number")
    date_of_birth = fields.Date(string="Date Of Birth",tracking=True)
    date_of_marriage = fields.Date(string="Date Of Marriage",tracking=True)
    phone = fields.Char(string="Whatsapp Mo.")

    c_street = fields.Char()
    c_street2 = fields.Char()
    c_zip = fields.Char(change_default=True)
    c_city = fields.Char()
    c_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    c_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    cost = fields.Float(string="Cost",tracking=True)


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
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            records = self.search(['|', '|', ('name', operator, name), ('phone', operator, name), ('city', operator, name)]+args)
            return records.name_get()
        return self.search([('name', operator, name)]+args, limit=limit).name_get()