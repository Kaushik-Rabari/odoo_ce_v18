import imghdr
from base64 import b64decode
from odoo import http,fields, _
from odoo.http import request


class CustomImageController(http.Controller):

    @http.route(['/custom_image_save'], type='http', auth="public", methods=['POST'], csrf=False)
    def save_custom_image(self, **post):
        image_data = post.get("image_data")
        product_id = post.get("product_id")
        redirect_url = post.get("redirect_url") or '/'
        print(f"\nimage_data---{bool(image_data)}, product_id---{bool(product_id)}, redirect_url---{bool(redirect_url)}")

        if not image_data or not product_id:
            return request.redirect('/error_page')

        # remove data prefix from base64
        if "," in image_data:
            print("------if.image_data------")
            image_data = image_data.split(",")[1]

        try:
            decoded_image = b64decode(image_data)
            # print("------try.decoded_image------", decoded_image)
        except Exception as e:
            return request.redirect('/error_page')

        # Find draft Sale Order and matching product line
        sale_order = request.env['sale.order'].sudo().search([('state', '=', 'draft')], limit=1)
        print("sale_order------------", sale_order)
        if sale_order:
            line = request.env['sale.order.line'].sudo().search([
                ('order_id', '=', sale_order.id),
                ('product_id', '=', int(product_id))
            ], order='id desc', limit=1)
            print("line------------", line)

            if line:
                line.write({'product_personalized_image': image_data})

        # # Find draft Sale Order and matching product line
        # sale_order = request.env['sale.order'].sudo().search([('state', '=', 'draft')], limit=1)
        # print("sale_order------------", sale_order)
        # if sale_order:
        #     line = sale_order.order_line.filtered(lambda l: l.product_id.id == int(product_id))
        #     print("line------------", line)
        #     latest_line = line.search([], order="id desc", limit=1)
        #     print("Latest Line ID:", latest_line.id)

        #     if latest_line:
        #         latest_line.sudo().write({
        #             'product_personalized_image': image_data,  # must be base64 string
        #         })
        #         print("line------------", line)

        return request.redirect(redirect_url)

class ImageDownloadController(http.Controller):

    @http.route('/download/image/<int:line_id>', type='http', auth='user')
    def download_image(self, line_id):
        sale_line = request.env['sale.order.line'].sudo().browse(line_id)
        if not sale_line.exists() or not sale_line.product_personalized_image:
            return request.not_found()

        image_data = b64decode(sale_line.product_personalized_image)

        # Detect actual file type
        file_type = imghdr.what(None, image_data)
        print("\nfile_type---------", file_type)
        if not file_type:
            return request.not_found()

        # Example: file_type = 'png', 'jpeg', etc.
        content_type = f'image/{file_type}'
        print("content_type---------", content_type)

        filename = f'product_personalized_image.{file_type}'
        print("filename---------", filename)

        headers = [
            ('Content-Type', content_type),
            ('Content-Disposition', f'attachment; filename="{filename}"'),
        ]
        print("headers---------", headers, "\n")
        return request.make_response(image_data, headers)
