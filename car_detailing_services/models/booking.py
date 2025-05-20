from odoo import models, fields, api
from odoo.addons.portal.models.portal_mixin import PortalMixin


class Booking(models.Model):
    _name="car.booking"
    _description= "this model store the details related to the Booking."
    _rec_name= "vehicle_id"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    customer_id = fields.Many2one("res.partner", string="Customer ID ")
    vehicle_id = fields.Many2one("car.vehicle", string = "Customer Vehicle ")
    service_ids = fields.Many2many("car.service.type", string="Services ")
    booking_date = fields.Datetime("Booking Date")
    time_slot = fields.Datetime("Select Time Slots ")
    technician_id = fields.Many2one("car.technician", string="Technician ")
    state = fields.Selection(
        [
            ("draft", "Draft"), 
            ("confirmed", "Confirmed"), 
            ("in_progress", "In Progress"), 
            ("done", "Done"), 
            ("cancelled", "Cancelled")
        ], string="States of the Records", default="draft")
    total_estimated_price = fields.Monetary("Estimated Total", compute="_compute_estimated_price", store=True)
    currency_id = fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id)
    service_count = fields.Integer("Service Count", compute="_compute_service_count")

    @api.depends("service_ids")
    def _compute_service_count(self):
        for rec in self:
            rec.service_count = len(rec.service_ids)

    @api.depends("service_ids.price")
    def _compute_estimated_price(self):
        for rec in self:
            rec.total_estimated_price = sum(rec.service_ids.mapped("price"))

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
