from odoo import models, fields, api


class TechnicialInfo(models.Model):
    _name="car.technician"
    _description="this model stores the data of the technician"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Technician Name: ")
    phone_no = fields.Char("Technician Number: ")
    skills = fields.Char("Technician Skils: ")
    image = fields.Binary("")
    available = fields.Boolean(default=True)
    user_id = fields.Many2one('res.users', string='User Account', ondelete='cascade', )

    # domain="[('groups_id', 'in', [ref('car_detailing_services.group_technician')])]"
