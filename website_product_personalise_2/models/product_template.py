from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(self, combination=None, **kwargs):
        """ Override Odoo's base `_get_combination_info` method to add custom attributes dynamically. """
        result = super()._get_combination_info(combination, **kwargs)

        # Get the product variant based on the combination
        if combination:
            variant = self._get_variant_for_combination(combination)
        else:
            variant = self.env['product.product'].search([('product_tmpl_id', '=', self.id)], limit=1)

        if variant:
            custom_attributes = {}
            for attr in variant.custom_attributes:

                custom_attributes[attr.attr_id.name] = {
                    "attr_id": attr.attr_id.id,
                    "name": attr.name,
                    "top": attr.top,
                    "left": attr.left,
                    "font_color": attr.font_color,
                    "font_size": f"{attr.font_size}px",
                    # "font_family": attr.font_family,
                }
            result.update({"custom_input_style": custom_attributes})
            print("\nFinal_Result -------", result, "\n")

        return result
