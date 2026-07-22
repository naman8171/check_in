import logging

from babel.dates import format_date

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class EventEvent(models.Model):
    _inherit = "event.event"

    # ----------------------------------------------------------------
    # Provider / content classification
    # ----------------------------------------------------------------
    provider_type = fields.Selection(
        selection=[
            ("aha", "Aha Academy"),
            ("iap2", "IAP2"),
        ],
        string="Pathway Type",
        help="Controls website visibility rules for event details.",
    )

    content_type = fields.Selection(
        selection=[
            ("engagement", "Engagement"),
            ("conflict", "Conflict"),
            ("facilitation", "Facilitation"),
            ("evaluation", "Evaluation"),
        ],
        string="Topic Type",
    )

    booking_url = fields.Char(string="Booking Link")
    more_info_url = fields.Char(string="More Information Link")

    # Free-text "Level & Pathway" line shown on the catalog card, just
    # below the course title (centered, Lora italic, #e8a821). Populated
    # per event from the backend; hidden on the card when left empty.
    level_pathway = fields.Char(
        string="Level & Pathway",
        translate=True,
        help="Short level / pathway label shown beneath the course title "
             "on the public catalog card (e.g. 'Foundation - Engagement "
             "Pathway').",
    )

    # ----------------------------------------------------------------
    # Course detail-page content (the redesigned public event page).
    #
    # The four "info box" fields are free text; put each line of the box
    # on its own line (they render with the line breaks preserved). They
    # are shown only when filled, so empty boxes are simply omitted.
    # "About this Course" reuses ``intro_text`` (fallback ``description``);
    # the Participants block uses ``participants_text``.
    # ----------------------------------------------------------------
    course_duration = fields.Text(
        string="Duration (detail page)",
        translate=True,
        help="Shown in the DURATION box on the course detail page. One value "
             "per line, e.g. '2 DAYS' then '9-4 PM'.",
    )
    course_delivery = fields.Text(
        string="Delivery (detail page)",
        translate=True,
        help="Shown in the DELIVERY box, one value per line "
             "(e.g. 'FACE TO FACE' / 'ONLINE CLASSROOM').",
    )
    course_format = fields.Text(
        string="Format (detail page)",
        translate=True,
        help="Shown in the FORMAT box, one value per line.",
    )
    course_prerequisite = fields.Text(
        string="Prerequisite (detail page)",
        translate=True,
        help="Shown in the PREREQUISITE box, one value per line.",
    )

    # ----------------------------------------------------------------
    # Course price (shown in the right sidebar on the detail page,
    # after the date/time block and before the venue). The price is taken
    # automatically from the cheapest available event ticket -- i.e. the
    # same price shown in the "Book Now" tickets popup -- so it never has
    # to be kept in sync by hand. Visibility follows
    # website_can_see_restricted_fields(): always shown on Aha Academy
    # courses, only to logged-in visitors on IAP2 courses.
    # ----------------------------------------------------------------
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        compute="_compute_course_price",
        compute_sudo=True,
    )
    course_price = fields.Monetary(
        string="Course Price (from ticket)",
        compute="_compute_course_price",
        compute_sudo=True,
        currency_field="currency_id",
        help="Automatically taken from the cheapest available event ticket "
             "(the price shown in the Book Now popup). Shown in the right "
             "sidebar of the course detail page; hidden when there is no "
             "priced ticket.",
    )

    @api.depends("event_ticket_ids")
    def _compute_course_price(self):
        """Headline price = cheapest available (priced) event ticket.

        The ``price`` field on event tickets is provided by the event sale
        apps, so it is read defensively: when those apps are not installed
        the block simply shows nothing (price stays 0.0).
        """
        for event in self:
            currency = (event.company_id or self.env.company).currency_id
            price = 0.0
            tickets = event.event_ticket_ids
            if tickets and "price" in tickets._fields:
                available = tickets.filtered("sale_available") or tickets
                priced = available.filtered(lambda t: t.price)
                chosen = self.env["event.event.ticket"]
                if priced:
                    chosen = min(priced, key=lambda t: t.price)
                elif available:
                    chosen = available[:1]
                if chosen:
                    price = chosen.price or 0.0
                    if "currency_id" in chosen._fields and chosen.currency_id:
                        currency = chosen.currency_id
            event.course_price = price
            event.currency_id = currency
    participants_text = fields.Html(
        string="Participants (detail page)",
        translate=True,
        sanitize=True,
        help="Shown in the 'Participants' section at the bottom of the "
             "course detail page.",
    )
    learning_outcomes = fields.Html(
        string="Learning Outcomes (detail page)",
        translate=True,
        sanitize=True,
        help="Shown in the 'Learning Outcomes' section at the bottom of the "
             "course detail page.",
    )

    # ----------------------------------------------------------------
    # Facilitator (the "YOUR FACILITATOR" block on the detail page).
    # Name, bio and photo are managed from the backend event form and
    # rendered at the bottom of the public course detail page. The block
    # is shown only when at least one of these fields is filled.
    # ----------------------------------------------------------------
    facilitator_name = fields.Char(
        string="Facilitator Name",
        translate=True,
        help="Facilitator's name shown in the 'YOUR FACILITATOR' block on "
             "the course detail page.",
    )
    facilitator_bio = fields.Html(
        string="Facilitator Bio",
        translate=True,
        sanitize=True,
        help="Short biography shown beneath the facilitator's name on the "
             "course detail page.",
    )
    facilitator_image = fields.Image(
        string="Facilitator Photo",
        max_width=1024,
        max_height=1024,
        help="Photo shown to the right of the facilitator bio on the course "
             "detail page.",
    )

    # ----------------------------------------------------------------
    # Event-page introduction (replaces Odoo's static default)
    #
    # Out of the box, every new event's website ``description`` is
    # pre-filled by Odoo with a shared boilerplate snippet ("Join us for
    # this ... Event / Every year we invite our community ..."). That is
    # why the intro looks identical on every event page until someone
    # edits it in the website builder.
    #
    # These two fields let an editor manage that intro from the backend
    # event form instead. The website template (see
    # ``inom_training_catalog.event_page_intro_fields``) renders them at
    # the top of the event detail page in place of the default
    # description. If BOTH are left empty, the page falls back to the
    # standard ``description`` field, so existing events are unaffected
    # until the new fields are filled in.
    # ----------------------------------------------------------------
    intro_heading = fields.Char(
        string="Event Page Heading",
        translate=True,
        help="Heading shown at the top of the public event detail page, "
             "replacing Odoo's default event introduction.",
    )
    intro_text = fields.Html(
        string="Course Description",
        translate=True,
        sanitize=True,
        help="Introductory paragraph shown beneath the heading on the "
             "public event detail page. Leave this and the heading empty "
             "to fall back to the standard event description.",
    )

    # ----------------------------------------------------------------
    # Course image
    #
    # In this Odoo 19 build, ``event.event`` does **not** inherit
    # ``image.mixin`` (we confirmed via the upgrade error: ``Field
    # "image_1920" does not exist in model "event.event"``). We
    # therefore declare the image fields explicitly here -- the main
    # ``image_1920`` plus the four derived variants that ``image.mixin``
    # would normally provide. The form view's
    # ``options="{'preview_image': 'image_128'}"`` relies on
    # ``image_128`` actually existing, so we can't skip the variants.
    #
    # The variant fields are related-with-store on ``image_1920``: you
    # upload one large image, Odoo auto-resizes and persists the four
    # smaller versions, and the website / kanban / list views all read
    # from whichever variant matches their layout.
    # ----------------------------------------------------------------
    image_1920 = fields.Image(
        string="Thumbnail Image",
        max_width=1920,
        max_height=1920,
        help="Thumbnail shown on the course cards and listings in the "
             "public catalog (and used as the record image in the "
             "backend kanban/list). Odoo auto-derives the smaller "
             "variants used by those views. For the wide banner at the "
             "top of the course detail page, use the separate "
             "'Cover / Header Image' field instead.",
    )
    image_1024 = fields.Image(
        "Image 1024",
        related="image_1920",
        max_width=1024, max_height=1024,
        store=True, readonly=False,
    )
    image_512 = fields.Image(
        "Image 512",
        related="image_1920",
        max_width=512, max_height=512,
        store=True, readonly=False,
    )
    image_256 = fields.Image(
        "Image 256",
        related="image_1920",
        max_width=256, max_height=256,
        store=True, readonly=False,
    )
    image_128 = fields.Image(
        "Image 128",
        related="image_1920",
        max_width=128, max_height=128,
        store=True, readonly=False,
    )

    # ----------------------------------------------------------------
    # Cover / header image  (course detail-page banner)
    #
    # Kept separate from ``image_1920`` (the thumbnail) so each image can
    # be cropped and sized for its own space: a roughly square-ish card
    # thumbnail vs. a wide banner across the top of the detail page.
    #
    # This is a standalone ``fields.Image`` (no resize variants needed --
    # it is only ever rendered large, in the banner). If it is left
    # empty, the detail page falls back to ``image_1920`` so existing
    # courses keep their banner until a dedicated cover is uploaded.
    # ----------------------------------------------------------------
    cover_image = fields.Image(
        string="Cover / Header Image",
        max_width=1920,
        max_height=1920,
        help="Wide banner/header image shown at the top of the course "
             "detail page. Upload an image cropped for a wide header so "
             "it fills that space correctly. If left empty, the detail "
             "page falls back to the Thumbnail Image.",
    )

    training_pdf_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Training PDF",
        domain='[("res_model","=","event.event"), ("mimetype","=like","application/pdf%")]',
        help="Downloadable PDF for this course/event.",
    )

    # ----------------------------------------------------------------
    # Catalog visibility
    # ----------------------------------------------------------------
    show_in_portfolio = fields.Boolean(
        string="Show in Portfolio",
        default=True,
        help="Display this course in the always-on portfolio section.",
    )

    is_unscheduled_course = fields.Boolean(
        string="Unscheduled Course",
        help="Use this when the course should appear as a portfolio item "
             "without an active schedule.",
    )

    visibility_state = fields.Selection(
        selection=[("published", "Published"), ("unpublished", "Unpublished")],
        string="Publish/Unpublish",
        compute="_compute_visibility_state",
        search="_search_visibility_state",
    )

    schedule_state = fields.Selection(
        selection=[("scheduled", "Scheduled"), ("unscheduled", "Unscheduled")],
        string="Scheduled/Unscheduled",
        compute="_compute_schedule_state",
        search="_search_schedule_state",
    )

    # ----------------------------------------------------------------
    # Computes & searches
    # ----------------------------------------------------------------
    @api.depends("website_published")
    def _compute_visibility_state(self):
        for event in self:
            event.visibility_state = (
                "published" if event.website_published else "unpublished"
            )

    @api.depends("is_unscheduled_course", "date_begin")
    def _compute_schedule_state(self):
        for event in self:
            event.schedule_state = (
                "unscheduled"
                if event.is_unscheduled_course or not event.date_begin
                else "scheduled"
            )

    def _search_visibility_state(self, operator, value):
        if operator not in ("=", "!="):
            return []
        want_published = value == "published"
        if operator == "!=":
            want_published = not want_published
        return [("website_published", "=", want_published)]

    def _search_schedule_state(self, operator, value):
        if operator not in ("=", "!="):
            return []
        want_unscheduled = value == "unscheduled"
        if operator == "!=":
            want_unscheduled = not want_unscheduled
        if want_unscheduled:
            return [
                "|",
                ("is_unscheduled_course", "=", True),
                ("date_begin", "=", False),
            ]
        return [
            ("is_unscheduled_course", "=", False),
            ("date_begin", "!=", False),
        ]

    # ----------------------------------------------------------------
    # Website helpers
    # ----------------------------------------------------------------
    def website_can_see_restricted_fields(self):
        """IAP2 details (booking link, PDF, etc.) are gated to logged-in
        visitors. Aha Academy events are public. Internal users see
        everything."""
        self.ensure_one()
        return self.provider_type != "iap2" or not self.env.user._is_public()

    def website_pdf_url(self):
        """Return a /web/content URL for the linked PDF attachment, or
        False if no PDF is attached."""
        self.ensure_one()
        if not self.training_pdf_attachment_id:
            return False
        return f"/web/content/{self.training_pdf_attachment_id.id}?download=true"

    def catalog_date_display(self):
        """Human-friendly date label shown on the public catalogue card.

        Formatting rules (day-level, no year):
          * Single day               -> "2 November"
          * Same month, two days     -> "2 and 3 November"
          * Spanning two months      -> "30 June and 31 July"

        ``date_begin`` / ``date_end`` are stored in UTC, so both are first
        converted to the visitor's timezone (the same conversion the datetime
        widget applies elsewhere on the card) before the day/month is read.
        Returns an empty string when the event has no start date.
        """
        self.ensure_one()
        if not self.date_begin:
            return ""

        lang = self.env.context.get("lang") or "en_US"

        def _fmt(value, fmt):
            try:
                return format_date(value, format=fmt, locale=lang)
            except Exception:  # Unknown/locale issues fall back to English.
                return format_date(value, format=fmt, locale="en_US")

        begin = fields.Datetime.context_timestamp(self, self.date_begin)
        end = (
            fields.Datetime.context_timestamp(self, self.date_end)
            if self.date_end
            else begin
        )

        # Single-day event (start and end land on the same calendar day).
        if begin.date() == end.date():
            return _fmt(begin, "d MMMM")

        # Same month and year -> share the month name once: "2 and 3 November".
        if (begin.year, begin.month) == (end.year, end.month):
            return "%s and %s" % (_fmt(begin, "d"), _fmt(end, "d MMMM"))

        # Different months -> spell out both fully: "30 June and 31 July".
        return "%s and %s" % (_fmt(begin, "d MMMM"), _fmt(end, "d MMMM"))
