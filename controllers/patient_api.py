from odoo import http
from odoo.http import request
import json

class HospitalApi(http.Controller):
    
    def valid_response(self, data, status, pagination_info=None):
        response_body = {
            'data': data,
            'status': status,
        }
        if pagination_info:
            response_body['pagination_info'] = pagination_info
        return request.make_json_response(response_body, status=status)

    def invalid_response(self, error, status):
        return request.make_json_response({'error': error}, status=status)


    @http.route('/v1/patients', type='http', methods=['GET'], auth='none', csrf=False)
    def Get_all_patients(self):
        try:
            patients = request.env['hospital.patient'].sudo().search([])
            patients_list = []
            for patient in patients:
                patients_list.append({
                    'id': patient.id,
                    'name': patient.name,
                    'age': patient.age,
                    'gender': patient.gender,
                    'date_of_birth': patient.date_of_birth,
                })
            return self.valid_response(data=patients_list, status=200)
        except Exception as e:
            return self.invalid_response(error=str(e), status=400)

    @http.route('/v1/patient/<int:patient_id>', type='http', methods=['GET'], auth='none', csrf=False)
    def get_patient_data(self, patient_id):
        try:
            patient = request.env['hospital.patient'].sudo().browse(patient_id)
            if not patient.exists():
                return self.invalid_response(error='Patient Not Found', status=404)
            
            patient_vals = {
                'id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'gender': patient.gender,
            }
            return self.valid_response(data=patient_vals, status=200)
        except Exception as e:
            return self.invalid_response(error=str(e), status=400)

    @http.route('/v1/patient/newpatient', type='http', methods=['POST'], auth='none', csrf=False)
    def create_New_patient(self):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals.get('name'):
                return self.invalid_response(error='Name Is Required', status=400)

            new_patient = request.env['hospital.patient'].sudo().create({
                'name': vals.get('name'),
                'age': vals.get('age'),
                'gender': vals.get('gender'),
                'date_of_birth': vals.get('date_of_birth'),
            })
            
            respose_data = {
                'message': 'Patient created successfully',
                'id': new_patient.id,
                'name': new_patient.name,
            }
            return self.valid_response(data=respose_data, status=201)
        except Exception as e:
            return self.invalid_response(error=str(e), status=400)

    @http.route('/v1/patient/<int:patient_id>', type='http', methods=['PUT'], auth='none', csrf=False)
    def UpdatePatient(self, patient_id):
        try:
            patient = request.env['hospital.patient'].sudo().browse(patient_id)
            if not patient.exists():
                return self.invalid_response(error='Patient ID not found', status=404)

            args = request.httprequest.data.decode()
            vals = json.loads(args)
            patient.write(vals)

            response_data = {
                'message': 'Patient updated successfully',
                'id': patient.id,
                'new_name': patient.name,
                'new_age': patient.age
            }
            return self.valid_response(data=response_data, status=200)
        except Exception as e:
            return self.invalid_response(error=str(e), status=400)

    @http.route('/v1/patient/<int:patient_id>', type='http', methods=['DELETE'], auth='none', csrf=False)
    def deletepatient(self, patient_id):
        try:
            patient = request.env['hospital.patient'].sudo().browse(patient_id)
            if not patient.exists():
                return self.invalid_response(error='Patient ID not exist', status=400)

            patient.unlink()
            return self.valid_response(data={"message": "Patient Has Been Deleted successfully"}, status=200)
        except Exception as e:
            return self.invalid_response(error=str(e), status=400)