from odoo import api, models, fields
from num2words import num2words
import json

class InheritAccountMove(models.Model):
    _inherit = "account.move"

    po_type = fields.Selection([
                                ('in_house','In-House PO'),('normal','Normal PO')],string="PO Type")
    

    def action_post(self):
        res = super(InheritAccountMove,self).action_post()
        for line in self.invoice_line_ids:
            if line.purchase_id:
                line.purchase_id.write({
                        'partner_ref': self.name,
                    })
        return res

    def amount_to_text(self, amount, currency='INR'):
        word = num2words(amount,lang='en_IN').upper()
        return word

    def get_amount(self,type):
        payment_records = self.env['account.payment'].search([('partner_id','=',self.partner_id.id),('state','=','posted')])
        discount_amount = 0
        payment_amount = 0
        list = []
        for record in payment_records:
            if record.partner_type == 'customer':
                list = record.reconciled_invoice_ids.ids
            else:
                list = record.reconciled_bill_ids.ids
            if self.id in list:
                if record.journal_id.id == self.env.ref('ct_function_v15.hr_discount_journal').id:
                    discount_amount = discount_amount + record.amount
                elif record.journal_id.name in ('Bank','Cash'):
                    payment_amount = payment_amount + record.amount


        if type == 'discount':
            return discount_amount
        elif type == 'advance':
            return payment_amount

    def get_gst_amount(self):
        gst = {'sgst': 0, 'cgst': 0, 'igst': 0}
        
        for fun in self:
            to_compare = json.loads(fun.tax_totals_json)
            for groups in to_compare['groups_by_subtotal'].values():
                for line in groups:
                    tax_group_name = line.get('tax_group_name')
                    tax_group_amount = line.get('tax_group_amount')
                    if tax_group_name == 'SGST':
                        gst['sgst'] += tax_group_amount
                    elif tax_group_name == 'CGST':
                        gst['cgst'] += tax_group_amount
                    elif tax_group_name == 'IGST':
                        gst['igst'] += tax_group_amount
        
        return {k: v for k, v in gst.items() if v > 0}


class InheritAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    purchase_id = fields.Many2one('purchase.order',"Purchase Order")
    sale_id = fields.Many2one('sale.order',"Sale Order")
    fun_date = fields.Date(string="Function Date",default=fields.Date.context_today)