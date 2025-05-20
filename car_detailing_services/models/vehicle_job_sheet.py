from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.addons.portal.models.portal_mixin import PortalMixin


class VehicleJobSheet(models.Model):
    _name="car.job.sheet"
    _description = 'Vehicle Service Job Sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char("Job Sheet no.: ", required=True, copy=False, readonly=True, default="New")
    booking_id = fields.Many2one("car.booking", string="Booking Reference", required=True)
    customer_id = fields.Many2one("res.partner", string="Customer", related="booking_id.customer_id", store=True)
    vehicle_id = fields.Many2one(related="booking_id.vehicle_id", string="Vehicle", readonly=True)
    technician_id = fields.Many2one("car.technician", string="Assigned Technician: ")
    start_time = fields.Datetime("Start Time")
    end_time = fields.Datetime("End Time")
    tasks_done = fields.Text("Tasks Done/ Notes")
    service_ids = fields.Many2many(related="booking_id.service_ids", string="Services: ")
    part_line_ids = fields.One2many("car.job.part.line", "job_sheet_id", string="Spare Parts Used")
    image_before = fields.Binary("Before Service Image", attachment=True)
    image_after = fields.Binary("After Service Image", attachment=True)
    location_id = fields.Many2one("stock.location", string="Source Location", default=lambda self: self.env.ref("stock.stock_location_stock"))
    stock_deducted = fields.Boolean("Stock Deducted", default=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ], string="Status", default="draft"
    )
    # labour_charge = fields.Float("Labour Charge: ")
    service_cost = fields.Float("Service Cost: ", )
    parts_total = fields.Float("Parts Cost", compute="_compute_parts_total")
    total_amount = fields.Float("Total Amount: ", compute="_compute_total_amount", readonly=True)
    related_user = fields.Many2one('res.users', string="Related User: ", default=lambda self: self.env.user.id)
    invoice_ids = fields.One2many("car.invoice", "job_sheet_id", string="Invoices")
    feedback_ids = fields.One2many("car.job.sheet.feedback", "job_sheet_id", string="Customer Feedback")

    @api.depends("part_line_ids.line_subtotal")
    def _compute_parts_total(self):
        print("\n_compute_parts_total - Called\n")
        for sheet in self:
            sheet.parts_total = sum(line.line_subtotal for line in sheet.part_line_ids)

    @api.depends("parts_total", "total_amount")
    def _compute_total_amount(self):
        print("\n_compute_total_amount - Called\n")
        for record in self:
            record.total_amount = record.parts_total + record.service_cost

    @api.constrains("end_time", "start_time")
    def _check_times(self):
        print("\n_check_times - Called\n")
        for record in self:
            if record.end_time and record.start_time and record.end_time < record.start_time:
                raise ValidationError("End time must be after start time.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.vehicle_id and record.end_time:
                vals.vehicle_id.last_service_date = vals.end_time.date()
                print(f"\n[CREATE] Updated Vehicle ({vals.vehicle_id.vehicle_model}) last_service_date to: {vals.vehicle_id.last_service_date}\n")
            record = super().create(vals_list)
            return record

    def write(self, vals):
        result = super().write(vals)
        for record in self:
            if 'end_time' in vals or 'vehicle_id' in vals:
                if record.vehicle_id and record.end_time:
                    record.vehicle_id.last_service_date = record.end_time.date() or fields.Date.today()
                    print(f"\n[WRITE] Updated Vehicle ({record.vehicle_id.vehicle_model}) last_service_date to: {record.vehicle_id.last_service_date}\n")
            return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("car.job.sheet") or "New"
        return super().create(vals_list)

    def action_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'list,form',
            'res_model': 'car.invoice',
            'domain': [('job_sheet_id', '=', self.id)],
            'context': {'default_job_sheet_id': self.id},
        }

    # # To show this job on the portal dashboard (/my/home)
    # def _get_portal_return_action(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'My Job Sheets',
    #         'res_model': 'car.job.sheet',
    #         'view_mode': 'list,form',
    #         'domain': [('id', 'in', self.ids)],
    #     }

    # def get_portal_url(self, suffix=None, report_type=None, download=None):
    #     self.ensure_one()
    #     url = f"/my/job/{self.id}/feedback"
    #     return url

    def action_mark_done(self):
        for sheet in self:
            for part in sheet.part_line_ids:
                if part.product_id.type != "product":
                    continue # Skip consumables/services
                
                qty_available = part.product_id.qty_available
                if qty_available < part.quantity:
                    raise UserError(f"Not Enough stock for {part.product_id.name}. Only {qty_available} available.")

                # Create stock move
                self.env["stock.move"].create({
                    'name': f'Job Sheet: {sheet.name or "Unknown"} - {part.product_id.name}',
                    'product_id': part.product_id.id,
                    'product_uom_qty': part.quantity,
                    'product_uom': part.product_id.uom_id.id,
                    'location_id': sheet.location_id.id, # from where
                    'locaion_dest_id': sheet.customer_id.property_stock_customer.id, # to customer
                    'state': 'confirmed',
                })._action_confirm()._action_assign()._action_done()
            
            sheet.stock_deducted = True
            sheet.state = 'done'

class VehicleJobParts(models.Model):
    _name="car.job.part.line"
    _description = "Spare Parts Used in Job Sheet"

    job_sheet_id = fields.Many2one("car.job.sheet", string="Job Sheet: ")
    product_id = fields.Many2one("product.product", string="Part/Product")
    quantity = fields.Float("Quantity", default=1.0)
    uom_id = fields.Many2one(related="product_id.uom_id", string="Unit of Measure", readonly=True)
    price_unit = fields.Float(related="product_id.lst_price", string="Unit Price", readonly=True)
    line_subtotal = fields.Float("Subtotal", compute="_compute_line_subtotal", store=True)

    @api.depends("quantity", "price_unit")
    def _compute_line_subtotal(self):
        print("\n_compute_line_subtotal - Called\n")
        for line in self:
            line.line_subtotal = line.quantity * line.price_unit


class CarJobSheetFeedback(models.Model):
    _name= "car.job.sheet.feedback"
    _description= "Feedback & Rating for Job Sheet"

    job_sheet_id = fields.Many2one("car.job.sheet", string="Job Sheet", required=True, ondelete="cascade")
    customer_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    rating = fields.Selection([
        ('1', '★☆☆☆☆'),
        ('2', '★★☆☆☆'),
        ('3', '★★★☆☆'),
        ('4', '★★★★☆'),
        ('5', '★★★★★'),
    ], string="Rating", required=True)
    comments = fields.Text(string="Comments")
    date = fields.Datetime(string="Feedback Date", default=fields.Datetime.now, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "customer_id" not in vals:
                job = self.env["car.job.sheet"].browse(vals.get("job_sheet_id"))
                vals["customer_id"] = job.booking_id.customer_id.id
            return super().create(vals)
