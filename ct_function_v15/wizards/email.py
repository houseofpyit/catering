from odoo import models, fields
import base64

class SendEmailWhatsapp(models.TransientModel):
    _name='hop.send.email.whatsapp'

    email = fields.Char(string='Email')
    wpno = fields.Char(string='Whatsapp Number')
    pno = fields.Char(string='Phone Number')
    
    def action_send(self):
        sale = self.env[self.env.context.get('active_model')].browse(self.env.context['active_ids'])
        if sale:
            sale.send_email = True
            if self.env.context.get('active_model') == 'sale.order':
                # sale.state = 'sale'
                sale['confirm_date']=fields.Date.today()
            # else :
                # sale.state='purchase'

        if self.email:
            self.ensure_one()
            template_id = self.env.ref('ct_function_v15.mail_template_custom_sale',False)
            # lang = self.env.context.get('lang')
            # template = self.env['mail.template'].browse(template_id)

            so_pdf = self.env.ref('sale.action_report_saleorder').sudo()._render_qweb_pdf([sale.id])
            data = base64.b64encode(so_pdf[0])
            attach_vals = {
                'name':'%s.pdf' % (sale.name),
                'type': 'binary',
                'datas': data,
            }
            report_id = self.env['ir.attachment'].create(attach_vals)

            ctx = dict(
            default_model= 'sale.order',
            default_res_id= sale.id,
            default_use_template= bool(template_id),
            default_template_id= template_id.id,
            default_attachment_ids= [(report_id.id)],
            default_composition_mode= 'comment',
            force_email= True,
            )
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }
            
            # so_pdf = self.env.ref('sale.action_report_saleorder').sudo()._render_qweb_pdf([sale.id])
            # data = base64.b64encode(so_pdf[0])
            # attach_vals = {
            #     'name':'%s.pdf' % (sale.name),
            #     'type': 'binary',
            #     'datas': data,
            # }
            # report_id = self.env['ir.attachment'].create(attach_vals)
            # mail_dict = {
            #             "subject": 'Send Mail',
            #             # "email_from": smtp_user_rec.smtp_user,
            #             "email_to": self.email,
            #             "body_html": "<br>"+
            #             "<span>Hello  </span>" + " - " + 
            #             # "<p>I Hope this email finds you well. I am writing to kindly remind you of the Block Product, heres the Detail :</p>"+ 
            #             # "<p><b>Project : </b>"+self.project_id.name + "</p>" +
            #             "<p>With Warm Regards, </p>",
            #             "attachment_ids": [(report_id.id)],
            #             }
            # print("..............................mail_dict",mail_dict)
            # if mail_dict:
            #     mail_create = self.env['mail.mail'].create(mail_dict)
            #     mail_create.send()
