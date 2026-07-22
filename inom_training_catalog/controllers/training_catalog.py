from odoo import fields, http
from odoo.http import request


class TrainingCatalogController(http.Controller):
    @http.route(["/training_catalogue", "/training_catalogue/<string:view_mode>"], type="http", auth="public", website=True)
    def training_catalog(self, view_mode="portfolio", **kwargs):

        Event = request.env["event.event"].sudo()

        provider_type = kwargs.get("provider_type")
        content_type = kwargs.get("content_type")
        query = kwargs.get("q")
        # The Scheduled/Unscheduled filter was removed from the page. The value
        # is still read so any existing links/templates referencing it keep
        # working, but it no longer filters the listing.
        scheduled = kwargs.get("scheduled")
        published = kwargs.get("published")

        is_public_user = request.env.user._is_public()

        # Hide Cancelled and Completed (Ended) courses from every public
        # listing - both the Scheduled and the Portfolio views.
        # In Odoo's native event model:
        #   - a Cancelled event has kanban_state == 'cancel'
        #   - a Completed/Ended event sits in a stage flagged stage_id.pipe_end
        # The "!=" operators are null-safe (they also keep records whose value
        # is not set).
        base_domain = [
            ("show_in_portfolio", "=", True),
            ("kanban_state", "!=", "cancel"),
            ("stage_id.pipe_end", "!=", True),
        ]

        # Unscheduled courses are shown ALONGSIDE scheduled ones. The "upcoming"
        # listing therefore includes every upcoming dated course PLUS every
        # course flagged "Unscheduled" in the backend (these have no start
        # date). The "portfolio" view keeps the same combined behaviour.
        if view_mode == "upcoming":
            base_domain += [
                "|",
                ("is_unscheduled_course", "=", True),
                ("date_begin", ">=", fields.Datetime.now()),
            ]
        elif view_mode == "portfolio":
            base_domain += [
                "|",
                ("is_unscheduled_course", "=", True),
                ("date_begin", "!=", False),
            ]

        if provider_type in ("aha", "iap2"):
            base_domain.append(("provider_type", "=", provider_type))

        if content_type in ("engagement", "conflict", "facilitation", "evaluation"):
            base_domain.append(("content_type", "=", content_type))

        if is_public_user:
            # Public visitors always see published-only — no choice given.
            base_domain.append(("website_published", "=", True))
        else:
            # Logged-in / admin users:
            #   "published"   -> show only published
            #   "unpublished" -> show only unpublished
            #   anything else -> show BOTH (default for admins)
            if published == "published":
                base_domain.append(("website_published", "=", True))
            elif published == "unpublished":
                base_domain.append(("website_published", "=", False))

        if query:
            search_fields = [field for field in ("name", "subtitle", "description") if field in Event._fields]
            if search_fields:
                if len(search_fields) == 1:
                    base_domain.append((search_fields[0], "ilike", query))
                elif len(search_fields) == 2:
                    base_domain += ["|", (search_fields[0], "ilike", query), (search_fields[1], "ilike", query)]
                else:
                    base_domain += [
                        "|",
                        "|",
                        (search_fields[0], "ilike", query),
                        (search_fields[1], "ilike", query),
                        (search_fields[2], "ilike", query),
                    ]

        events = Event.search(base_domain, order="date_begin asc, name asc")

        values = {
            "events": events,
            "view_mode": view_mode,
            "provider_type": provider_type,
            "content_type": content_type,
            "q": query,
            "scheduled": scheduled,
            "published": published,
            "is_public_user": is_public_user,
        }

        return request.render("inom_training_catalog.training_catalog_page", values)
