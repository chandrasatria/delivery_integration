import frappe

def on_update(self, method):
    if self.get("name"):
        territory_update_tree(self.get("name"))
        self.reload()

def territory_update_tree(territory):
	territories = frappe.get_all("Territory", fields=["name", "lft", "rgt"],filters=[["name","=",territory]])

	for t in territories:
		search_list = ""
		country, province, city, district, subdistrict = None, None, None, None, None

		parent_territory = frappe.get_all("Territory", fields=["name", "type"], filters=[['lft', '<=', t['lft']], ['rgt', '>=', t['rgt']], ['name', '!=', 'All Territories']], order_by="lft DESC")
		if len(parent_territory) > 0:
			for pt in parent_territory:
				print('{} = "{}"'.format(pt['type'].lower(), pt['name']))
				if pt['type'].lower() == "country":
					country = pt['name']
				if pt['type'].lower() == "province":
					province = pt['name']
				if pt['type'].lower() == "city":
					city = pt['name']
				if pt['type'].lower() == "district":
					district = pt['name']
				if pt['type'].lower() == "subdistrict":
					subdistrict = pt['name']
				search_list += "{}\n".format(pt['name'])
		else:
			# tidak ada parentnya
			pass

		print("{} | {} | {} | {} | {}".format(country, province, city, district, subdistrict))

		frappe.db.sql("""
			UPDATE `tabTerritory`
			SET 
				search_list = %(search_list)s,
				country = %(country)s,
				province = %(province)s,
				city = %(city)s,
				district = %(district)s,
				subdistrict = %(subdistrict)s
			WHERE name = %(name)s
			""", {
			"search_list"	: search_list,
			"name"			: t['name'],
			"country"		: country,
			"province"		: province,
			"city"			: city,
			"district"		: district,
			"subdistrict"	: subdistrict
			})
		print("Updating {}: {}".format("Territory", t['name']))
	frappe.db.commit()