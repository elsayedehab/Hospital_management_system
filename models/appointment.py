from odoo import fields,models,api, _


class HospitalAppointment(models.Model):

    _name="hospital.appointment"
    _description='Hospital Appointment'
    _rec_name = "appointment_time"

    _inherit=['mail.thread','mail.activity.mixin']


    patient_id=fields.Many2one('hospital.patient',string="Patient_Name", tracking=True)

    age=fields.Integer(string="Age", related='patient_id.age', readonly=True)

    gender=fields.Selection([
        ('male','Male'),
        ('female','Female'),
        ('other','Other'),
    ], string='Gender', related='patient_id.gender', readonly=True)

    appointment_time=fields.Date(string="Appointment Time", default=fields.Datetime.now)

    booking_time=fields.Date(string="Booking_Date", default=fields.Date.context_today, readonly=True)


    patient_appointment_preciption_id=fields.One2many('patient.prescription','appointment_id')

    appointment_serial = fields.Char(string="Appointment ID", readonly=True, default=lambda self: _('New_Apppointment'))

    @api.model
    def create(self, vals):
        if vals.get('appointment_serial', _('New_Apppointment')) == _('New_Apppointment'):
            vals['appointment_serial'] = self.env['ir.sequence'].next_by_code('hospital.appointment.sequence') or _('New_Apppointment')
        res = super().create(vals)
        return res


    presciption_count=fields.Integer(string="Preciptions", compute="compute_presciption_count")

    def compute_presciption_count(self):
        for rec in self:
            if not rec.id:
                rec.presciption_count = 0
                continue
            
            rec.presciption_count = self.env['patient.prescription'].search_count([
                ('appointment_id', '=', rec.id)
            ])



    def action_view_presciptions(self):
        return{
            'name' :'Preciptions',
            'res_model':'patient.prescription',
            "view_mode":'tree,form',
            'domain': [('appointment_id', '=', self.id)],
            'context': {'default_appointment_id': self.id}, 
            'target' : 'current',
            'type' :'ir.actions.act_window'
        }    