from odoo import fields,models,api, _
from datetime import date


class HospitalAppointment(models.Model):

    _name="hospital.appointment"
    _description='Hospital Appointment'
    _rec_name = "appointment_time"

    _inherit=['mail.thread','mail.activity.mixin']


    patient_id = fields.Many2one('hospital.patient', string="Patient", tracking=True, states={'draft': [('readonly', False)]})    

    state = fields.Selection([
        ('draft', 'Draft'),      
        ('done', 'Done'),        
        ('cancel', 'Cancelled'), 
    ], string='Status', default='draft', tracking=True)

    age=fields.Integer(string="Age", related='patient_id.age', readonly=True)

    gender=fields.Selection([
        ('male','Male'),
        ('female','Female'),
        ('other','Other'),
    ], string='Gender', related='patient_id.gender', readonly=True)

    appointment_time = fields.Date(string="Appointment Time", default=fields.Date.context_today)
    booking_time=fields.Date(string="Booking_Date", default=fields.Date.context_today, readonly=True)


    patient_appointment_preciption_id=fields.One2many('patient.prescription','appointment_id')

    appointment_serial = fields.Char(string="Appointment ID", readonly=True, default=lambda self: _('New_Apppointment'))


    history_ids = fields.One2many('appointment.history', 'appointment_id', string='History')
    
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




    def action_check_today_appointments(self):

            today_date=date.today()
            appiontments_today=self.search([
                ('appointment_time', '=', today_date),
                ('state', '=', 'draft')

            ])
            for rec in appiontments_today:
                rec.message_post(body="This Appointment is Today")    

    def create_history(self,old_state,new_state,reason):
        for rec in self:
            self.env['appointment.history'].create({
                'appointment_id':rec.id,
                'old_state':old_state,
                'new_state':new_state,
                'reason':reason,
            })        

    def action_done(self):
        for rec in self:
            rec.create_history(rec.state, 'done', "Appointment completed successfully")
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.create_history(rec.state, 'cancel', "Patient cancelled or missed the slot")
            rec.state = 'cancel'

    def action_reset_to_draft(self):
        for rec in self:
            rec.create_history(rec.state, 'draft', "Reset for corrections")
            rec.state='draft'       


    
    def action_view_history(self):
        return {
            'name': 'Appointment History',
            'type': 'ir.actions.act_window',
            'res_model': 'appointment.history',
            'view_mode': 'tree',
            'domain': [('appointment_id', '=', self.id)],
            'context': {'default_appointment_id': self.id},
            'target': 'current',
        }   

    @api.model
    def cancel_passed_appointmemnts(self):
        today=fields.Date.today()

        passed_appointments=self.search([
            ('appointment_time','<',today),
            ('state','=','draft')
        ])   

        for rec in passed_appointments:
            rec.create_history('draft','cancel',"Auto-cancelled: Appointment date has passed.")
            rec.state='cancel'