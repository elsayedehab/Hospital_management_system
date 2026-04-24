from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date

class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _description = 'Hospital Appointment'
    _rec_name = "appointment_serial" # يفضل السيريال يكون هو الـ Name
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- Basic Fields ---
    patient_id = fields.Many2one('hospital.patient', string="Patient", tracking=True)
    appointment_serial = fields.Char(string="Appointment ID", readonly=True, default=lambda self: _('New'))
    appointment_time = fields.Date(string="Appointment Time", default=fields.Date.context_today)
    booking_time = fields.Date(string="Booking Date", default=fields.Date.context_today, readonly=True)
    
    # --- Patient Info (Related) ---
    age = fields.Integer(string="Age", related='patient_id.age', readonly=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', related='patient_id.gender', readonly=True)

    # --- Status Fields ---
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid')
    ], string="Payment Status", compute='_compute_payment_state', store=True, tracking=True)

    # --- Relational Fields ---
    invoice_id = fields.Many2one('account.move', string="Related Invoice", readonly=True)
    patient_appointment_prescription_id = fields.One2many('patient.prescription', 'appointment_id')
    history_ids = fields.One2many('appointment.history', 'appointment_id', string='History')
    prescription_count = fields.Integer(string="Prescription Count", compute="compute_prescription_count")

    # --- Constraints & Logic ---

    @api.depends('invoice_id.payment_state')
    def _compute_payment_state(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.payment_state in ['paid', 'in_payment']:
                rec.payment_state = 'paid'
            else:
                rec.payment_state = 'not_paid'

    @api.model
    def create(self, vals):
        if vals.get('appointment_serial', _('New')) == _('New'):
            vals['appointment_serial'] = self.env['ir.sequence'].next_by_code('hospital.appointment.sequence') or _('New')
        return super(HospitalAppointment, self).create(vals)

    def compute_prescription_count(self):
        for rec in self:
            rec.prescription_count = self.env['patient.prescription'].search_count([
                ('appointment_id', '=', rec.id)
            ]) if rec.id else 0

    # --- Actions ---
    def action_create_invoice(self):
        for rec in self:
            if not rec.invoice_id:
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': rec.patient_id.partner_id.id,
                    'invoice_line_ids': [(0, 0, {
                        'name': _('Consultation Fees: %s') % rec.appointment_serial,
                        'quantity': 1,
                        'price_unit': 500.0,
                    })],
                })
                rec.invoice_id = invoice

    def action_done(self):
        for rec in self:
            if rec.payment_state != 'paid':
                raise ValidationError(_("Access Denied: Appointment cannot be completed until the consultation fee is paid."))
            
            rec.create_history(rec.state, 'done', "Appointment completed successfully")
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.create_history(rec.state, 'cancel', "Patient cancelled or missed the slot")
            rec.state = 'cancel'

    def action_reset_to_draft(self):
        for rec in self:
            rec.create_history(rec.state, 'draft', "Reset for corrections")
            rec.state = 'draft'

    # --- View Actions ---
    def action_view_prescriptions(self):
        return {
            'name': 'Prescriptions',
            'res_model': 'patient.prescription',
            'view_mode': 'tree,form',
            'domain': [('appointment_id', '=', self.id)],
            'context': {'default_appointment_id': self.id},
            'target': 'current',
            'type': 'ir.actions.act_window'
        }

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

    # --- Helpers & Cron ---
    def create_history(self, old_state, new_state, reason):
        for rec in self:
            self.env['appointment.history'].create({
                'appointment_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason,
            })

    @api.model
    def cancel_passed_appointments(self):
        today = fields.Date.today()
        passed_appointments = self.search([
            ('appointment_time', '<', today),
            ('state', '=', 'draft')
        ])
        for rec in passed_appointments:
            rec.create_history('draft', 'cancel', "Auto-cancelled: Appointment date has passed.")
            rec.state = 'cancel'