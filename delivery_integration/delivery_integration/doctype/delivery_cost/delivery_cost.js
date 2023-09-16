// Copyright (c) 2021, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Cost', {
	onload: function(frm) {
		if(cur_frm.is_new()){
			console.log("delivery_cost_set_default_value")
			cur_frm.events.delivery_cost_set_default_value();
		}
		cur_frm.events.set_filter();
	},
	delivery_cost_set_default_value: function (){
		cur_frm.set_value("from_territory","Jabodetabek-DKI Jakarta");
		cur_frm.set_value("to_territory","");
	},
	set_filter:function(){
		cur_frm.set_query("to_territory", function () {
			return {
					"filters": [
					['type', '=', 'District']
					]
			}
	});
	}
});
