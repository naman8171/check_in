from datetime import datetime

import pytz

from odoo import _, api, fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    late_check_in = fields.Boolean(string="Late Check-in", default=False, index=True)
    late_minutes = fields.Integer(string="Late by (minutes)", default=0)

    @api.model_create_multi
    def create(self, vals_list):
        attendances = super().create(vals_list)
        template = self.env.ref(
            "hr_attendance_late_checkin.mail_template_late_check_in",
            raise_if_not_found=False,
        )

        for attendance in attendances:
            late_info = attendance._get_late_check_in_info()
            if not late_info["is_late"]:
                continue

            attendance.write(
                {
                    "late_check_in": True,
                    "late_minutes": late_info["late_minutes"],
                }
            )

            if template:
                attendance._send_late_email(template, late_info["scheduled_start_local"])

        return attendances

    def _get_late_check_in_info(self):
        self.ensure_one()

        if not self.employee_id or not self.check_in:
            return {"is_late": False, "late_minutes": 0, "scheduled_start_local": None}

        calendar = self.employee_id.resource_calendar_id or self.employee_id.company_id.resource_calendar_id
        if not calendar:
            return {"is_late": False, "late_minutes": 0, "scheduled_start_local": None}

        timezone_name = (
            calendar.tz
            or self.employee_id.tz
            or self.employee_id.company_id.partner_id.tz
            or "UTC"
        )
        timezone = pytz.timezone(timezone_name)

        check_in_utc = fields.Datetime.from_string(self.check_in)
        check_in_local = pytz.UTC.localize(check_in_utc).astimezone(timezone)
        weekday = str(check_in_local.weekday())

        day_lines = calendar.attendance_ids.filtered(
            lambda line: line.dayofweek == weekday and line.display_type == False
        )
        if not day_lines:
            return {"is_late": False, "late_minutes": 0, "scheduled_start_local": None}

        earliest_line = min(day_lines, key=lambda line: line.hour_from)

        start_hour = int(earliest_line.hour_from)
        start_minute = int(round((earliest_line.hour_from - start_hour) * 60))

        scheduled_start_local = check_in_local.replace(
            hour=start_hour, minute=start_minute, second=0, microsecond=0
        )

        late_delta = check_in_local - scheduled_start_local
        late_minutes = max(0, int(late_delta.total_seconds() // 60))

        return {
            "is_late": late_minutes > 0,
            "late_minutes": late_minutes,
            "scheduled_start_local": scheduled_start_local,
        }

    def _send_late_email(self, template, scheduled_start_local):
        self.ensure_one()

        manager = self.employee_id.parent_id
        if not manager or not manager.work_email:
            return

        employee_email = self.employee_id.work_email
        email_to = manager.work_email
        email_cc = employee_email if employee_email else False

        start_label = (
            scheduled_start_local.strftime("%H:%M")
            if isinstance(scheduled_start_local, datetime)
            else _("the scheduled office time")
        )

        context = {
            "scheduled_start_label": start_label,
            "late_minutes": self.late_minutes,
        }

        template.with_context(**context).send_mail(
            self.id,
            force_send=True,
            email_values={"email_to": email_to, "email_cc": email_cc},
        )
