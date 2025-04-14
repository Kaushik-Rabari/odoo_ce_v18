from odoo import models, fields, api


class Booking(models.Model):
    _name="car.booking"
    _description= "this model store the details related to the Booking."
    _rec_name= "vehicle_id"

    customer_id = fields.Many2one("res.partner", string="Customer ID: ")
    vehicle_id = fields.Many2one("car.vehicle", string = "Customer Vehicle: ")
    service_ids = fields.Many2many("car.service.type", string="Services: ")
    booking_date = fields.Datetime("Booking Date")
    time_slot = fields.Datetime("Select Time Slots: ")
    # technician_id = fields.Many2one("res.employee", string="Select Technician")
    state = fields.Selection(
        [
            ("draft", "Draft"), 
            ("confirmed", "Confirmed"), 
            ("in_progress", "In Progress"), 
            ("done", "Done"), 
            ("cancelled", "Cancelled")
        ], string="States of the Records", default="draft")

    def button_draft(self):
        for records in self:
            records.write({"state": "draft"})

    def button_confirmed(self):
        for records in self:
            records.write({"state": "confirmed"})

    def button_in_progress(self):
        for records in self:
            records.write({"state": "in_progress"})

    def button_done(self):
        for records in self:
            records.write({"state": "done"})

    def button_cancelled(self):
        for records in self:
            records.write({"state": "cancelled"})
