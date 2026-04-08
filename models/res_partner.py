from odoo import fields,models


class ResPartner(models.Model):
    _inherit="res.partner"


    last_appointment_date=fields.Date(string='Last Appointment', compute="_compute_Last_Appointment")


    def _compute_Last_Appointment(self):
        for rec in self:

            last_app=self.env['hospital.appointment'].search([
                ('patient_id.partner_id', '=', rec.id)
            ], limit=1, order='appointment_time desc')

            rec.last_appointment_date=last_app.appointment_time if last_app else False
