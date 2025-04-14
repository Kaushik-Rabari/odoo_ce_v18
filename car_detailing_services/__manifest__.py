{
    "name": "Cars Detailing and Servicing",
    "category": "Services/Automotive",
    "license": "LGPL-3",
    'sequence': 1,
    'summary': 'Manage car detailing, washing, and other automotive services',
    'description': """
        This module allows businesses to manage car detailing and service bookings, track service history,
        customer vehicles, pricing, and staff assignments.
    """,
    "author": "Kaushik Rabari",
    "images": ["static/description/image.jpg"],
    "depends": ['base', 'contacts', 'sale', 'sale_management', 'fleet'],
    "data": [
        "security/ir.model.access.csv",
        "views/vehicle_views.xml",
        "views/service_type_views.xml",
        "views/booking_views.xml",
    ],
    "installable": True,
    "application": True,
}
