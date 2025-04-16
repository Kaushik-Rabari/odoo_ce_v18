from odoo import models, fields

class ProductCustomAttribute(models.Model):
    _name = "product.custom.attribute"
    _description = "Custom Product Attributes"

    product_id = fields.Many2one("product.product", string="Product Variant", ondelete="cascade", readonly=True)
    attr_id = fields.Many2one("product.attribute", string="Select Attribute", required=True)
    name = fields.Char(string="Attribute Name")
    top = fields.Integer(string="Top Position", default=125)
    left = fields.Integer(string="Left Position", default=320)
    font_color = fields.Char(string="Font Color", default="black")
    font_size = fields.Integer(string="Font Size", default=23)
    # font_family = fields.Char(string="Font Family", default="Arial")
