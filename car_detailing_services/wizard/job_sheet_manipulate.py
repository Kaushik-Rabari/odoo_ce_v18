from odoo import models, fields, api

class UpdateJobSheetData(models.TransientModel):
    _name = "car.job.sheet.wizard"
    _description = "Wizard for Updating Job Sheet Data"

    name = fields.Char(string="Job Sheet No.", readonly=True, default="New")
    technician_id = fields.Many2one("car.technician", string="Assigned Technician")
    tasks_done = fields.Text("Tasks Done / Notes")

    def update_job_sheet_details(self):
        print("\n🛠️ Starting job sheet update wizard...")

        job_sheet_ids = self.env.context.get("active_ids", [])
        print("📄 Active Job Sheet IDs from context:", job_sheet_ids)

        job_sheets = self.env["car.job.sheet"].browse(job_sheet_ids)
        print(f"🔍 Retrieved Job Sheet Records: {[j.name for j in job_sheets]}")

        for job_sheet in job_sheets:
            print(f"\n➡️ Updating Job Sheet: {job_sheet.name}")
            print(f"👨‍🔧 New Technician: {self.technician_id.name if self.technician_id else 'None'}")
            print(f"📝 New Task Notes: {self.tasks_done}")

            job_sheet.write({
                'technician_id': self.technician_id.id,
                'tasks_done': self.tasks_done,
            })

            job_sheet.message_post(
                body=f"Updated via wizard:"
                     f"- Technician: {self.technician_id.name}<br/>"
                     f"- Tasks Done: {self.tasks_done}"
            )

            print(f"✅ Job Sheet {job_sheet.name} updated successfully.")

        print("🎉 Wizard completed.\n")



# from odoo import models, fields


# class UpdateJobSheetData(models.TransientModel):
#     _name="car.job.sheet.wizard"
#     _description="wizard for update job sheet data"

#     name = fields.Char("Job Sheet no.: ", required=True, copy=False, readonly=True, default="New")
#     technician_id = fields.Many2one("car.technician", string="Assigned Technician: ")
#     tasks_done = fields.Text("Tasks Done/ Notes")
#     # booking_id = fields.Many2one("car.booking", string="Booking Reference", required=True)
#     # service_ids = fields.Many2many(related="booking_id.service_ids", string="Services: ")

#     def update_job_sheet_details(self):
#         print("\nself.context-----------", self._context)
#         new_technician_id = self.env["car.job.sheet"].browse(self._context.get("active_ids"))
#         new_technician_id.technician_id = self.technician_id
#         print("new_technician_id-----------", new_technician_id)

#         new_tasks_done = self.env["car.job.sheet"].browse(self._context.get("active_ids"))
#         new_tasks_done.tasks_done = self.tasks_done
#         print("new_tasks_done-----------", new_tasks_done, "\n")
