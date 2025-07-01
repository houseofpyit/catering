from odoo import api, models, fields

class HopCancelReport(models.Model):
    _name = "hop.cancel.report"

    party_id = fields.Many2one('res.partner',string="Party") 
    date = fields.Date(string="Function Date")
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type",tracking=True)
    cancel_type = fields.Selection([('Event Inquiry','Event Inquiry'),('Menu Planner','Menu Planner'),('Confirm Orders','Confirm Orders')],string="Cancel Department",tracking=True)
    no_of_pax = fields.Integer(string="No Of Pax")
    venue_address = fields.Text('Venue Address')
    reason = fields.Text('Reason')
