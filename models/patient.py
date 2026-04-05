from odoo import fields, models, api
from datetime import date 
from odoo.exceptions import UserError

class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _description = "Hospital Patient"
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    name = fields.Char(string="Patient Name", tracking=True)
    age = fields.Integer(string="Patient Age", compute="_compute_age", store=True, tracking=True)
    date_of_birth = fields.Date(string="Date Of Birth", tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender", tracking=True, default='male')
    active=fields.Boolean(string="Active",default=1, tracking=True)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = date.today()
                if rec.date_of_birth > today:
                    raise UserError("Sorry, birth date cannot be in the future!")

                age = today.year - rec.date_of_birth.year
                if (today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day):
                    age -= 1
                
                rec.age = age
            else:
                rec.age = 0