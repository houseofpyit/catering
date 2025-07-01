from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

class Hopledger(models.TransientModel):
    _name = "hop.ledger"

    
    
    from_date = fields.Date(string="From Date",default=fields.Date.context_today)
    to_date = fields.Date(string="To Date",default=fields.Date.context_today)
    party_ids = fields.Many2many('res.partner','ref_party_ids_ledger',string="Party")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    def generate(self):
        sql = "delete from hop_ledger_line "
        self._cr.execute(sql)
        from_date = self.from_date
        to_date = self.to_date
        domain = []
        if self.party_ids:
            domain.append(('id','=',self.party_ids.ids))
        partner_record = self.env['res.partner'].search(domain)
        print(partner_record)
        for party in partner_record:
            sql = """
                SELECT x.date, x.doc, x.des, x.credit, x.debit, x.partner_id
                FROM (
                    SELECT a.date, a.name as doc, a.narration as des,
                        CASE WHEN a.move_type = 'in_invoice' THEN a.amount_total ELSE 0 END as credit,
                        CASE WHEN a.move_type = 'out_invoice' THEN a.amount_total ELSE 0 END as debit,
                        a.partner_id
                    FROM account_move a
                    WHERE a.partner_id = %s AND a.date BETWEEN %s AND %s
                    And a.amount_total > 0
                    and a.state = 'posted'
                    

                    UNION ALL

                    SELECT b.date, b.name as doc, '' as des,
                        CASE WHEN a.payment_type = 'inbound' THEN a.amount ELSE 0 END as credit,
                        CASE WHEN a.payment_type = 'outbound' THEN a.amount ELSE 0 END as debit,
                        a.partner_id
                    FROM account_payment a
                    LEFT JOIN account_move b ON a.move_id = b.id
                    WHERE a.partner_id = %s AND b.date BETWEEN %s AND %s
                    And a.amount > 0
                    and b.state = 'posted' 
                ) AS x
                ORDER BY x.date;
            """
            params = (party.id, from_date, to_date, party.id, from_date, to_date)
            self.env.cr.execute(sql, params)
            query_result = self.env.cr.dictfetchall()

            for i in query_result:
                if i['credit'] > 0 or i['debit'] > 0:
                    self.env['hop.ledger.line'].create({
                        'date': i['date'],
                        'doc': i['doc'],
                        'des': i['des'],
                        'credit': i['credit'],
                        'debit': i['debit'],
                        'balance': i['credit'] - i['debit'],
                        'party_id': i['partner_id'],
                    })

    def generate_ledger(self):
     
        self.generate()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Ledger',
            'view_mode': 'tree',
            'res_model': 'hop.ledger.line',
            'context': "{'create': False,'edit':False,'delete':False, 'group_by': 'party_id'}",
            'target':"main"
        }

    def generate_ledger_pdf_vals(self):
        self.generate()
        record=self.env['hop.ledger.line'].search([])
        # for res in record.mapped('party_id'):
        #     credit = 0
        #     debit = 0
        #     balance = 0
        #     for line in record.filtered(lambda l: l.party_id.id == res.id):
        #         credit = credit + line.credit
        #         debit = debit + line.debit
        #         balance = credit - debit
        #         record_list.append(
        #             {
        #             'date': line.date,
        #             'doc': line.doc,
        #             'des':line.des,
        #             'credit': line.credit,
        #             'debit': line.debit,
        #             'balance': line.balance,
        #             'party_name': line.party_id.name,
        #             })
        #     record_list.append(
        #             {
        #             'date': '',
        #             'doc': '',
        #             'des':'',
        #             'credit': credit,
        #             'debit': debit,
        #             'balance': balance,
        #             'party_name': 'Total',
        #             })
        # print(record_list)
        # main.update({'from_date':self.from_date})
        # main.update({'to_date':self.to_date})
        # main.update({'company_id':self.company_id.logo})
        # main.update({'data':record_list})
        main={}
        party_data=[]
        for res in record.mapped('party_id'):
            record_list = []
            for line in record.filtered(lambda l: l.party_id.id == res.id):
                record_list.append(
                    {
                    'date': line.date,
                    'doc': line.doc,
                    'des':line.des,
                    'credit': line.credit,
                    'debit': line.debit,
                    'balance': line.balance,
                    'party_name': line.party_id.name,
                    })
            party_data.append({'party':res.name,'detail':record_list})
        main.update({'ledger_data':party_data})
        main.update({'from_date':self.from_date})
        main.update({'to_date':self.to_date})
        main.update({'company_id':self.company_id.logo if self.company_id.logo else False})

        print(",,,,,,,,,,,,................,,,,,,,,,,,",main)
        return [main]
    def generate_ledger_pdf(self):
        return self.env.ref('ct_report_v15.action_ledger_report').report_action(self)              

class HopledgerLine(models.Model):
    _name = "hop.ledger.line"

    date = fields.Date(string="Date")
    doc = fields.Char(string="Documents")
    des = fields.Char(string="Description")
    credit = fields.Float(string="Credit")
    debit = fields.Float(string="Debit")
    balance = fields.Float(string="Balance")
    party_id = fields.Many2one('res.partner',string="Party")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

