from odoo import api, models, fields,_
from odoo.exceptions import UserError,ValidationError
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

class HopRecipes(models.Model):
    _name = "hop.recipes"
    _inherit = ['mail.thread']
    _rec_name = "name"
    _description = "Recipes"

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Name must be unique !')]

    @api.constrains('name')
    def _check_name(self):
        recipe_rec = self.env['hop.recipes'].search([('name', '=', self.name),('id', '!=', self.id)])
        if recipe_rec:
            raise ValidationError(_('Exists ! Already a recipe exists in this name'))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)") % (self.name)
        return super(HopRecipes, self).copy(default=default)

    name = fields.Char(string="Name",tracking=True)
    agencies_insider_id = fields.Many2one('res.partner',string="Insider",domain=[('is_vender','=',True)],tracking=True)
    uom = fields.Many2one('uom.uom',string="Uom",tracking=True)
    rate = fields.Float(string="Vendor Rate(Per Person)",tracking=True)
    qty = fields.Integer(string="Quantity",default='100',tracking=True)
    product_img = fields.Binary(attachment=True)
    convert_name = fields.Char(string="Convert Name",tracking=True)
    gujarati = fields.Char('Gujarati')
    hindi = fields.Char('Hindi')
    category_id = fields.Many2one('hop.recipes.category',string="Category",tracking=True )
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")
    remarks = fields.Text(string="Remarks",tracking=True)
    description = fields.Text("Description")
    product_id = fields.Many2one('product.product',string="Product")
    accomplishment = fields.Boolean(string="Accomplishment")
    cost = fields.Float(string="Per UoM Cost Rate",tracking=True,compute="_compute_cost_rate")
    
    agencies_ids = fields.One2many('hop.agencies.type', 'recipes_id',string="Agencies Type", tracking=True)
    raw_materials_ids = fields.One2many('hop.raw.materials', 'recipes_category_id',string="Raw Materials" ,copy=True, tracking=True)
    create_raw_material = fields.Boolean(string="Create Raw Material" , compute="compute_create_raw_material")
    is_recipe = fields.Boolean(string="Is Recipe")
    recipe = fields.Boolean(string="Is Recipe", compute="compute_recipe")
    jobwork_type = fields.Selection([('in_house','In house'),('out_source','Out-Source')],string="Work Type",tracking=True)
    vender_id = fields.Many2one('res.partner',string="Vendor",track_visibility='onchange',domain=[('is_vender','=',True)])

    def update_product_uom(self):
        for rec in self.search([]):
            if rec.uom.id != rec.product_id.uom_id.id:
                sql = "update  product_template set uom_id = %d , uom_po_id = %d where id=%d ;" % (rec.uom.id,rec.uom.id,rec.product_id.product_tmpl_id.id)
                self._cr.execute(sql)

    def update_uom(self):
        for rec in self.search([]):
            for line in rec.raw_materials_ids:
                line.uom = line.item_id.uom_id.id

    @api.depends('recipe')
    def compute_recipe(self):
        if len(self.raw_materials_ids) > 0:
            self.recipe = True
            self.is_recipe = True
        else:
            self.recipe = False
            self.is_recipe = False

    def with_without_update(self):
        for line in self.search([]):
            line.compute_recipe()

            
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
        for i in self:
            fun_re  = self.env['hop.fuction.line'].search([('item_id','=',i.id)])
            if fun_re:
                raise UserError("Can't Delete This Record")
            fun_lead  = self.env['hop.fuction.lead.line'].search([('item_id','=',i.id)])
            if fun_lead:
                raise UserError("Can't Delete This Record")
            uten_mst  = self.env['utensils.mst.line'].search([('item_id','=',i.id)])
            if uten_mst:
                raise UserError("Can't Delete This Record")
            fun_out  = self.env['hop.fuction.out.source.and.in.house.line.wizard'].search([('item_id','=',i.id)])
            if fun_out:
                raise UserError("Can't Delete This Record")
            rec_rm  = self.env['hop.recipe.rm'].search([('recipe_id','=',i.id)])
            if rec_rm:
                raise UserError("Can't Delete This Record")
            age_type  = self.env['hop.agencies.type'].search([('recipes_id','=',i.id)])
            if age_type:
                raise UserError("Can't Delete This Record")
            raw_mat  = self.env['hop.add.raw.material'].search([('recipes_id','=',i.id)])
            if raw_mat:
                raise UserError("Can't Delete This Record")
            itm_rpt  = self.env['hop.item.wise.report'].search([('item_id','=',i.id)])
            if itm_rpt:
                raise UserError("Can't Delete This Record")
            
            #Website not install 
            # pkg_lne  = self.env['hop.package.line'].search([('item_id','=',i.id)])
            # if pkg_lne:
            #     raise UserError("Can't Delete This Record")
        return super(HopRecipes,self).unlink()
    
    @api.depends('raw_materials_ids','cost')
    def _compute_cost_rate(self):
        for res in self:
            if sum(res.raw_materials_ids.mapped('price')) > 0:
                res.cost =  sum(res.raw_materials_ids.mapped('price')) / res.qty
            else:
                res.cost = 0
    
    @api.depends('create_raw_material')
    def compute_create_raw_material(self):
        for i in self:
            record = self.env['hop.add.raw.material'].search([('id','not in',self.env['product.product'].search([('utility_type', '=','raw_materials')]).ids)])
            if record:
                record.unlink()
            for record in self.env['product.product'].search([('id', 'not in',self.env['hop.add.raw.material'].search([]).ids),('utility_type', '=','raw_materials')]) :
                self.env['hop.add.raw.material'].create({
                        'item_id' : record.id,
                        'recipes_id': self.id,
                        'categ_id':record.categ_id.id
                        }) 
                
            sql = "update hop_add_raw_material set recipes_id=%d ;" % self.id
            self._cr.execute(sql)

            if self.raw_materials_ids:
                if self.raw_materials_ids.mapped('item_id').ids != []:
                    sql = "delete from hop_add_raw_material where item_id in %s ;" % self.tuple_return(self.raw_materials_ids.mapped('item_id').ids)
                    print("***********************************************",sql)
                    self._cr.execute(sql)
            i.create_raw_material = True

    def tuple_return(self,cut_list):
        typle_list=''
        for i in cut_list:
            if typle_list == '':
                typle_list += '(' + str(i)
            else:
                typle_list += ',' + str(i)
        typle_list +=')'
        return typle_list
    @api.model
    def create(self,vals):
        res = super(HopRecipes,self).create(vals)
        product_rec = self.env['product.product'].create({
            'name':vals['name'],
            'uom_id':vals['uom'],
            'uom_po_id':vals['uom'],
            'lst_price':vals['rate'],
            'is_recipe':True,
            })
        print("--------------------- product_rec",product_rec)
        # res['product_id'] = product_rec.id
        res.product_id = product_rec.id
        return res

    def write(self, vals):
        if vals.get('uom',False):
            sql = "update  product_template set uom_id = %d where id=%d ;" % (vals.get('uom',False),self.product_id.product_tmpl_id.id)
            self._cr.execute(sql)
        if vals.get('raw_materials_ids'):
            data_text = ""
            for i in vals.get('raw_materials_ids'):
                if i[2]:
                    data_text += str(i[2]) + ","
            message = _("Changes in Raw Material %s ",data_text if data_text else "Delete")
            self.message_post(body=message,message_type='comment')

        if vals.get('agencies_ids'):
            data_text = ""
            for i in vals.get('agencies_ids'):
                if i[2]:
                    data_text += str(i[2]) + ","
            message = _("Changes in Outsider Agencies %s ",data_text if data_text else "Delete")
            self.message_post(body=message,message_type='comment')
        for res in self:
            res.product_id.name = vals.get('name') or res.name
        return super().write(vals)

class HopAgenciesCategory(models.Model):
    _name = "hop.agencies.type"

    recipes_id = fields.Many2one('hop.recipes',string="Recipes Category", ondelete='cascade')
    agencies_outsider_id = fields.Many2one('res.partner',string="Agencies Name",tracking=True)
    agencies_rate = fields.Float(string="Agencies Rate",tracking=True)

class HopRawMaterials(models.Model):
    _name = "hop.raw.materials"

    recipes_category_id = fields.Many2one('hop.recipes',string="Recipes Category", ondelete='cascade', log_access=True)
    item_id = fields.Many2one('product.product',string="Item name",domain=[('utility_type','=','raw_materials')],track_visibility='onchange')
    uom = fields.Many2one('uom.uom',string="Uom",track_visibility='onchange')
    item_cost = fields.Float(string="Item Cost",related='item_id.standard_price')
    weight = fields.Float(string="Weight",track_visibility='onchange',digits='Stock Weight')
    price = fields.Float(string="Price",track_visibility='onchange', compute="_compute_price")


    @api.model
    def create(self,vals):
        res = super(HopRawMaterials,self).create(vals)
        # if res.weight == 0 :
        #     raise UserError("Kindly Enter the weight")  
        return res
    
    def write(self,vals):
        res = super(HopRawMaterials,self).write(vals)
        # if self.weight == 0 :
        #     raise UserError("Kindly Enter the weight")  
        return res
    
    @api.onchange('item_id')
    def _onchange_item_id(self):
        if self.item_id :
            self.uom = self.item_id.uom_id.id
            if self.item_id.standard_price != 0 :
                self.item_cost = self.item_id.standard_price 
            else:
                raise UserError('Enter Cost price in %s'% self.item_id.name)
    
    @api.depends('item_cost','weight')
    def _compute_price(self):
        self.price=0
        for rec in self:
            if rec.item_cost and rec.weight:
                rec.price = rec.item_cost * rec.weight
            # else:
            #     rec.price = rec.item_cost * rec.req_weight
