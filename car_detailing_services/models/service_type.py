from odoo import fields, models, api


class ServiceType(models.Model):
    _name= "car.service.type"
    _description = "Services offered for vehicle care"
    _rec_name = "service_type"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # name = fields.Char("Name: ")
    # service_type = fields.Selection(
    #     [
    #         ("exterior_wash", "Exterior Wash"),
    #         ("interior_detailing", "Interior Detailing"),
    #         ("ceramic_coating", "Ceramic Coating"),
    #         ("engine_bay_cleaning", "Engine Bay Cleaning")
    #     ], string="Select Service")

    service_type = fields.Char("Service type: ")
    description = fields.Html("Description: ")
    price = fields.Integer("Price: ")
    duration = fields.Char("Duration/Timing :")
    # category = fields.Char("Category :")
    category = fields.Selection(
        [
            ("cleaning", "Cleaning"),
            ("detailing", "Detailing"),
            ("protection", "Protection / Coating"),
            ("maintenance", "Maintenance"),
            ("repair", "Repair"),
            ("Custom", "Custom Work"),
        ], string="Cateogry"
    )

    vehicle_type = fields.Selection(
        [
            ("hatchback", "Hatchback"),
            ("sedan", "Sedan"),
            ("suv", "SUV"),
            ("luxury", "Luxury"),
            ("van", "Van"),
            ("bike", "Bike"),
            ("other", "Other"),
        ], string="Vehicle Type", help="what kind of vehicle is this service designed for?"
    )

    active = fields.Boolean("Active", default=True)
    image = fields.Image("Service Image", max_width=256, max_height=256)

    recommended_frequency = fields.Char("Recommended Frequency", help="E.g., Every3 motnhs")
    includes_pickup = fields.Boolean("Pickup & Drop Included", default=False)
    gst_applicable = fields.Boolean("GST Applicable", default=True)
    tax_id = fields.Many2one("account.tax", string="Tax")

    # Analytics / tags
    is_popular = fields.Boolean("Mark as Popular")
    # tags = fields.Many2many("car.service.tag")
