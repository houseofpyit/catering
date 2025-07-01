from odoo import api, models, fields

class HopGalleryMaster(models.Model):
    _name = "hop.gallery.master"
    _description = "Gallery"
    _inherit = ['mail.thread']

    name = fields.Char(string="Name",tracking=True)
    logo = fields.Binary(tracking=True)
    type = fields.Selection([
        ('corporate', 'Corporate'),
        ('wedding', 'Wedding'),
        ('special_occasions', 'Special Occasions'),
    ], string='Type',tracking=True)
    attachment_ids = fields.Many2many('ir.attachment',string="Attachment",tracking=True)
    menu_line_ids = fields.One2many('hop.gallery.menu.master','mst_id',string="Menu Line",tracking=True)
class MenuMaster(models.Model):
    _name="hop.gallery.menu.master"

    mst_id = fields.Many2one('hop.gallery.master',string="Menu",tracking=True)
    category_id = fields.Many2one('hop.recipes.category',string="Category",tracking=True)
    item_id = fields.Many2one('hop.recipes',string="Item Name",tracking=True)
    qty = fields.Char(string="Qty",tracking=True)