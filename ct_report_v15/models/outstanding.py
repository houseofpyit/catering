from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

class HopOutstanding(models.TransientModel):
    _name = "hop.outstanding"

    type = fields.Selection([('customer','Customer'),('vendor','Vendor')],string="Type")
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    customer_ids = fields.Many2many('res.partner','ref_customer_ids_outstanding',string="Customer")
    vendor_ids = fields.Many2many('res.partner','ref_vendor_ids_outstanding',string="Vendor")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)


    def generate(self):
        sql = "delete from hop_outstanding_line "
        self._cr.execute(sql)
        domain = []
        if self.type == 'customer':
            domain.append(('is_customer','=',True))
        elif self.type == 'vendor':
            domain.append(('is_vender','=',True))
        if self.vendor_ids:
            domain.append(('id','=',self.vendor_ids.ids))
        if self.customer_ids:
            domain.append(('id','=',self.customer_ids.ids))
        partner_record = self.env['res.partner'].search(domain)
        print(partner_record)
        for party in partner_record:
            sql = """
            SELECT   SUM(x.total_amt) as total_amt, SUM(x.received_amt) as received_amt,  SUM(x.total_amt) - SUM(x.received_amt) as  balance_amt ,x.partner_id
                FROM (
            SELECT   a.amount_total as total_amt , 0 as received_amt, 
            a.partner_id
                    FROM account_move a
         
                    WHERE a.amount_total > 0 and a.partner_id = %s AND a.date BETWEEN %s AND %s  """
            if self.type == 'customer':
                sql += """  and a.move_type  in ('out_invoice') """
            if self.type == 'vendor':
                sql += """  and a.move_type  in ('in_invoice') """
            sql += " and a.state not in ('cancel') "
            sql += """  
                union all	
            SELECT 0 as total_amt , a.amount as received_amt,    
                        a.partner_id
                    FROM account_payment a
                    LEFT JOIN account_move b ON a.move_id = b.id
                WHERE  a.amount > 0 and  a.partner_id = %s AND b.date BETWEEN %s AND %s  """
            if self.type == 'customer':
                sql += """  and a.payment_type  in ('inbound') """
            if self.type == 'vendor':
                sql += """  and a.payment_type  in ('outbound') """
            sql += " and b.state not in ('cancel') "
            sql += """        ) AS x
                        GROUP BY x.partner_id 
                    ORDER BY x.partner_id;
            """
            
            params = (party.id, self.from_date, self.to_date, party.id, self.from_date, self.to_date)
            self.env.cr.execute(sql, params)
            query_result = self.env.cr.dictfetchall()

            for i in query_result:
                self.env['hop.outstanding.line'].create({
                    'party_id': i['partner_id'],
                    'phone': party.phone,
                    'total_amt': i['total_amt'],
                    'received_amt': i['received_amt'],
                    'balance': i['balance_amt'],

                })

        # for party in partner_record:
        #     # sql = """
        #     #     SELECT  x.doc, SUM(x.credit) as credit, SUM(x.debit) as debit, x.partner_id
        #     #     FROM (
        #     #         SELECT a.date, a.name as doc, a.narration as des,
        #     #             CASE WHEN a.move_type = 'in_invoice' THEN a.amount_total ELSE 0 END as credit,
        #     #             CASE WHEN a.move_type = 'out_invoice' THEN a.amount_total ELSE 0 END as debit,
        #     #             a.partner_id
        #     #         FROM account_move a
        #     #         WHERE a.partner_id = %s AND a.date BETWEEN %s AND %s
        #     #         And a.amount_total > 0

        #     #         UNION ALL

        #     #         SELECT b.date, '' as doc, '' as des,
        #     #             CASE WHEN a.payment_type = 'inbound' THEN a.amount ELSE 0 END as credit,
        #     #             CASE WHEN a.payment_type = 'outbound' THEN a.amount ELSE 0 END as debit,
        #     #             a.partner_id
        #     #         FROM account_payment a
        #     #         LEFT JOIN account_move b ON a.move_id = b.id
        #     #         WHERE a.partner_id = %s AND b.date BETWEEN %s AND %s
        #     #         And a.amount > 0
        #     #     ) AS x
        #     #     GROUP BY x.doc,x.partner_id 
        #     #     ORDER BY x.partner_id;
        #     # """
        #     # params = (party.id, from_date, to_date, party.id, from_date, to_date)
        #     # self.env.cr.execute(sql, params)
        #     tot_net_amount = 0
        #     tot_payment_amount = 0
        #     tot_discount_amount = 0
        #     invoice_records = self.env['account.move'].search([('partner_id','=',party.id),('date','<=',self.to_date),('date','>=',self.from_date),('state','=','posted'),('move_type','in',('in_invoice','out_invoice'))])
        #     for invoice in invoice_records:
        #         payment_records = self.env['account.payment'].search([('partner_id','=',party.id),('state','=','posted')])
        #         discount_amount = 0
        #         payment_amount = 0
        #         for record in payment_records:
        #             if self.type == 'customer':
        #                 list = record.reconciled_invoice_ids.ids
        #             else:
        #                 list = record.reconciled_bill_ids.ids
        #             if invoice.id in list:
        #                 if record.journal_id.id == self.env.ref('ct_function_v15.hr_discount_journal').id:
        #                     discount_amount = discount_amount + record.amount
        #                     tot_discount_amount = tot_discount_amount + record.amount
        #                 elif record.journal_id.name in ('Bank','Cash'):
        #                     tot_payment_amount = tot_payment_amount + record.amount
        #                     payment_amount = payment_amount + record.amount
        #         tot_net_amount = tot_net_amount + invoice.amount_total
        #         print(payment_amount)
        #         self.env['hop.outstanding.line'].create({
        #                 'doc': invoice.name,
        #                 'net_amount': invoice.amount_total,
        #                 'discount_amount':discount_amount,
        #                 'payment_amount':payment_amount,
        #                 'balance': invoice.amount_total - payment_amount - discount_amount,
        #                 'party_id': invoice.partner_id.id,                  
        #             })
        #     payment_records = self.env['account.payment'].search([('partner_id','=',party.id),('state','=','posted')])
        #     for record in payment_records:
        #         if self.type == 'customer':
        #             list = record.reconciled_invoice_ids.ids
        #         else:
        #             list = record.reconciled_bill_ids.ids
        #         if list == []:
        #             if record.journal_id.id == self.env.ref('ct_function_v15.hr_discount_journal').id:
        #                 tot_discount_amount = tot_discount_amount + record.amount
        #                 self.env['hop.outstanding.line'].create({
        #                         'doc': record.name+(' Unadjust'),
        #                         'net_amount': 0,
        #                         'discount_amount':record.amount,
        #                         'payment_amount':0,
        #                         'balance': - record.amount,
        #                         'party_id': party.id,                  
        #                     })
        #             elif record.journal_id.name in ('Bank','Cash'):
        #                 tot_payment_amount = tot_payment_amount + record.amount
        #                 self.env['hop.outstanding.line'].create({
        #                         'doc': record.name +(' Unadjust'),
        #                         'net_amount': 0,
        #                         'discount_amount':0,
        #                         'payment_amount':record.amount,
        #                         'balance': - record.amount,
        #                         'party_id': party.id,                  
        #                     })
        #     # if  tot_net_amount != 0 or tot_payment_amount != 0 or tot_discount_amount != 0:
        #     #     self.env['hop.outstanding.line'].create({
        #     #                     'doc': 'Total',
        #     #                     'net_amount': tot_net_amount,
        #     #                     'discount_amount':tot_discount_amount,
        #     #                     'payment_amount':tot_payment_amount,
        #     #                     'balance': tot_net_amount - tot_payment_amount - tot_discount_amount,
        #     #                     'party_id': False,                  
        #     #                 })

    def generate_outstanding(self):
        self.generate()
        vals = {
            'type': 'ir.actions.act_window',
            'name': 'Outstanding',
            'view_mode': 'tree',
            'res_model': 'hop.outstanding.line',
            'context': "{'create': False,'edit':False,'delete':False}",
            'target':"main"
        }
        if self.type == 'customer':
            vals.update({'name': 'Customer Outstanding'})
        elif self.type == 'vendor':
            vals.update({'name': 'Vendor Outstanding'})
        return vals

    def generate_outstanding_pdf_vals(self):
        self.generate()
        record=self.env['hop.outstanding.line'].search([])
        # main={}
        # record_list = []
        # for res in record.mapped('party_id'):
        #     net_amount = 0
        #     payment_amount = 0
        #     discount_amount = 0
        #     balance = 0
        #     for line in record.filtered(lambda l: l.party_id.id == res.id):
        #         net_amount = net_amount + line.net_amount
        #         payment_amount = payment_amount + line.payment_amount
        #         discount_amount = discount_amount + line.discount_amount
        #         balance = balance + line.balance
        #         record_list.append(
        #             {
        #             'doc': line.doc,
        #             'net_amount': line.net_amount,
        #             'payment_amount': line.payment_amount,
        #             'discount_amount': line.discount_amount,
        #             'balance': line.balance,
        #             'party_name': line.party_id.name,
        #             })
        #     record_list.append(
        #             {
        #             'doc': '',
        #             'net_amount': net_amount,
        #             'payment_amount': payment_amount,
        #             'discount_amount': discount_amount,
        #             'balance': net_amount - payment_amount - discount_amount,
        #             'party_name': 'Total',
        #             })
        # print(record_list)
        main={}
        party_data=[]
        record_list = []
        for res in record.mapped('party_id'):
            for line in record.filtered(lambda l: l.party_id.id == res.id):
                record_list.append({
                    'phone': line.phone,
                    'total_amt': line.total_amt,
                    'received_amt': line.received_amt,
                    'balance': line.balance,
                    'party_name': line.party_id.name,
                    })
            # party_data.append({'party':res.name,'detail':record_list})
        main.update({'record_list':record_list})
        main.update({'from_date':self.from_date})
        main.update({'to_date':self.to_date})
        main.update({'company_id':self.company_id.logo if self.company_id.logo else False})
        
        return [main]
    
    def generate_outstanding_pdf(self):
        return self.env.ref('ct_report_v15.action_outstanding_report').report_action(self)              

class HopoutstandingLine(models.Model):
    _name = "hop.outstanding.line"

    # doc = fields.Char(string="Documents")
    # party_id = fields.Many2one('res.partner',string="Party")
    # net_amount = fields.Float(string="Net Amount")
    # payment_amount = fields.Float(string="Payment Amount")
    # discount_amount = fields.Float(string="Discount Amount")
    # balance = fields.Float(string="Balance")

    party_id = fields.Many2one('res.partner',string="Party")
    phone = fields.Char(string="Phone")
    total_amt= fields.Float(string="Total Amount")
    received_amt = fields.Float(string="Received Amount")
    balance = fields.Float(string="Balance")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
