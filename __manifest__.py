{
    "name": "Hospital Management System",
    "author": "Elsayed Ehab",
    "version": "17.0.1.0.0",
    "category": "Medical",
    "summary": "Hospital Records, Patients, and REST API Integration",
    "description": """
        Manage your hospital efficiently:
        - Patient Records & Medical History
        - Appointment Scheduling
        - Doctor Management
        - Prescription & Treatments
        - Invoicing & Payments
        - REST API for Mobile/Web integration
    """,
    "depends": [
        'base', 
        'mail',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/patient_view.xml',
        'views/appointment_view.xml',
        'views/prescription_view.xml',   
        'views/menu.xml',                
    ],
    'assets': {
        'web.assets_backend': [
            'hospital_management/static/src/components/patientCard/patientCard.css',
            'hospital_management/static/src/components/patientCard/patientCard.js',
            'hospital_management/static/src/components/patientCard/patientCard.xml',
            
            
        ],
    },
    'images': ['static/description/icon.png'],
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}