/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class LoanDashboardClientAction extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            page: 1,
            filters: { user_id: false, borrower_id: false, loan_type_id: false, date_range: "lifetime", top_limit: 5 },
            data: null,
        });
        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData(page = 1) {
        this.state.loading = true;
        this.state.page = page;
        this.state.data = await this.orm.call("loan.dashboard", "get_dashboard_payload", [this.state.filters, page, 10]);
        this.state.loading = false;
    }

    async onFilterChange(ev, key) {
        const val = ev.target.value;
        this.state.filters[key] = val ? (Number.isNaN(parseInt(val)) ? val : parseInt(val)) : false;
        await this.loadData(1);
    }

    async prevPage() {
        if (this.state.data?.has_prev) {
            await this.loadData(this.state.page - 1);
        }
    }

    async nextPage() {
        if (this.state.data?.has_next) {
            await this.loadData(this.state.page + 1);
        }
    }

    async printDashboard() {
        await this.action.doAction("loan_management_system.action_report_loan_dashboard");
    }
}

LoanDashboardClientAction.template = "loan_management_system.LoanDashboardClientAction";
registry.category("actions").add("loan_dashboard.client_action", LoanDashboardClientAction);
