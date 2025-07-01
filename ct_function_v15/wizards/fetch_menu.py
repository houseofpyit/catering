from odoo import api, models, fields

class FetchMenu(models.TransientModel):
    _name = 'hop.fetch.menu'

    fuction_id = fields.Many2one('hop.function',string="Function")

    def action_ok(self):
        fetch  = self.env[self.env.context.get('active_model')].browse(self.env.context['active_id'])
        if fetch.stage == 'create_menu':
            fetch.accompplishment_line_ids =False
            fetch.fuction_line_ids = False
            list_line=[]
            for line in self.fuction_id.fuction_line_ids:
                list_line.append(
                    (0,0,{
                        'category_id':line.category_id.id,
                        'item_id':line.item_id.id,
                        'jobwork_type':line.item_id.jobwork_type,
                        'instruction':line.instruction,
                        'uom':line.item_id.uom.id,
                    })
                )
            fetch.fuction_line_ids = list_line

            list_line=[]
            for line in self.fuction_id.accompplishment_line_ids:
                list_line.append(
                    (0,0,{
                        'item_id':line.item_id.id,
                        'accomplishment_id':[(6,0,line.accomplishment_id.ids)]
                        
                    })
                )
            fetch.accompplishment_line_ids = list_line
            fetch._onchange_function_id()
            for line in fetch.fuction_line_ids:    
                line._onchange_jobwork_type()
