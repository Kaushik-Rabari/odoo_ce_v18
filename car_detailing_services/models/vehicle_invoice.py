from odoo import models, fields, api
from datetime import datetime
from odoo.addons.portal.models.portal_mixin import PortalMixin


class VehicleInvoice(models.Model):
    _name="car.invoice"
    _description="Vehicle Service Invoice"
    _rec_name="job_sheet_id"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    invoice_number= fields.Char("Invoice no.: ", readonly=True, default="New")
    job_sheet_id= fields.Many2one("car.job.sheet", string="Job Sheet", required=True)
    booking_id= fields.Many2one(related="job_sheet_id.booking_id", string="Booking: ", readonly=True)
    vehicle_id= fields.Many2one(related="job_sheet_id.vehicle_id", string="Vehicle: ", readonly=True)
    customer_id= fields.Many2one(related="booking_id.customer_id", string="Customer: ", readonly=True)

    service_amount= fields.Monetary("Service Cost", currency_field="currency_id")
    parts_amount= fields.Monetary("Parts Cost", currency_field="currency_id")
    total_amount= fields.Monetary("Total Cost", compute="_compute_total_amount")
    currency_id= fields.Many2one("res.currency", default=lambda self:self.env.company.currency_id)

    invoice_date= fields.Date("Invoice Date: ", default=fields.Date.today)
    print_count= fields.Integer(string="Print Count", default=0)

    # state = fields.Selection(
    #     [
    #         ("draft", "Draft"),
    #         ("confirmed", "Confirmed"),
    #         ("cancelled", "Cancelled"),
    #     ], string="Status", default="draft"
    # )
    payment_status = fields.Selection(
        [
            ("unpaid", "Unpaid"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
        ], default="unpaid", string="Payment Status", tracking=True
    )

    # payment_status_time = fields.Datetime(string="Status Changed At", default=fields.Datetime.now)
    # payment_status_duration = fields.Char("Status with Time", compute="_compute_status_duration")

    # @api.onchange('payment_status')
    # def _onchange_status(self):
    #     self.payment_status_time = fields.Datetime.now()

    # @api.depends('payment_status_time')
    # def _compute_status_duration(self):
    #     for rec in self:
    #         if rec.payment_status_time:
    #             delta = fields.Datetime.now() - rec.payment_status_time
    #             minutes = int(delta.total_seconds() // 60)
    #             hours, mins = divmod(minutes, 60)
    #             if hours:
    #                 rec.payment_status_duration = f"{hours}H {mins}M"
    #             else:
    #                 rec.payment_status_duration = f"{mins}M"
    #         else:
    #             rec.payment_status_duration = "0M"


    @api.onchange("job_sheet_id")
    def _onchange_parts_amount(self):
        print("\n_onchange_parts_amount - Called\n")
        for rec in self:
            parts_total = sum(line.quantity * line.product_id.list_price for line in rec.job_sheet_id.part_line_ids)
            rec.parts_amount = parts_total

            service_total = sum(line.service_cost for line in rec.job_sheet_id)
            rec.service_amount = service_total

    @api.depends("service_amount", "parts_amount")
    def _compute_total_amount(self):
        print("\n_compute_total_amount - Called\n")
        for rec in self:
            rec.total_amount = (rec.parts_amount or 0.0) + (rec.service_amount or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("invoice_number", "New") == "New":
                vals["invoice_number"] = self.env["ir.sequence"].next_by_code("car.invoice") or "New"
        return super().create(vals_list)

    def action_unpaid_invoice(self):
        for rec in self:
            rec.payment_status = "unpaid"

    def action_paid_invoice(self):
        for rec in self:
            rec.payment_status = "paid"

    def action_partially_paid_invoice(self):
        for rec in self:
            rec.payment_status = "partial"


class ReportInvoicePrintCount(models.AbstractModel):
    _name = 'report.car_detailing_services.invoice_report_template'
    _description="Service Invoice report counter"

    def _get_report_values(self, docids, data=None):
        docs = self.env['car.invoice'].browse(docids)
        for doc in docs:
            doc.print_count += 1
        return {
            'doc_ids': docids,
            'doc_model': 'car.invoice',
            'docs': docs,
        }
