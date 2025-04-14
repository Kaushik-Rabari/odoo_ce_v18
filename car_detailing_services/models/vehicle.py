from odoo import models, fields, api


class Vehicle(models.Model):
    _name = "car.vehicle"
    _description = "this model stored customers vehicles details"
    _rec_name = "vehicle_model"

    owner_id = fields.Many2one("res.partner")
    vehicle_model = fields.Char("Vehicle Model: ")
    vehicle_company = fields.Char("Vehicle Company: ")
    vehicle_plate_no = fields.Char("Vehicle Plate No.: ")
    vehicle_year = fields.Char("Vehicle Year: ")
    vehicle_color = fields.Char("Vehicle Color: ")
    vehicle_image = fields.Binary()
