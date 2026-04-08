from odoo import fields, models, api
from datetime import date 
from odoo.exceptions import UserError

class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _description = "Hospital Patient"
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    partner_id = fields.Many2one('res.partner', string="Contact Info")
    phone = fields.Char(string="Phone", related='partner_id.phone', readonly=True)
    email = fields.Char(string="Email", related='partner_id.email', readonly=True)

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

    appointment_count = fields.Integer(compute='_compute_appointment_count', string='Appointment Count')

    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['hospital.appointment'].search_count([
                ('patient_id', '=', rec.id)
            ])

    def action_view_appointments(self):
        return {
            'name': 'Appointments',
            'res_model': 'hospital.appointment',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'target': 'current',
            'type': 'ir.actions.act_window',
        
        }            