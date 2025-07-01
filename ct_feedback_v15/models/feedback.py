from odoo import models,fields,api
from datetime import datetime, date ,timedelta

class CtFeedback(models.Model):
    _name = "ct.feedback"

    party_name_id = fields.Many2one('res.partner',string="Party Name",tracking=True)
    function_id = fields.Many2one('hop.function',string="Function",tracking=True) 
    date = fields.Date(string="Function Date",tracking=True)
    venue_address = fields.Text('Venue Address')
    time = fields.Float(string="Time",tracking=True)
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    emergency_contact = fields.Text(string="Emergency Contact")
    manager_name_id = fields.Many2one('res.partner',string="Manager Name",tracking=True)
    mobile_num = fields.Char(string="Mobile Number",tracking=True)
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type",tracking=True)
    no_of_pax = fields.Integer(string="No Of Pax",tracking=True)
    remarks = fields.Text(string="Remarks",tracking=True)
    phone = fields.Char(string="Whatsapp Mo.")
    guest_suggest = fields.Char(string="Guest Suggestion")
    extra_item =  fields.Text(string="Extra Items/Services")
    note = fields.Html("WE CONFIRED RECEIVED FOOD/DECORATION/ALLIED SERVICES AS PER OUR ORDER")
    feedback_id = fields.Many2one('ct.feedback',string="Feedback")

    AVAILABLE_PRIORITIES = [
    ('0', 'Poor'),
    ('1', 'Fair'),
    ('2', 'Good'),
    ('3', 'Excellent')
]
 
    food_quality = fields.Selection(AVAILABLE_PRIORITIES, select=True,string="Food Quality")
    hospitality = fields.Selection(AVAILABLE_PRIORITIES, select=True,string="Hospitality")
    cleanliness_and_hygine = fields.Selection(AVAILABLE_PRIORITIES, select=True,string="Cleanliness And hygine")
    staff_friendliness = fields.Selection(AVAILABLE_PRIORITIES, select=True,string="Staff friendliness")
    overall_satisfaction =  fields.Selection(AVAILABLE_PRIORITIES, select=True,string="Overall satisfaction")
    overall_decoration = fields.Selection(AVAILABLE_PRIORITIES, select=True,string="Overall Decoration(If Any)")


    @api.onchange('function_id')
    def _onchange_function_id(self):
        if self.function_id :
            self.date = self.function_id.date,
            self.party_name_id = self.function_id.party_name_id.id,
            