from odoo import api, models, fields

class RecipeRMWiz(models.Model):
    _name='hop.recipe.rm'


    recipe_id = fields.Many2one('hop.recipes', string='Recipe Name')
    fun_date = fields.Date(string="Function Date")
    venue_address = fields.Char(string="Venue Address")
    rec_rm_ids = fields.One2many('hop.rec_rm.line','recipe_rm_id', string="Raw Materials")
    function_id = fields.Many2one('hop.function', string='Function')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    @api.model
    def create(self,vals):
        res = super(RecipeRMWiz,self).create(vals)
        query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(res.function_id.ids[0])
        self._cr.execute(query)
        if self.env.context.get('create_one',False) == False:
            res.function_id.issue_rm()
        return res
    
    def write(self,vals):
        res = super(RecipeRMWiz,self).write(vals)
        query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(self.function_id.ids[0])
        self._cr.execute(query)
        self.function_id.issue_rm()
        return res  
    
    def unlink(self):
        function = self.function_id
        id =self.function_id.ids[0]
        res = super(RecipeRMWiz,self).unlink()  
        query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(id)
        self._cr.execute(query)
        function.issue_rm()
        return  res


class RecipeRMLine(models.Model):
    _name='hop.rec_rm.line'

    recipe_rm_id = fields.Many2one('hop.recipe.rm')
    product_id = fields.Many2one('product.product', string='Raw Materals',domain=[('utility_type','=','raw_materials')])
    uom = fields.Many2one('uom.uom',string="Uom",track_visibility='onchange')
    weight = fields.Float(string="Weight",track_visibility='onchange',digits='Stock Weight')
    cost = fields.Float(string="Cost",track_visibility='onchange')
    item_cost = fields.Float(string="Per Cost",track_visibility='onchange')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    @api.onchange('weight')
    def _onchange_weight(self):
        if self.product_id:
            self.cost = self.weight * self.product_id.standard_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.uom = self.product_id.uom_id
        
    # @api.model
    # def create(self,vals):
    #     print("****************create")
    #     res = super(RecipeRMLine,self).create(vals)
    #     query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(res.recipe_rm_id.function_id.ids[0])
    #     self._cr.execute(query)
    #     res.recipe_rm_id.function_id.issue_rm()
    #     return res
    
    # def write(self,vals):
    #     print("***************write")
    #     res = super(RecipeRMLine,self).write(vals)
    #     query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(self.recipe_rm_id.function_id.ids[0])
    #     self._cr.execute(query)
    #     self.recipe_rm_id.function_id.issue_rm()
    #     return res  
    
    def unlink(self):
        function = self.recipe_rm_id.function_id
        id =self.recipe_rm_id.function_id.ids[0]
        res = super(RecipeRMLine,self).unlink()  
        query = "DELETE FROM hop_raw_materal WHERE fuction_id = " + str(id)
        self._cr.execute(query)
        function.issue_rm()
        return  res