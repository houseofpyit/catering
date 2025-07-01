from odoo import api, models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    total_number_of_users = fields.Integer('Total Number Of User')
    font_family = fields.Char('Font-Family')
    inhouse_outsource_po_master_rate = fields.Boolean(string="Inhouse Outsource Po Vender Rate", default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        total_number_of_users = ir_config.get_param('total_number_of_users', default=1)
        res.update(
            total_number_of_users=total_number_of_users
        )
        font_family = ir_config.get_param('font_family', default="")
        res.update(
            font_family=font_family
        )
        inhouse_outsource_po_master_rate = ir_config.get_param('inhouse_outsource_po_master_rate', default=False)
        res.update(
            inhouse_outsource_po_master_rate=inhouse_outsource_po_master_rate
        )
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("total_number_of_users", self.total_number_of_users or 1)
        ir_config.set_param("font_family", self.font_family or "")
        ir_config.set_param("inhouse_outsource_po_master_rate", self.inhouse_outsource_po_master_rate or False)
        