from odoo import api, models, fields, _
from odoo.tests import Form, tagged
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date


class InheritCalendar(models.Model):
    _inherit = "calendar.event"

    fuction_id = fields.Many2one('hop.function',string="Function",tracking=True) 
    lead_id = fields.Many2one('hop.lead',string="Lead",tracking=True) 
    fuction_name_id = fields.Many2one('hop.function.mst',string="Function Name",tracking=True)
    mobile_num = fields.Char(string="Mobile Number",tracking=True)