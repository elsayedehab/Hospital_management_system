from odoo import fields,models,api, _
from datetime import date, timedelta


class PatientPrescription(models.Model):
    _name="patient.prescription"
    _description = "Patient Prescription"
    

    prescription_serial=fields.Char(string="prescription serial", readonly=True, index=True, required=True, default=lambda self: _('New Prescription'))
    prescription_date=fields.Date(string='Date of Formulation', default=date.today())

    patient_id=fields.Many2one(related='appointment_id.patient_id') #هنا عشان نوفر علي المستخدم بدل ما يختار الموعد والمريض هنا المريض بيتحدد علي حسب الميعاد بتاعه

    appointment_id=fields.Many2one('hospital.appointment')

    appointment_id_name=fields.Char('Appointment Name', related='appointment_id.appointment_serial', readonly=True)

    patient_line_id=fields.One2many('patient.prescription.line', 'prescription_id')

    @api.model
    
    def create(self,vals):
        if vals.get('prescription_serial',_('New Prescription')) == _('New Prescription'):
            vals['prescription_serial']=self.env['ir.sequence'].next_by_code('patient.appointment.prescription.sequence') or _('New Prescription')

        res = super().create(vals)
        return res   




class PatientPrescriptionLine(models.Model):

    _name="patient.prescription.line"

    prescription_id=fields.Many2one('patient.prescription')

    prescription_id_name=fields.Char(related="prescription_id.prescription_serial",string='Prescription_ID')

    medicine_trade_name = fields.Char(string="Trade Name of Medicine")

    therapeutic_regimen = fields.Char(string="Therapeutic Regimen of Medicine")

