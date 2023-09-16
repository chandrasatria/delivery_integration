// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Area', {
	refresh: function(frm) {
		frm.events.set_query(frm);
	},

	set_query: function(frm) {
		frm.set_query("delivery_territory", function(){
			return {
				"filters" : [
				['Territory', 'type', 'NOT IN', ['Country', 'Province']]
				]
			}
		})
	}
});
