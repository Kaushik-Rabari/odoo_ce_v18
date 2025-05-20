/** @odoo-module **/

import { formatDuration } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { statusBarField, StatusBarField } from "@web/views/fields/statusbar/statusbar_field";
// import { onMounted } from "owl";
import { onMounted, useRef } from "owl";


export class StatusBarDurationField extends StatusBarField {
    static template = "car_detailing_services.StatusBarDurationField";

    // setup() {
    //     super.setup();
    //     onMounted(() => {
    //         this.adjustVisibleItems();
    //     });
    // }

    elRef = useRef("rootEl");  // Ref to root element with t-ref="rootEl"
    mounted() {
        super.mounted();
        if (this.elRef.el) {
            this.adjustVisibleItems();
        }
    }
    
    getAllItems() {
        const items = super.getAllItems();
        const durationTracking = this.props.record.data.duration_tracking || {};
        const now = new Date();
        const currentStatus = this.props.value;
        const lastChange = new Date(this.props.record.data.status_change_time);

        for (const item of items) {
            let duration = durationTracking[item.value] || 0;
            if (item.value === currentStatus) {
                duration += (now - lastChange) / 1000; // add current duration in seconds
            }

            if (duration > 0) {
                item.shortTimeInStage = formatDuration(duration, false); // e.g. "5M", "1H"
            } else {
                item.shortTimeInStage = null;
            }
        }
        return items;
    }

    adjustVisibleItems() {
        if (!this.el) {
            console.warn("StatusBarDurationField: this.el is null");
            return;
        }
        const spans = this.el.querySelectorAll('span.o_statusbar_status');
        if (!spans) {
            console.warn("StatusBarDurationField: no status spans found");
            return;
        }
        // Here you can implement any further adjustments to the spans if needed
        // For example, toggle visibility or styling depending on some condition
        // spans.forEach(span => { ... });
    }
}

export const statusBarDurationField = {
    ...statusBarField,
    component: StatusBarDurationField,
    displayName: _t("Statusbar with Duration"),
    supportedTypes: ["selection"],
    fieldDependencies: [
        { name: "duration_tracking", type: "json" },
        { name: "status_change_time", type: "datetime" },
    ],
};

registry.category("fields").add("statusbar_durations", statusBarDurationField);
