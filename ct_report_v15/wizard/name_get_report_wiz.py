from odoo import api, models, fields,_
# from odoo.exceptions import UserError
from odoo.addons.ct_function_v15.custom_utils import translate_field


class NameGetReportWizard(models.TransientModel):
    _name = 'hop.name.get.report.wizard'

    count = fields.Char(string="Count")
    recipes_selection = fields.Selection([('auto','Auto'),('manually','Manually')], defualt='auto', string="Recipes Selection")
    item_ids = fields.Many2many('hop.recipes',string="Item Name")
    fuction_name_id = fields.Many2many('hop.function',string="Function Name")
    total = fields.Integer(string="Total",default=1)
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
    
    @api.onchange('fuction_name_id')
    def _onchange_reccipes_selection(self):
        if self.recipes_selection == 'auto':
            print(self.fuction_name_id.ids)
            self.count  = len(self.env['hop.fuction.line'].search([('fuction_id','in',self.fuction_name_id.ids)]).ids)
           
    def front_sty(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        return ir_config.get_param('font_family')

    def create_name_tags_vals(self):
        iteam_list = []
        if self.recipes_selection == 'manually':
            function_rec = self.env['hop.recipes'].search([('id','in',self.item_ids.ids)]) 
            srl = 0
            vals ={}
            for i in function_rec:
                for x in range(self.total):
                    # print("--------------- function ",i.fuction_id.party_name_id.name)
                    if srl == 0:
                        print("------------- balnk")
                        vals = {
                            "1":"",
                            "2":""
                        }
                    if srl == 0:
                        vals.update({"1":translate_field(i, self.language)})
                        srl = 1
                        continue
                    if srl == 1:
                        vals.update({"2":translate_field(i, self.language)})
                        srl = 0
                        iteam_list.append(vals)
                        vals = {
                            "1":"",
                            "2":""
                        }
            if vals["1"]:
                iteam_list.append(vals)
        else:
            function_rec = self.env['hop.fuction.line'].search([('fuction_id','in',self.fuction_name_id.ids)])
            srl = 0
            vals ={}
            for i in function_rec:
                print("--------------- function ",i.fuction_id.party_name_id.name)
                if srl == 0:
                    print("------------- balnk")
                    vals = {
                        "1":"",
                        "2":""
                    }
                if srl == 0:
                    vals.update({"1":translate_field(i.item_id , self.language)})
                    srl = 1
                    continue
                if srl == 1:
                    vals.update({"2":translate_field(i.item_id , self.language)})
                    srl = 0
                    iteam_list.append(vals)
                    vals = {
                        "1":"",
                        "2":""
                    }
            if vals["1"]:
                iteam_list.append(vals)
        image =  False
        if self.env.company.watermark_image_name_tag:
            image = True
        return {'image':image,'list':iteam_list}
        return iteam_list

        # main =[{'item_list':iteam_list}]
        # print("--------------------------------",iteam_list)
        # datas = {'ids': self.ids,
        #          'form': self.ids,
        #          'model':'hop.name.get.report.wizard',
        #          'data':data_dict,
        #          }
    def action_print(self):
        return self.env.ref('ct_report_v15.action_name_get_fuction_report').report_action(self.id)
                
