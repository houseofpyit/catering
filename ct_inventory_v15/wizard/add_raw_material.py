from odoo import api, models, fields

class AddRawMaterial(models.TransientModel):
    _name='hop.add.raw.material'

    item_id = fields.Many2one('product.product', string='Iteam Name')
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    recipes_id = fields.Many2one('hop.recipes', string='Recipes')
    


    def add_raw_material(self):
        print(self[0].recipes_id.id)

        raw_list = []
        for line in self:
            raw_list.append((0, 0,
                            {
                                'item_id': line.item_id.id, 
                            }))
        raw_rec = self.env['hop.recipes'].search([('id','=',self[0].recipes_id.id)])
        if raw_rec:
            # raw_rec.raw_materials_ids = False
            raw_rec.raw_materials_ids = raw_list
            for line in raw_rec.raw_materials_ids:
                line._onchange_item_id()
                line._compute_price()
   
    