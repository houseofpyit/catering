from odoo import api, models, fields, _
import os
import base64
import requests
import re
from odoo.exceptions import UserError,ValidationError,RedirectWarning
import shutil
import datetime


class InheritPurchaseOrder(models.Model):
    _inherit = "purchase.order"


    def send_by_whatsapp(self):
        try:
            if len(self) > 3:
                raise UserError("You can only send up to 3 records at a time.")
            for purcese in self:
                if not purcese.partner_id.phone:
                    raise UserError('Venord whatsapp numbe is required')
                if not purcese.company_id.whatsapp_user_id and not purcese.company_id.whatsapp_pwd:
                    raise UserError('Whatsapp ID and Password is required')
                pdf = purcese.env.ref('ct_function_v15.action_po_print_format')._render_qweb_pdf(purcese.id)[0]
                pdf = base64.b64encode(pdf).decode()
                file_name = str(purcese.id) + '_' + str(purcese.partner_id.name) + '.pdf'
                pdf_name = str(purcese.id) + '_' + str(purcese.partner_id.name)


                path = '/var/www/html/'
                today_date = datetime.datetime.now().strftime('%Y-%m-%d')
                today_folder = os.path.join(path, today_date)

                # Create today's folder if it doesn't exist
                if not os.path.exists(today_folder):
                    os.makedirs(today_folder)
                    print(f"Created folder: {today_folder}")

                # Delete all previous date folders
                for folder_name in os.listdir(path):
                    folder_path = os.path.join(path, folder_name)
                    if os.path.isdir(folder_path) and folder_name != today_date:
                        try:
                            shutil.rmtree(folder_path)
                            print(f"Deleted folder: {folder_path}")
                        except Exception as e:
                            print(f"Error deleting folder {folder_path}: {e}")

                # Define the file name and file path
                # file_name = pdf_name  # Replace this with your actual file name logic
                file_path = os.path.join(today_folder, file_name)

                # Decode and write the PDF file
                with open(file_path, "wb") as pdf_file:
                    pdf_file.write(base64.b64decode(pdf))
                    print(f"File written to: {file_path}")
                # # file_name = f"{pdf_name}" 
                # file_path = os.path.join(path, file_name)

                # with open(file_path, "wb") as pdf_file:
                #     pdf_file.write(base64.b64decode(pdf))
                # phone_number = re.sub(r'\D', '', self.partner_id.phone)
                # phone_number = re.sub(r'^\+\d{2}\s*', '', phone_number)
                url = f"http://bhashsms.com/api/sendmsg.php?user={purcese.company_id.whatsapp_user_id}&pass={purcese.company_id.whatsapp_pwd}&sender=BUZWAP&phone={purcese.partner_id.phone}&text=purchase_order_temp&priority=wa&stype=normal&htype=document&fname={pdf_name}&url=https://amazeimage.oretta.in/{today_date}/{file_name}"
                print("=====================",url)
                payload={}
                headers = {}

                response = requests.request("GET", url, headers=headers, data=payload)
                print("******response********",response)
                # rm_path = path+file_name
                # if os.path.exists(rm_path):
                #     os.remove(rm_path)
        except Exception as e:
            raise UserError(e)

