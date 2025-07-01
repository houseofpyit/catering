from odoo import api, models, fields

class AddRawUtensils(models.TransientModel):
    _name='hop.add.utensils'

    item_id = fields.Many2one('product.product', string='Iteam Name')
    utensils_type = fields.Selection([('ground','Ground'),('kitche','Kitchen'),('disposable','Disposable'),('decoration','Decoration')],string="Utensils Type",tracking=True)
    utensils_id = fields.Many2one('utensils.mst', string='Recipes')
    


    def add_utensils(self):

        utensils_list = []
        for line in self:
            utensils_list.append((0, 0,
                            {
                                'utensils_id': line.item_id.id, 
                            }))
        utensils_rec = self.env['utensils.mst'].search([('id','=',self[0].utensils_id.id)])
        if utensils_rec:
            # utensils_rec.utensils_line_ids = False
            utensils_rec.utensils_line_ids = utensils_list
            for line in utensils_rec.utensils_line_ids:
                line._onchange_utensils_id()
   
    