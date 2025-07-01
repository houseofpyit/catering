from odoo import models, fields, _
class HopPartyWiseReport(models.Model):
    _name = "hop.party.wise.report"
    
    function_id = fields.Many2one('hop.function',string="Function")
    party_name_id = fields.Many2one('res.partner',string="Party Name",tracking=True,domain=[('is_customer','=',True)])
    mobile_num = fields.Char(string="Mobile Number",tracking=True)
    fuction_name_id = fields.Many2one('hop.function.mst',string="Function Name",tracking=True)
    date = fields.Date(string="Function Date",default=fields.Date.context_today,tracking=True)
    emergency_contact = fields.Text(string="Emergency Contact")
    remarks = fields.Text(string="Remarks",tracking=True)
    manager_name_id = fields.Many2one('res.partner',string="Manager Name",domain=[('is_vender','=',True)] ,tracking=True)
    meal_type = fields.Selection([('early_morning_tea','Early Morning Tea'),('breakfast','Breakfast'),('brunch','Brunch'),('mini_meals','Mini Meals'),('lunch','Lunch'),('hi-tea','HI-TEA'),('dinner','Dinner'),('late_night_snacks','Late Night Snacks'),('parcel','Parcel')],string="Meal Type",tracking=True)
    no_of_pax = fields.Integer(string="No Of Pax",tracking=True)
    time = fields.Float(string="Time",tracking=True)
    am_pm = fields.Selection([('am','AM'),('pm','PM')],string="AM-PM",tracking=True)
    venue_address = fields.Text('Venue Address')
    company_id = fields.Many2one('res.company',string="Company Name",default=lambda self:self.env.company.id)
   
