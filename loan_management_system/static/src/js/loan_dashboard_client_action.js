/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class LoanDashboardClientAction extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            page: 1,
            filters: {
                user_id: false,
                borrower_id: false,
                loan_type_id: false,
                date_range: "lifetime",
                top_limit: 5,
                upcoming_duration: 365,
            },
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
        if (this.state.data?.has_prev) await this.loadData(this.state.page - 1);
    }

    async nextPage() {
        if (this.state.data?.has_next) await this.loadData(this.state.page + 1);
    }

    async printDashboard() {
        await this.action.doAction("loan_management_system.action_report_loan_dashboard");
    }

    async openLoanTypeRecords(loanTypeId) {
        if (!loanTypeId) return;
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Loan Records",
            res_model: "loan.loan",
            view_mode: "list,form",
            domain: [["loan_type_id", "=", loanTypeId]],
            target: "current",
        });
    }

    async downloadPanel(panelId) {
        const el = document.getElementById(panelId);
        if (!el) return;
        if (!window.html2canvas) {
            this.notification.add("Install html2canvas in assets to enable PNG export.", { type: "warning" });
            return;
        }
        const canvas = await window.html2canvas(el, { backgroundColor: "#ffffff" });
        const a = document.createElement("a");
        a.href = canvas.toDataURL("image/png");
        a.download = `${panelId}.png`;
        a.click();
    }

    amount(value) {
        return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 2 });
    }

    monthlyWidth(amount) {
        const vals = (this.state.data?.monthly_trend || []).map((row) => Number(row.amount || 0));
        const max = Math.max(...vals, 1);
        return `width:${Math.round((Number(amount || 0) / max) * 100)}%`;
    }

    stageRows() {
        return Object.entries(this.state.data?.stage_counts || {}).map(([label, count]) => ({ label, count: Number(count || 0) }));
    }

    stageWidth(count) {
        const vals = this.stageRows().map((row) => row.count);
        const max = Math.max(...vals, 1);
        return `height:${Math.round((Number(count || 0) / max) * 100)}%`;
    }

    loanTypeStyle() {
        const rows = this.state.data?.loan_type_volume || [];
        const first = Number(rows[0]?.amount || 0);
        const second = Number(rows[1]?.amount || 0);
        const total = first + second;
        const ratio = total ? Math.round((first * 100) / total) : 0;
        return `background:conic-gradient(#51c99b 0 ${ratio}%, #eb6a67 ${ratio}% 100%)`;
    }

    paidUnpaidStyle() {
        const paid = Number(this.state.data?.kpis?.paid_installment || 0);
        const unpaid = Number(this.state.data?.kpis?.unpaid_installment || 0);
        const total = paid + unpaid;
        const ratio = total ? Math.round((paid * 100) / total) : 0;
        return `background:conic-gradient(#55cb9b 0 ${ratio}%, #ee6b67 ${ratio}% 100%)`;
    }

    upcomingInstallments() {
        const today = new Date();
        const maxDate = new Date();
        maxDate.setDate(today.getDate() + Number(this.state.filters.upcoming_duration || 365));
        return (this.state.data?.top_installments || []).filter((item) => {
            const due = new Date(item.due_date);
            return due >= today && due <= maxDate;
        });
    }

    overdueInstallments() {
        const today = new Date();
        return (this.state.data?.top_installments || []).filter((item) => new Date(item.due_date) < today);
    }

    totalPages() {
        const total = Number(this.state.data?.total_installments || 0);
        const perPage = Number(this.state.data?.per_page || 10);
        return Math.max(Math.ceil(total / perPage), 1);
    }
}

LoanDashboardClientAction.template = "loan_management_system.LoanDashboardClientAction";
registry.category("actions").add("loan_dashboard.client_action", LoanDashboardClientAction);
