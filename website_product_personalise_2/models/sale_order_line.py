from odoo import models, fields, api
from odoo.exceptions import UserError
# from odoo import Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    custom_text = fields.Char(string="Custom Text")  # Store the user’s input
    product_personalized_image = fields.Binary(string="Personalized Image")  # Store the customized image

    # @api.model_create_multi
    # def create(self, vals_list):
    #     print("\nvals_list----------", vals_list)

    #     for vals in vals_list:

    #     #     raw_attrs = vals.get('product_custom_attribute_value_ids', [])
    #     #     filtered_attrs = [
    #     #         (Command.CREATE, 0, attr) for (cmd, _, attr) in raw_attrs
    #     #         if attr.get('custom_value') and attr.get('custom_value').strip()
    #     #     ]
    #     #     vals['product_custom_attribute_value_ids'] = filtered_attrs

    #         product_id = vals.get('product_id')
    #         if product_id:
    #             product = self.env['product.product'].browse(product_id)
    #             if product.image_1920:
    #                 vals['product_personalized_image'] = product.image_1920  # Copy the product image

    #     records = super(SaleOrderLine, self).create(vals_list)
    #     print("\nAfter_Create----------", records)  # Debugging output
    #     return records

    def action_preview_image(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Personalized Image Preview',
            'res_model': 'sale.order.line',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',  # Opens in a popup
            'views': [(self.env.ref('website_product_personalise_2.sale_order_line_preview_view').id, 'form')],
        }

    def action_download_image(self):
        self.ensure_one()
        if not self.product_personalized_image:
            raise UserError("No image to download.")

        return {
            'type': 'ir.actions.act_url',
            'url': f'/download/image/{self.id}',
            'target': 'self',
        }
