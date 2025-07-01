from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.addons.ct_function_v15.custom_utils import translate_field, meal_type, utensils_type ,location_field

class Po_Print_Report_Wizard(models.TransientModel):
    _name = 'po.print.report.wizard'

    language =  fields.Selection([('english','English'),('gujarati','ગુજરાતી'),('hindi','हिंदी')])
    po_ids = fields.Many2many('purchase.order','all_po_report')

    def report_vals(self):
        print("------------------ call method --------------",self.po_ids.ids,self.env.context)
        fetch  = self.env['purchase.order'].search([('id','=',self.po_ids.ids)])
        # fetch  = self.env['purchase.order'].browse(self.env.context['active_id'])
        print("------------------ call method fatch --------------",fetch)

        main=[]
        for fun in fetch:
            list=[]
            party_list={}
            date =  False
            time = False
            am_pm = False
            if fun.delivery_date:
                date = fun.delivery_date.strftime('%d-%m-%Y')
            else:
                date = fun.date.strftime('%d-%m-%Y')
            if fun.delivery_time:
                time =  f"{int(fun.delivery_time):02d}:{int((fun.delivery_time % 1) * 60):02d}"
            else:
                time =  f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d}"
            if fun.delivery_am_pm:
                am_pm = dict(fun._fields['delivery_am_pm'].selection).get(fun.delivery_am_pm)
            else:   
                am_pm = dict(fun._fields['am_pm'].selection).get(fun.am_pm)
            party_list.update({
                'name':fun.name,
                'partner_id':translate_field(fun.partner_id ,self.language),
                'company_id': fun.company_id.logo if fun.company_id.logo else False,
                'date':fun.date.strftime('%d-%m-%Y') if fun.date else '',
                'time':f"{int(fun.time):02d}:{int((fun.time % 1) * 60):02d} {'AM' if fun.am_pm == 'am' else 'PM'}",
                'am_pm':dict(fun._fields['am_pm'].selection).get(fun.am_pm),
                'delivery_time':time,
                'delivery_date':date,
                'delivery_am_pm':am_pm,
                'venue_address':fun.venue_address,
                'meal_type': meal_type(fun.meal_type,self.language,fun),
                'phone':fun.partner_id.phone,
                'maneger':translate_field(fun.manager_name_id ,self.language),
                'maneger_phone':fun.manager_name_id.phone,
                'remarks': fun.remarks,
                'notes':fun.notes
                })
                        
            for cat in fun.order_line:
                record = self.env['hop.recipes'].search([('product_id','=',cat.product_id.id)])
                product_id = False
                if record:
                    product_id = record
                else:
                    product_id = cat.product_id
                list.append({
                'product_id' : translate_field(product_id,self.language),
                'product_qty':cat.product_qty,
                'product_uom': cat.product_uom.name,
                'helper': cat.helper,
                'chief': cat.chief,
                'date': cat.date.strftime('%d-%m-%Y') if cat.date else '',
                'time': cat.time,
                'am_pm': cat.am_pm,
                'name': cat.name,
                'no_of_pax': cat.no_of_pax,
                'order_qty': cat.order_qty,
                'instruction': cat.instruction,
                'category_id' :translate_field(cat.category_id  ,self.language),
                'hospitality_ids' : cat.hospitality_ids.name,
                'shift_date' : cat.shift_date.strftime('%d-%m-%Y') if cat.shift_date else '',
                'shift_time' : f"{int(cat.shift_time):02d}:{int((cat.shift_time % 1) * 60):02d}",
                'remarks': cat.remarks,
                'price_subtotal': cat.price_subtotal,
                'location': location_field(cat.location,self.language,cat),
                'qty_cal_type':cat.qty_cal_type,
                'uom':cat.product_uom.name

                })
        
            party_list.update({'po_type':fun.po_type,'product_list':list})

            main.append(party_list)
        if not list:
            return
        return main
    def action_confirm(self):
        print("**************************************",self.env.ref('ct_function_v15.action_all_po_prints').report_action(self))
        return self.env.ref('ct_function_v15.action_all_po_prints').report_action(self)
    
    def  action_confirm_render_qweb_pdf(self):
        return  self.env.ref('ct_function_v15.action_all_po_prints')._render_qweb_pdf([self.id])