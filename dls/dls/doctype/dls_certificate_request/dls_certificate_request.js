// Copyright (c) 2022, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("DLS Certificate Request", {
	refresh: function (frm) {
		if (!frm.is_new() && frm.doc.status == "Upcoming") {
			frm.add_custom_button(__("Conduct Evaluation"), () => {
				frappe.model.open_mapped_doc({
					method: "dls.dls.doctype.dls_certificate_request.dls_certificate_request.create_dls_certificate_evaluation",
					frm: frm,
				});
			});
		}
		if (!frm.doc.google_meet_link && frm.doc.status == "Upcoming") {
			frm.add_custom_button(__("Generate Google Meet Link"), () => {
				frappe.call({
					method: "dls.dls.doctype.dls_certificate_request.dls_certificate_request.setup_calendar_event",
					args: {
						eval: frm.doc,
					},
				});
			});
		}
	},

	onload: function (frm) {
		frm.set_query("member", function (doc) {
			return {
				filters: {
					ignore_user_type: 1,
				},
			};
		});
	},
});
