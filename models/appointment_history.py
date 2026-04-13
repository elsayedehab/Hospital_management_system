from odoo import fields,models
from datetime import date


class AppointmentHistory(models.Model):

    _name="appointment.history"
    _description="AAppointment History"

    appointment_id=fields.Many2one('hospital.appointment',string="Apointment")
    user_id=fields.Many2one('res.users',string="Changed By", default=lambda self: self.env.user)
    changed_date=fields.Datetime(string="Changed Date", default=fields.Datetime.now)
    old_state=fields.Char(string="Old State")
    new_state=fields.Char(string="New State")
    reason=fields.Text(string="Reason")