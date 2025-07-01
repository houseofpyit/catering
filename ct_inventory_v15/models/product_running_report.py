from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from datetime import datetime, date, timedelta


class ProductRunningReport(models.Model):
    _name = "hop.product.running.report"

    product_id = fields.Many2one('product.product', string='Product')
    date = fields.Date(string="Inquiry Date")
    open = fields.Float(string="Opening")
    purchase = fields.Float(string="Purchased")
    use = fields.Float(string="Used")
    close = fields.Float(string="Closed")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)

    def generate_running_stock(self, year, product):
        print("********************")
        fun_record = self.search([])
        for line in fun_record:
            line.unlink()
        
        end_date = datetime(year + 1, 3, 31)
        start_date = datetime(year, 4, 1)
        close_date = datetime(year, 3, 31)  # Extract the current date without time
        self.fetch_data(close_date, product, type='opening')

        while start_date.date() <= end_date.date():
            self.fetch_data(start_date.date(), product)
            start_date += timedelta(days=1)

    def fetch_data(self, date, product, type=''):
        pur_domain = []
        fun_domain = []
        if type == 'opening':
            pur_domain = [('date', '<', date), ('state', '!=', 'cancel'),('partner_id','!=',self.env.ref('ct_inventory_v15.partner_godown').id)]
            fun_domain = [('date', '<', date), ('stage', '!=', 'cancel')]
        else:
            pur_domain = [('date', '=', date), ('state', '!=', 'cancel'),('partner_id','!=',self.env.ref('ct_inventory_v15.partner_godown').id)]
            fun_domain = [('date', '=', date), ('stage', '!=', 'cancel')]

        purchase = self.env['purchase.order'].search(pur_domain)
        pur_qty = 0
        rm_qty = 0
        issue_qty = 0
        return_qty = 0

        for res in purchase:
            pur_qty += sum(res.order_line.filtered(lambda l: l.product_id.id == product.id).mapped('product_qty'))

        fun_record = self.env['hop.function'].search(fun_domain)
        rm_record = self.env['hop.recipe.rm'].search([('function_id', 'in', fun_record.ids)])

        for rm in rm_record:
            print(rm.function_id)
            rm_qty += sum(rm.rec_rm_ids.filtered(lambda l: l.product_id.id == product.id).mapped('weight'))
        print(rm_qty)
        for fun in fun_record:
            issue_qty += sum(fun.inventory_line_ids.filtered(lambda l: l.product_id.id == product.id and l.type == 'issue').mapped('qty'))
            return_qty += sum(fun.inventory_line_ids.filtered(lambda l: l.product_id.id == product.id and l.type == 'return').mapped('qty'))
        product_opening_stock = sum(self.env['hop.opening.stock'].search([('product_id','=',product.id),('date','=',date)]).mapped('qty'))
        if product_opening_stock >0:
            self.create({
                'product_id': product.id,
                'date': date,
                'open': product_opening_stock,
                'purchase': 0,
                'use': 0,
                'close': 0,
            })


        if pur_qty > 0 or rm_qty > 0 or issue_qty > 0 or return_qty > 0:
            last_record = self.search([('date', '<', date)], limit=1, order='date desc')
            last_close = last_record.close if last_record else 0

            self.create({
                'product_id': product.id,
                'date': date,
                'open': last_close,
                'purchase': pur_qty,
                'use': rm_qty + issue_qty - return_qty,
                'close': last_close + pur_qty - rm_qty - issue_qty + return_qty
            })

# def generate_accounting_dates(start_year, end_year):
#     dates = []
    
#     for year in range(start_year, end_year + 1):
#         start_date = datetime(year, 4, 1)
#         end_date = datetime(year + 1, 3, 31)
#         dates.append((start_date, end_date))
    
#     return dates

# start_year = 2023
# end_year = 2025



# def generate_dates(start_date, end_date):
#     current_date = start_date
#     while current_date <= end_date:
#         yield current_date
#         current_date += timedelta(days=1)

# start_date = datetime(2023, 4, 1)
# end_date = datetime(2025, 3, 31)

# for date in generate_dates(start_date, end_date):
#     print(date.strftime("%d-%m-%Y"))

# current_date = datetime.now()
# current_year = current_date.year
