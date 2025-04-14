from odoo import fields, models, api


class ServiceType(models.Model):
    _name= "car.service.type"
    _description= "this model store the details related to the service types which we provides."

    service_type = fields.Selection(
        [
            ("exterior_wash", "Exterior Wash"), 
            ("interior_detailing", "Interior Detailing"), 
            ("ceramic_coating", "Ceramic Coating"), 
            ("engine_bay_cleaning", "Engine Bay Cleaning")
        ], string="Select Service")
    name = fields.Char("Name: ")
    description = fields.Html("Description: ")
    price = fields.Integer("Price: ")
    duration = fields.Char("Duration/Timing :")
    category = fields.Char("Category :")
