from odoo import api, models, fields
from io import BytesIO
import base64
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime

class Print(models.TransientModel):
    _name = 'hop.print'

    type = fields.Selection([('menu','Menu'),('quotation','Quotation'),('both','Both')])
    without_description = fields.Boolean("Without Description")


    def convert_to_24hr_time(self, time_str, am_pm):
        print("..........", time_str)
        try:
            if not time_str or not am_pm:
                return None

            # Convert the input to a float and split into hours and minutes
            time_float = float(time_str)
            hours = int(time_float)
            minutes = int(round((time_float - hours) * 60))  # Convert fractional hours to minutes

            # Ensure minutes are valid
            if minutes >= 60:
                raise ValueError("Invalid time format")

            # Construct time string
            time_str = f"{hours}:{minutes:02d}"

            # Parse and adjust for AM/PM
            time_obj = datetime.strptime(time_str, '%I:%M')
            if am_pm.lower() == 'pm' and time_obj.hour != 12:
                time_obj = time_obj.replace(hour=time_obj.hour + 12)
            elif am_pm.lower() == 'am' and time_obj.hour == 12:
                time_obj = time_obj.replace(hour=0)
            return time_obj.time()
        except (ValueError, TypeError) as e:
            print(f"Error: {e}")
            return None

    
    def sort_list(self,record):
        list_record=[]
        for line in record:
            list_record.append({
                'object':line,"time":self.convert_to_24hr_time(line.time,line.am_pm)
            })
        sorted_list = sorted(list_record, key=lambda x: x['time'])
        return [entry['object'] for entry in sorted_list]

    def action_print(self, context=None):
        fetch  = self.env[self.env.context.get('active_model')].browse(self.env.context['active_id'])
        fetch = fetch.sorted(
            key=lambda l: (getattr(l, 'date', None))
        )
        if self.env.context.get('active_model') == 'sale.order':
            list_record = []
            for line in fetch:
                list_record.append({
                    'object': line,
                    'datetime': line.lead_id.date,
                    'time': self.convert_to_24hr_time(line.lead_id.time, line.lead_id.am_pm)
                })

            # Sort by both datetime and time
            sorted_list = sorted(
                list_record,
                key=lambda x: (x['datetime'], x['time'])  # First by date, then by time
            )
            fetch = [entry['object'] for entry in sorted_list]
            if self.type == 'menu':
                # menu = self.env.ref('ct_report_v15.action_lead_funtion_report').report_action(fetch.lead_id.id)
                if fetch:
                    for order in fetch:
                        if self.without_description:
                            order.lead_id.without_description = True
                        else:
                            order.lead_id.without_description = False
                    return self.env.ref('ct_report_v15.action_lead_funtion_report').report_action([entry.lead_id.id for entry in fetch])
                else:
                    return
            elif self.type == 'quotation':
                return self.env.ref('ct_report_v15.action_print_report').report_action([entry.id for entry in fetch])
            
            elif self.type == 'both':
                attachment = []
                report = self.env.ref('ct_report_v15.action_print_report')._render_qweb_pdf([entry.id for entry in fetch])
                data = base64.b64encode(report[0])
                attach_vals = {
                    'name':'%s.pdf' % ('quotation'),
                    'type': 'binary',
                    'datas': data,
                }   
                attachment.append(self.env['ir.attachment'].create(attach_vals).id)
                for order in fetch:
                    if len(order.lead_id.fuction_line_ids) > 0:
                        if self.without_description:
                            order.lead_id.without_description = True
                        else:
                            order.lead_id.without_description = False
                record =  self.env.ref('ct_report_v15.action_lead_funtion_report')._render_qweb_pdf([entry.lead_id.id for entry in fetch])
                data = base64.b64encode(record[0])
                attach_vals = {
                    'name':'%s.pdf' % ('menu'),
                    'type': 'binary',
                    'datas': data,
                }
                attachment.append(self.env['ir.attachment'].create(attach_vals).id)

          
                print(attachment)
                url = '/web/binary/download_document?tab_id=%s' % attachment
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }

        elif self.env.context.get('active_model') == 'hop.calendar':
            list_record = []
            for line in fetch:
                list_record.append({
                    'object': line,
                    'datetime': line.date,
                })

            # Sort by both datetime and time
            sorted_list = sorted(
                list_record,
                key=lambda x: (x['datetime'])  # First by date, then by time
            )

            # Return only the original objects in sorted order
            fetch = [entry['object'] for entry in sorted_list]
            if self.type == 'menu':
                list = []
                for rec in fetch:
                    for line in self.sort_list(rec.calendar_line_ids):
                        if line.lead_id:
                            if self.without_description:
                                line.lead_id.without_description = True
                            if not self.without_description:
                                line.lead_id.without_description = False
                            list.append(line)
                list_record = []
                
                for line in list:
                    list_record.append({
                        'object': line,
                        'datetime': line.date,
                        'time': self.convert_to_24hr_time(line.time, line.am_pm)
                    })

                # Sort by both datetime and time
                sorted_list = sorted(
                    list_record,
                    key=lambda x: (x['datetime'], x['time'])  # First by date, then by time
                )
                list = [entry['object'].lead_id.id for entry in sorted_list]
                if list:
                    return self.env.ref('ct_report_v15.action_lead_funtion_report').report_action(list)
                else:
                    return
            elif self.type == 'quotation':
                main=[]
                list=[]
                party_list={}
                sgst=0
                igst=0
                cgst=0
                for rec in fetch:
                    for line in self.sort_list(rec.calendar_line_ids):
                        record = self.env['sale.order'].search([('lead_id','=',line.lead_id.id)])
                        for fun in record:

                            party_list.update({
                                'partner_id':fun.partner_id.name,
                                'company_id': fun.company_id.logo if fun.company_id.logo else False,
                                'date':fun.date.strftime('%d-%m-%Y'),
                                'street':fun.partner_id.street,
                                'city':fun.partner_id.city,
                                'state_id':fun.partner_id.state_id.name,
                                'country_id':fun.partner_id.country_id.name,
                                'phone':fun.partner_id.phone,
                                'fuction_name_id':fun.lead_id.fuction_name_id.name,
                                'vat':fun.partner_id.vat,
                                'remarks':fun.remarks,
                                'note':fun.note,
                                'name':fun.company_id.name,
                                'venue_address':fun.lead_id.venue_address,
                                'payment_condition':fun.company_id.payment_condition or  False
                              })
                            
                            
                            for cat in fun.order_line:
                                tax_list = ""
                                for gst in cat.tax_id:
                                    tax_list += gst.name  + " , "
                                list.append({
                                'lead_id':cat.order_id.lead_id,
                                'order_line_id':cat,
                                # 'name' : cat.name,
                                # 'product_id' : cat.product_id.name,
                                # 'gst':tax_list,
                                # 'product_uom_qty':int(cat.product_uom_qty),
                                # 'price_unit': cat.price_unit,
                                # 'price_subtotal': cat.price_subtotal,
                                })
                    for fun in self.env['sale.order'].search([('lead_id','in',rec.calendar_line_ids.mapped('lead_id').ids)]):
                        to_compare = json.loads(fun.tax_totals_json)
                        for groups in to_compare['groups_by_subtotal'].values():
                            for line in groups:  
                                if line.get('tax_group_name') == 'SGST':
                                    sgst = sgst + line.get('tax_group_amount')
                                if line.get('tax_group_name') == 'CGST':
                                    cgst = cgst + line.get('tax_group_amount')
                                if line.get('tax_group_name') == 'IGST':
                                    igst = igst + line.get('tax_group_amount')
                if sgst >0:
                    party_list.update({'sgst':sgst})
                if cgst >0:
                    party_list.update({'cgst':cgst})
                if igst >0:
                    party_list.update({'igst':igst})
                list_record = []
                for line in list:
                    list_record.append({
                        'order_line_id': line.get('order_line_id'),
                        'datetime': line.get('lead_id').date,
                        'time': self.convert_to_24hr_time( line.get('lead_id').time,  line.get('lead_id').am_pm)
                    })

                # Sort by both datetime and time
                sorted_list = sorted(
                    list_record,
                    key=lambda x: (x['datetime'], x['time'])  # First by date, then by time
                )
                # Return only the original objects in sorted order
                list = [entry['order_line_id'] for entry in sorted_list]
                order_line= []
                for cat in list:
                    tax_list = ""
                    for gst in cat.tax_id:
                        tax_list += gst.name  + " , "
                    order_line.append({
                    'name' : cat.name,
                    'product_id' : cat.product_id.name,
                    'gst':tax_list,
                    'product_uom_qty':int(cat.product_uom_qty),
                    'price_unit': cat.price_unit,
                    'price_subtotal': cat.price_subtotal,
                    })
                party_list.update({'product_list':order_line})

                main.append(party_list)
                if not list:
                    return

                datas = {'ids': self.ids,
                    'form': self.ids,
                    'model':'hop.print',
                    'data':main,
                    }

                return self.env.ref('ct_report_v15.action_quotation_print_report').report_action(self, data=datas)
         
            elif self.type == 'both':
                main=[]
                list=[]
                party_list={}
                sgst=0
                igst=0
                cgst=0
                for rec in fetch:
                    for line in self.sort_list(rec.calendar_line_ids):
                        record = self.env['sale.order'].search([('lead_id','=',line.lead_id.id)])
                        for fun in record:
                            party_list.update({
                                'partner_id':fun.partner_id.name,
                                'company_id': str(fun.company_id.logo if fun.company_id.logo else '','utf-8'),
                                'date':fun.date.strftime('%d-%m-%Y'),
                                'street':fun.partner_id.street,
                                'city':fun.partner_id.city,
                                'state_id':fun.partner_id.state_id.name,
                                'country_id':fun.partner_id.country_id.name,
                                'phone':fun.partner_id.phone,
                                'fuction_name_id':fun.lead_id.fuction_name_id.name,
                                'vat':fun.partner_id.vat,
                                'remarks':fun.remarks,
                                'note':fun.note,
                                'name':fun.company_id.name,
                                'venue_address':fun.lead_id.venue_address,
                                'payment_condition':fun.company_id.payment_condition or  False
                                })
                            
                            # print("---------------------",fun.tax_totals_json)
                            
                            for cat in fun.order_line:
                                tax_list = ""
                                for gst in cat.tax_id:
                                    tax_list += gst.name  + " , "
                                list.append({
                                'lead_id':cat.order_id.lead_id,
                                'order_line_id':cat,
                                # 'name' : cat.name,
                                # 'product_id' : cat.product_id.name,
                                # 'product_uom_qty':int(cat.product_uom_qty),
                                # 'gst':tax_list,
                                # 'price_unit': cat.price_unit,
                                # 'price_subtotal': cat.price_subtotal,
                                })
                    for fun in self.env['sale.order'].search([('lead_id','in',rec.calendar_line_ids.mapped('lead_id').ids)]):
                        to_compare = json.loads(fun.tax_totals_json)
                        for groups in to_compare['groups_by_subtotal'].values():
                            for line in groups:
                                if line.get('tax_group_name') == 'SGST':
                                    sgst = sgst + line.get('tax_group_amount')
                                if line.get('tax_group_name') == 'CGST':
                                    cgst = cgst + line.get('tax_group_amount')
                                if line.get('tax_group_name') == 'IGST':
                                    igst = igst + line.get('tax_group_amount')
                                print("-------------",sgst,cgst,igst)
                list_record = []
                for line in list:
                    list_record.append({
                        'order_line_id': line.get('order_line_id'),
                        'datetime': line.get('lead_id').date,
                        'time': self.convert_to_24hr_time( line.get('lead_id').time,  line.get('lead_id').am_pm)
                    })

                # Sort by both datetime and time
                sorted_list = sorted(
                    list_record,
                    key=lambda x: (x['datetime'],x['time'])  # First by date, then by time
                )
                # Return only the original objects in sorted order
                list = [entry['order_line_id'] for entry in sorted_list]
                
                order_line= []
                for cat in list:
                    tax_list = ""
                    for gst in cat.tax_id:
                        tax_list += gst.name  + " , "
                    order_line.append({
                    'name' : cat.name,
                    'product_id' : cat.product_id.name,
                    'gst':tax_list,
                    'product_uom_qty':int(cat.product_uom_qty),
                    'price_unit': cat.price_unit,
                    'price_subtotal': cat.price_subtotal,
                    })
                party_list.update({'product_list':order_line})
                # party_list.update({'product_list':list})
                if sgst >0:
                    party_list.update({'sgst':sgst})
                if cgst >0:
                    party_list.update({'cgst':cgst})
                if igst >0:
                    party_list.update({'igst':igst})
                main.append(party_list)
                attachment = []
                datas = {'ids': self.ids,
                    'form': self.ids,
                    'model':'hop.print',
                    'data':main,
                    }
                if main and list:
                    report = self.env.ref('ct_report_v15.action_quotation_print_report')._render_qweb_pdf(self, data=datas)
                    data = base64.b64encode(report[0])
                    attach_vals = {
                        'name':'%s.pdf' % ('quotation'),
                        'type': 'binary',
                        'datas': data,
                    }   
                    attachment.append(self.env['ir.attachment'].create(attach_vals).id)
                lead_list = []
                for rec in fetch:
                    for line in self.sort_list(rec.calendar_line_ids):
                        if line.lead_id:
                            if len(line.lead_id.fuction_line_ids) > 0:
                                if line.lead_id:
                                    if self.without_description:
                                        line.lead_id.without_description = True
                                    else:
                                        line.lead_id.without_description = False
                                    lead_list.append(line)
                list_record = []
                for line in lead_list:
                    list_record.append({
                        'object': line,
                        'datetime': line.date,
                        'time': self.convert_to_24hr_time(line.time, line.am_pm)
                    })

                # Sort by both datetime and time
                sorted_list = sorted(
                    list_record,
                    key=lambda x: (x['datetime'], x['time'])  # First by date, then by time
                )
                lead_list = [entry['object'].lead_id.id for entry in sorted_list]
                if lead_list:
                    record =  self.env.ref('ct_report_v15.action_lead_funtion_report')._render_qweb_pdf(lead_list)
                    data = base64.b64encode(record[0])
                    attach_vals = {
                        'name':'%s.pdf' % ('menu'),
                        'type': 'binary',
                        'datas': data,
                    }
                    attachment.append(self.env['ir.attachment'].create(attach_vals).id)
                if not lead_list and not list:
                    return
                    # print(attachment)
                url = '/web/binary/download_document?tab_id=%s' % attachment
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'target': 'new',
                }