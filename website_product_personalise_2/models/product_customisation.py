from odoo import models, fields, api


class ProductCustomisation(models.Model):
    _inherit = "product.product"

    custom_attributes = fields.One2many(
        "product.custom.attribute",
        "product_id",
        string="Custom Attributes",
    )
