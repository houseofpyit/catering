from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

class FunctionCostingreportwizard(models.TransientModel):
    _name = 'function.costing.report.wizard'

    fuction_ids = fields.Many2many('hop.function',string="Function",domain="[('date','>=',from_date),('date','<=',to_date)]")
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    def action_print(self):
        self.generate()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Costing Report',
            'view_mode': 'tree',
            'res_model': 'hop.costing',
            'context': "{'create': False,'edit':False,'delete':False, 'group_by': 'partner_id'}"
        }

    def generate_pdf_vals(self):
        self.generate()
        record=self.env['hop.costing'].search([])

        main={}
        party_data=[]
        for res in record.mapped('partner_id'):
            record_list = []
            for line in record.filtered(lambda l: l.partner_id.id == res.id):
                record_list.append(
                    {
                    'partner':line.partner_id.name,
                    'function':dict(line.function_id._fields['meal_type'].selection).get(line.function_id.meal_type) ,
                    'in_house_cost':line.in_house_cost,
                    'out_source_cost': line.out_source_cost,
                    'labour_cost': line.labour_cost,
                    'addons_cost': line.addons_cost,
                    'raw_material_cost': line.raw_material_cost,
                    'raw_material_issue_cost':line.raw_material_issue_cost,
                    'raw_material_return_cost':line.raw_material_return_cost,
                    'total':line.total,
                    })
            party_data.append({'partner':res.name,'detail':record_list})
        main.update({'costing_data':party_data})
        main.update({'from_date':self.from_date})
        main.update({'to_date':self.to_date})
        main.update({'company_id':self.company_id.logo if self.company_id.logo else False})

        return [main]
    def generate_pdf(self):
        return self.env.ref('ct_report_v15.action_costing_report').report_action(self)
    
    def generate(self):
        sql = "delete from hop_costing;"
        self._cr.execute(sql)
        domain = [('date','>=',self.from_date),('date','<=',self.to_date)]
        if self.fuction_ids:
                domain.append(('id','in',self.fuction_ids.ids))
        functions = self.env['hop.function'].search(domain)
        if not functions:
            raise UserError("No Record Found............")
        for res in functions:
            
            in_house_cost =0
            out_source_cost = 0
            labour_cost = 0
            addons_cost = 0
            raw_material_cost = 0
            raw_material_issue_cost = 0
            raw_material_return_cost = 0
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','in_house')])
            if po_rec:
                in_house_cost = sum(po_rec.mapped('amount_total'))
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','out_source')])
            if po_rec:
                out_source_cost = sum(po_rec.mapped('amount_total'))
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','service')])
            if po_rec:
                labour_cost = sum(po_rec.mapped('amount_total'))
            po_rec  = self.env['purchase.order'].search([('fuction_id_rec','=',res.id),('po_type','=','addons')])
            if po_rec:
                addons_cost = sum(po_rec.mapped('amount_total'))
            record = self.env['hop.recipe.rm'].search([('function_id','=',res.id)])
            for line in record:
                raw_material_cost = raw_material_cost + sum(self.env['hop.rec_rm.line'].search([('recipe_rm_id','=',line.id)]).mapped('cost'))
            raw_material_issue_cost = sum(self.env['hop.inventory'].search([('type','=','issue'),('inventory_id','=',res.id)]).mapped('cost'))
            raw_material_return_cost = sum(self.env['hop.inventory'].search([('type','=','return'),('inventory_id','=',res.id)]).mapped('cost'))
            

            self.env['hop.costing'].create({
                        'partner_id':res.party_name_id.id,
                        'function_id':res.id,
                        'in_house_cost':in_house_cost,
                        'out_source_cost': out_source_cost,
                        'labour_cost': labour_cost,
                        'addons_cost': addons_cost,
                        'raw_material_cost': raw_material_cost,
                        'raw_material_issue_cost':raw_material_issue_cost,
                        'raw_material_return_cost':raw_material_return_cost,
                        'total':out_source_cost + labour_cost + addons_cost + raw_material_cost + raw_material_issue_cost - raw_material_return_cost + in_house_cost,
                    })    
        
class Costing(models.Model):
    _name = "hop.costing"

    partner_id= fields.Many2one('res.partner',string="Party Name")
    function_id = fields.Many2one('hop.function',string="Function")
    in_house_cost = fields.Float(string="In House PO")
    out_source_cost = fields.Float(string="Out Source PO")
    labour_cost = fields.Float(string="Labour PO")
    addons_cost = fields.Float(string="Add-ons PO")
    raw_material_cost = fields.Float(string="Raw Materials")
    raw_material_issue_cost = fields.Float(string="Raw Materials Issue")
    raw_material_return_cost = fields.Float(string="Raw Materials Return")
    total = fields.Float(string="Total Cost")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)



