from odoo import api, models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from io import BytesIO
import base64
import json
from odoo.addons.ct_function_v15.custom_utils import translate_field ,location_field,meal_type

class purcheshallpowizard(models.TransientModel):
    _name='purchesh.all.po.wizard'

    date = fields.Date(string="Date",default=fields.Date.context_today)
    function_id = fields.Many2one('hop.function', string='Function',domain="[('date','=',date)]")
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Order')
    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])

    @api.onchange('function_id')
    def _onchange_function_id(self):
        if self.function_id:
            records = self.env['purchase.order'].search([('fuction_id_rec','=',self.function_id.id)])
            self.purchase_order_ids = records

    def action_generate_po(self):
        attachments = []

        fun_name = False
        for order in self.purchase_order_ids:
            if not fun_name:
                fun_name = order.fuction_id_rec.party_name_id.name  + ' - '+  str(order.fuction_id_rec.date.strftime('%d-%m-%Y')) + ' - ' + dict(order.fuction_id_rec._fields['meal_type'].selection).get(order.fuction_id_rec.meal_type)
            # record = self.env.ref('ct_function_v15.action_po_print_format')._render_qweb_pdf(order.id)
            # main=[]
            # list=[]
            # party_list={}
            # for fun in order:
            #     date =  False
            #     time = False
            #     am_pm = False
            #     if fun.delivery_date:
            #         date = fun.delivery_date.strftime('%d-%m-%Y')
            #     else:
            #         date = fun.date.strftime('%d-%m-%Y')
            #     if fun.delivery_time:
            #         time =  f"{int(fun.delivery_time):02d}:{int((fun.delivery_time % 1) * 60):02d}"
            #     else:
            #         time =  f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}"
            #     if fun.delivery_am_pm:
            #         am_pm = dict(fun._fields['delivery_am_pm'].selection).get(fun.delivery_am_pm)
            #     else:   
            #         am_pm = dict(fun._fields['am_pm'].selection).get(fun.am_pm)

            #     if fun.company_id.logo:
            #         company_logo = str(fun.company_id.logo ,'utf-8')
            #     else:
            #         company_logo = ''
            #     party_list.update({
            #         'name':fun.name,
            #         'partner_id':translate_field(fun.partner_id ,self.language),
            #         'company_id':  company_logo,
            #         'date':fun.date,
            #         'time':f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d} {'AM' if fun.am_pm == 'am' else 'PM'}",
            #         'am_pm':dict(fun._fields['am_pm'].selection).get(fun.am_pm),
            #         'delivery_time':time,
            #         'delivery_date':date,
            #         'delivery_am_pm':am_pm,
            #         'venue_address':fun.venue_address,
            #         'meal_type': meal_type(fun.meal_type,self.language,fun),
            #         'phone':fun.partner_id.phone,
            #         'maneger':translate_field(fun.manager_name_id ,self.language),
            #         'maneger_phone':fun.manager_name_id.phone,
            #         'remarks': fun.remarks,
            #         })
                            
            #     for cat in fun.order_line:
            #         record = self.env['hop.recipes'].search([('product_id','=',cat.product_id.id)])
            #         product_id = False
            #         if record:
            #             product_id = record
            #         else:
            #             product_id = cat.product_id
            #         list.append({
            #         'product_id' : translate_field(product_id,self.language),
            #         'product_qty':cat.product_qty,
            #         'product_uom': cat.product_uom.name,
            #         'helper': cat.helper,
            #         'chief': cat.chief,
            #         'date': cat.date,
            #         'time': cat.time,
            #         'am_pm': cat.am_pm,
            #         'name': cat.name,
            #         'no_of_pax': cat.no_of_pax,
            #         'order_qty': cat.order_qty,
            #         'instruction': cat.instruction,
            #         'category_id' :translate_field(cat.category_id  ,self.language),
            #         'hospitality_ids' : cat.hospitality_ids.name,
            #         'shift_date' : cat.shift_date,
            #         'shift_time' : f"{int(cat.shift_time):02d}:{int((cat.shift_time % 1) * 60):02d}",
            #         'remarks': cat.remarks,
            #         'price_subtotal': cat.price_subtotal,
            #         'location': location_field(cat.location,self.language,cat),

            #         })
            
            #     party_list.update({'po_type':fun.po_type,'product_list':list})

            # main.append(party_list)
            # if not list:
            #     return

            # datas = {'ids': self.ids,
            #     'form': self.ids,
            #     'model':'hop.print',
            #     'data':main,
            #     }

            # record =  self.env.ref('ct_function_v15.action_all_po_prints')._render_qweb_pdf(self, data=datas)
            new_record = self.env['po.print.report.wizard'].create({'language':self.language,'po_ids':[(6,0,order.ids)]})
            record =  new_record.action_confirm_render_qweb_pdf()
            print("***************",record)
            data = base64.b64encode(record[0])
            name_parts = []
            if order.venue_address:
                name_parts.append(order.venue_address[:10])
            if order.date:
                name_parts.append(str(order.date))
            if order.partner_id:
                name_parts.append(order.partner_id.name)
            if order.meal_type:
                name_parts.append(dict(order._fields['meal_type'].selection).get(order.meal_type))
            if order.po_type:
                name_parts.append(dict(order._fields['po_type'].selection).get(order.po_type))
            
            attachment_name = '-'.join(name_parts) + '.pdf'
            
            attach_vals = {
                'name': attachment_name,
                'type': 'binary',
                'datas': data,
            }
            attachment = self.env['ir.attachment'].create(attach_vals)
            attachments.append(attachment.id)

        attachment_ids = ','.join(map(str, attachments))
        if not attachment_ids:
            raise ValidationError("Purchase Order is not found")
        url = '/web/binary/download_document_zip?tab_id=%s' % [attachment_ids,fun_name]
        
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
