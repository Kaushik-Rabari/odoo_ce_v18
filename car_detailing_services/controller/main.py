from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalVehicleService(CustomerPortal):
    def prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        values['job_sheet_count'] = request.env['car.job.sheet'].sudo().search_count([('customer_id', '=', partner.id)])
        values['invoice_count'] = request.env['car.invoice'].sudo().search_count([('customer_id', '=', partner.id)])
        return values

    @http.route(['/my/job-sheets'], type='http', auth='user', website=True)
    def portal_my_job_sheets(self, **kwargs):
        partner = request.env.user.partner_id
        job_sheets = request.env["car.job.sheet"].sudo().search([('customer_id', '=', partner.id)])
        return request.render("car_detailing_services.portal_my_job_sheets", {
            'job_sheets': job_sheets,
        })

class CarDetailingPortal(http.Controller):
    @http.route(['/my/job/', '/my/job/<int:job_id>/feedback'], type="http", auth="user", website=True)
    def job_feedback_form(self, job_id, **kwargs):
        print("\nkwargs --->", kwargs)
        print("job_id --->", job_id, "\n")

        job = request.env['car.job.sheet'].sudo().browse(int(job_id))
        job.check_access('read')
        job.check_access('read')
        if not job.exists():
            raise NotFound()
        return request.render("car_detailing_services.job_feedback_template", {
            "job": job,
        })
    
    @http.route(['/my/job/', '/my/job/<int:job_id>/feedback/submit'], type="http", auth="user", methods=['POST'], website=True)
    def job_feedback_submit(self, job_id, rating, comments, **kwargs):
        job = request.env['car.job.sheet'].sudo().browse(job_id)
        if not job.exists() or job.booking_id.customer_id.user_id.id != request.uid:
            return request.not_found()
        
        request.env['car.job.sheet.feedback'].sudo().create({
            'job_sheet_id': job_id,
            'rating': rating,
            'comments': comments,
        })

        return request.redirect('/my/jobs')