from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError,RedirectWarning
from datetime import datetime


class DoneActivity(models.TransientModel):
    _name = 'done.activity'
    _description = "Done Activity"

    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(DoneActivity, self).default_get(fields)
        for lead_id in self.env['hop.meeting'].browse(context.get('active_ids')):
            res['lead_id'] = lead_id.id
        return res

    lead_id = fields.Many2one('hop.meeting', 'Contact')
    description = fields.Text("Description", required=True)
    next_activity_id = fields.Many2one('mail.activity.type', 'Next Activity')
    date_action_data = fields.Date('Date')
    title_action = fields.Char('Activity Detail')

    @api.onchange('date_action_data')
    def _onchange_date_action_data(self):
        if self.date_action_data and self.date_action_data < datetime.now().date():
            raise ValidationError("Can't Select Previous Date!!!!")
   

    def done_activity_description(self):
        if self.lead_id.next_activity_id:
            self.env['next.activity.log'].create({
                'crm_next_activity_id': self.lead_id.id,
                'next_activity_id': self.lead_id.next_activity_id.id,
                'date_action_data': self.lead_id.date_action_data,
                'title_action': self.lead_id.title_action,
                'description': self.description,
            })
            self.lead_id.next_activity_id = self.next_activity_id.id
            if self.date_action_data:
                self.lead_id.date_action_data = self.date_action_data
            else:
                pass
            self.lead_id.title_action = self.title_action
            self.lead_id.is_activity_done_today = False

