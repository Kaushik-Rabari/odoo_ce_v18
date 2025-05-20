from odoo import models, fields, api
from datetime import timedelta, time

class Vehicle(models.Model):
    _name = "car.vehicle"
    _description = "this model stored customers vehicles details"
    _rec_name = "vehicle_model"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    owner_id = fields.Many2one("res.partner")
    vehicle_model = fields.Char("Vehicle Model: ")
    # vehicle_company = fields.Char("Vehicle Company: ")
    vehicle_plate_no = fields.Char("Vehicle Plate No.: ")
    vehicle_year = fields.Char("Vehicle Year: ")
    vehicle_color = fields.Char("Vehicle Color: ")
    vehicle_image = fields.Binary()
    sheet_counts = fields.Integer(compute="sheet_count", string="Sheet Count")
    last_service_date = fields.Date("Last Service Date")
    service_interval_days = fields.Integer("Service Interval (Days)", default=90)
    vehicle_company = fields.Selection([
        # Indian Brands
        ('tata', 'Tata Motors'),
        ('mahindra', 'Mahindra'),
        ('maruti', 'Maruti Suzuki'),
        ('force', 'Force Motors'),
        ('ashok_leyland', 'Ashok Leyland'),

        # Korean Brands
        ('hyundai', 'Hyundai'),
        ('kia', 'Kia'),

        # Japanese Brands
        ('honda', 'Honda'),
        ('toyota', 'Toyota'),
        ('nissan', 'Nissan'),
        ('mitsubishi', 'Mitsubishi'),
        ('suzuki', 'Suzuki'),
        ('lexus', 'Lexus'),
        ('daihatsu', 'Daihatsu'),
        ('subaru', 'Subaru'),

        # American Brands
        ('ford', 'Ford'),
        ('chevrolet', 'Chevrolet'),
        ('jeep', 'Jeep'),
        ('cadillac', 'Cadillac'),
        ('buick', 'Buick'),
        ('tesla', 'Tesla'),
        ('lincoln', 'Lincoln'),
        ('chrysler', 'Chrysler'),
        ('gmc', 'GMC'),
        ('ram', 'RAM Trucks'),

        # German Brands
        ('volkswagen', 'Volkswagen'),
        ('bmw', 'BMW'),
        ('mercedes', 'Mercedes-Benz'),
        ('audi', 'Audi'),
        ('porsche', 'Porsche'),
        ('opel', 'Opel'),
        ('smart', 'Smart'),

        # British Brands
        ('land_rover', 'Land Rover'),
        ('jaguar', 'Jaguar'),
        ('mini', 'Mini'),
        ('rolls_royce', 'Rolls-Royce'),
        ('bentley', 'Bentley'),
        ('aston_martin', 'Aston Martin'),
        ('mg', 'MG Motor'),

        # French Brands
        ('renault', 'Renault'),
        ('peugeot', 'Peugeot'),
        ('citroen', 'Citroën'),

        # Italian Brands
        ('fiat', 'Fiat'),
        ('ferrari', 'Ferrari'),
        ('lamborghini', 'Lamborghini'),
        ('maserati', 'Maserati'),
        ('alfa_romeo', 'Alfa Romeo'),
        ('pagani', 'Pagani'),

        # Swedish Brands
        ('volvo', 'Volvo'),
        ('koenigsegg', 'Koenigsegg'),

        # Chinese Brands (entering Indian market slowly)
        ('byd', 'BYD'),
        ('geely', 'Geely'),
        ('great_wall', 'Great Wall Motors'),
        ('changan', 'Changan'),

        # Misc & Other
        ('other', 'Other / Unknown'),
    ], string="Vehicle Company")


    # Smart Button
    def smart_sheet_count(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'job Sheet',
            'view_mode': 'list,form',
            'res_model': 'car.job.sheet',
            'domain':[("vehicle_id", "=", self.id)],
            'context': {'default_vehicle_id': self.id},
        }
        return action
    
    @api.depends("vehicle_model")
    def sheet_count(self):
        for sheet in self:
            st = self.env['car.job.sheet'].search_count([("vehicle_id", "=", sheet.id)])
            print("\nst>>>>>>>>>>>>>>>>>>>>>>>>", st, "\n")
            sheet.sheet_counts= st

    def send_upcoming_service_reminders(self):
        print("\n=== Starting send_upcoming_service_reminders ===")
        today = fields.Date.today()
        upcoming_day = today + timedelta(days=7)
        print(f"Today's date: {today}, Upcoming threshold: {upcoming_day}")

        # vehicles = self.filtered(lambda v: v.last_service_date and v.service_interval_days)
        vehicles = self.env['car.vehicle'].search([])
        print(f"Vehicles to check: {len(vehicles)}")

        for vehicle in vehicles:
            due_date = vehicle.last_service_date + timedelta(days=vehicle.service_interval_days)
            print(f"Vehicle ID {vehicle.id} due date: {due_date}")

            if today <= due_date <= upcoming_day:
                customer = vehicle.owner_id
                if customer and customer.email:
                    print(f"Sending reminder to {customer.email} for vehicle {vehicle.vehicle_model} (ID {vehicle.id})")
                    template = self.env.ref("car_detailing_service.email_template_service_reminder", raise_if_not_found=False)
                    if not template:
                        print("ERROR: Email template not found!")
                        continue

                    mail_values = {
                        'subject': f"Upcoming Service Reminder for {vehicle.vehicle_model}",
                        'body_html': template._render_field('body_html', {'object': vehicle}),
                        'email_to': customer.email,
                        'auto_delete': True,
                    }
                    mail = self.env['mail.mail'].create(mail_values)
                    mail.send()
                else:
                    print(f"Skipping vehicle ID {vehicle.id}: No owner or email found.")
        print("=== Finished send_upcoming_service_reminders ===\n")
