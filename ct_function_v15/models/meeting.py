from odoo import api, models, fields
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class hop_meeting(models.Model):
    _name = "hop.meeting"
    _description = "Meeting"

    name = fields.Char(string="Name",required=True)
    date = fields.Date(string="Date",default=fields.Date.context_today)
    note = fields.Text(string="Note")
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
    mobileno = fields.Char(string="Mobile No.")
    time = fields.Float(string="Time")
    next_activity_id = fields.Many2one('mail.activity.type', 'Next Activity')
    date_action_data = fields.Date('Date',store=True)
    title_action = fields.Char('Activity Detail')
    next_activity_log_id = fields.One2many('next.activity.log', 'crm_next_activity_id', string="Next Activity Log Id")

    is_activity_done_today = fields.Boolean(compute='_compute_is_activity_done_today')

    @api.depends('date_action_data')
    def _compute_is_activity_done_today(self):
        for lead in self:
            if lead.date_action_data:
                if lead.date_action_data <= datetime.now().date():
                    lead.is_activity_done_today = True
                else:
                    lead.is_activity_done_today = False
            else:
                lead.is_activity_done_today = False

    @api.onchange('date_action_data')
    def _onchange_date_action_data(self):
        if self.date_action_data and self.date_action_data < datetime.now().date():
            raise ValidationError("Can't Select Previous Date!!!!")
   
   
class NextActivityLog(models.Model):
    _name = 'next.activity.log'
    _description = "Next Activity Log"

    crm_next_activity_id = fields.Many2one('hop.meeting', 'CRM Next Activity')
    partner_id = fields.Many2one('res.partner', 'Customer')
    next_activity_id = fields.Many2one('mail.activity.type', 'Activity')
    date_action_data = fields.Date('Date')
    title_action = fields.Char('Activity Detail')
    description = fields.Text("Description")
