// Copyright (c) 2025, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("DLS Batch Enrollment", {
	refresh(frm) {
		if (!frm.doc.confirmation_email_sent) {
			frm.add_custom_button(__("Send Confirmation Email"), function () {
				frappe.call({
					method: "dls.dls.doctype.dls_batch_enrollment.dls_batch_enrollment.send_confirmation_email",
					args: {
						doc: frm.doc,
					},
					callback: function (r) {
						frm.refresh();
					},
				});
			});
		}
	},
});
