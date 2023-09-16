# -*- coding: utf-8 -*-
# Copyright (c) 2020, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

import json
from frappe.utils import get_request_session
from frappe import _
from api_integration.validation import error_format, success_format

@frappe.whitelist(allow_guest=True)
def get_delivery():
	"""
	REQUEST
	{
		"to_territory" 	: "",
		"supplier_item"		: [
			{
				"supplier"			: "",
				"from_territory"	: "",
				"item"				: [
					{
						"item_name"		: "",
						"item_weight"	: ,
						"length"		: ,
						"width"			: ,
						"height"		: ,
						"qty"			: 
					},
					{
						"item_name"		: "",
						"item_weight"	: ,
						"length"		: ,
						"width"			: ,
						"height"		: ,
						"qty"			: 
					}
				]
			}
		]
	}

	RESPONSE
	{
		"delivery_method" : [
			{
				"supplier" 	: "nama supplier A",
				"available_delivery"	: [
					{
						"nama_cargo"	: "Muat",
						"pricelist"		: [
							{
								"type"	: "Reguler",
								"price"	: 100000
							}
						] 
					},
					{
						"nama_cargo"	: "JNE",
						"pricelist"		: [
							{
								"type"	: "Reguler",
								"price"	: 100000
							},
							{
								"type"	: "Yes",
								"price"	: 20000
							}
						]
					}
				]
			}
		]
	}
	"""
	try:
		# declare untuk result akhir dari api
		result = []
		
		# cek requestnya dapat atau tidak
		try:
			# pengecekan sudah ada delivery address atau belum
			request = frappe.request.data.decode("utf-8")
			request = json.loads(request)
		except:
			return result

		# api untuk mengetahui cost dari dan ke territory
		url_token = get_url_and_token()

		if len(request.get("supplier_item", [])) > 0:
			# request per supplier
			for request_supplier_item in request.get("supplier_item"):
				from_territory = request_supplier_item.get("from_territory", "")
				to_territory = request.get("to_territory", "")

				if from_territory != "" and to_territory != "":
					# ambil delivery area yang tersedia di db
					delivery_areas = get_delivery_area(from_territory=from_territory, to_territory=to_territory)

					if len(delivery_areas) > 0:
						# compile item berdasarkan delivery method yang tersedia
						items = get_items(items=request_supplier_item.get("item", []))
						if items is not None:
							delivery_method = {
								"supplier"				: request_supplier_item.get("supplier", None),
								"available_delivery"	: []
							}
							available_delivery = []

							for delivery_area in delivery_areas:
								# request per delivery method dan per supplier
								try:
									if delivery_area['origin_id'] is not None and delivery_area['destination_id'] != "":
										response = request_to_third_party(url_token=url_token[delivery_area['type_code']], delivery_area=delivery_area, items=items)
										if response != dict():
											if response['message']['code'] == 200:
												if len(response['message']['data']) > 0:
													# delivery
													price_list = []
													muat_delivery = {
														"delivery_method"	: delivery_area['type'],
														"image"				: url_token[delivery_area['type_code']]['image'],
														"pricelist"			: price_list
													}

													for muat_data in response['message']['data']:
														# harusnya cuma akan ngeloop 2 data saja dari muatnya
														if muat_data['service_type'] == "Using Pickup":
															# ambil yang using pickup saja
															# NOTE ANTZ: can_cod di hardcore 0 karena muat tidak bisa cod, sedangkan FE butuh field ini
															price_list.append({
																"type"				: muat_data['service_type'],
																"from_territory"	: muat_data['from_territory'],
																"to_territory"		: muat_data['to_territory'],
																"price"				: muat_data['grand_total'],
																"can_cod"			: 0,
																"etd_from"			: 0,
																"etd_thru"			: 0,
																})
														else:
															# abaikan yang bukan using pickup
															pass

													if len(price_list) > 0:
														available_delivery.append(muat_delivery)
													else:
														# jika price listnya tidak ada
														pass
												else:
													# tidak ada data dari muat
													pass
											else:
												# gagal dari muat
												pass
										else:
											# responsenya kosong
											pass
									else:
										delivery_cost = get_delivery_cost(from_territory=delivery_area['origin_territory'], to_territory=to_territory)
										if delivery_cost is not None:
											price = []
											price = calculate_price_manual(delivery_cost=delivery_cost, items=items)

											internal_delivery = {
												"delivery_method"	: delivery_area['type'],
												"image"				: url_token[delivery_area['type_code']]['image'],
												"pricelist"			: [
													{
														"type"				: "Internal",
														"can_cod"			: delivery_cost.get("can_cod") or 0,														"from_territory"	: delivery_cost.from_territory,
														"to_territory"		: delivery_cost.to_territory,
														"price"				: price,
														"etd_from"			: delivery_cost.get("estimated_from") or 0,
														"etd_thru"			: delivery_cost.get("estimated_to") or 0,
													}
												]
											}
											available_delivery.append(internal_delivery)
										else:
											pass
								except:
									frappe.log_error(frappe.get_traceback(), "Error: API Get Delivery Request to Third Party")

							delivery_method['available_delivery'] = available_delivery
							# append ke result
							if len(delivery_method['available_delivery']) > 0:
								result.append(delivery_method)
							else:
								pass

						else:
							return
					else:
						# tidak ditemukan delivery areanya
						pass
				else:
					# tidak ditemukan from and to territorynya
					pass
		else:
			# tidak ditemukan supplier itemnya
			pass
		return success_format(result)
	except:
		frappe.log_error(frappe.get_traceback(), "Error: API Get Delivery")
		return error_format(_("An error occurred with the server, please try again in a few minutes. Thank you!"))

def calculate_price_manual(delivery_cost, items):
	"""
	pake itemnya muat cargo karena perhitungan mirip muat_cargo
	items = 
	{
		"muat_cargo" : [
			{
				"description": "Iphone 12 Pro Max",
				"weight": 2.0,
				"length": 0.0,
				"width": 0.0,
				"height": 0.0,
				"qty": 1.0,
				"volume": 0.0
			},
			{
				"description": "Iphone 11",
				"weight": 1.0,
				"length": 0.0,
				"width": 0.0,
				"height": 0.0,
				"qty": 2.0,
				"volume": 0.0
			}
		]
	}
	"""
	price_list = []
	selling_price = 0
	for item in items['muat_cargo']:
		weight_in_kgv = (item['length'] * item['width'] * item['height']) / delivery_cost.conversion_to_kgv
		weight_taken_by_system = weight_in_kgv if weight_in_kgv > item['weight'] else item['weight']

		selling_price += weight_taken_by_system * delivery_cost.selling_price_in_kg
	return selling_price

def get_delivery_cost(from_territory, to_territory):
	result = None
	try:
		# perlu cari atas atasnya dari from dan to territory
		from_territory = frappe.get_doc("Territory", from_territory)
		from_territory_parent = frappe.get_all("Territory", fields=["name", "type"], filters=[['lft', '<=', from_territory.lft], ['rgt', '>=', from_territory.rgt], ['type', 'in', ['Subdistrict', 'District', 'City']]])

		to_territory = frappe.get_doc("Territory", to_territory)
		to_territory_parent = frappe.get_all("Territory", fields=["name", "type"], filters=[['lft', '<=', to_territory.lft], ['rgt', '>=', to_territory.rgt], ['type', 'in', ['Subdistrict', 'District', 'City']]])

		for ftp in from_territory_parent:
			for ttp in to_territory_parent:
				# ambil delivery costnya jika ada
				delivery_costs = frappe.get_all("Delivery Cost", fields="name", filters=[['from_territory', '=', ftp['name']], ['to_territory', '=', ttp['name']]])
				if len(delivery_costs) > 0:
					# jika ada maka 
					result = frappe.get_doc("Delivery Cost", delivery_costs[0]['name'])
					break
				else:
					pass
			
			# sudah ditemukan delivery costnya
			if result is not None:
				break
	except:
		# jika from dan to territory tidak ada di database
		frappe.log_error(frappe.get_traceback(), "Error: API Delivery Get Delivery Cost")

	return result

def get_url_and_token():
	url_token = {}
	try:
		delivery_methods = frappe.get_all("Delivery Method", fields="name, image, server, token, api_get_price")
		if len(delivery_methods) > 0:
			for delivery_method in delivery_methods:
				method = delivery_method['name'].replace(" ", "_").lower()
				url_token.update({
					method	: {
						"api_get_price"		: "{server}{api}".format(server=delivery_method['server'], api=delivery_method['api_get_price']),
						"token"				: delivery_method['token'],
						"image"				: delivery_method['image']
						}
					})
		else:
			return url_token
	except:
		frappe.log_error(frappe.get_traceback(), "Error: API Delivery Get URL Token")
	return url_token

def get_items(items):
	# declare parameter
	result = dict()

	try:
		# generate item berdasarkan request masing-masing delivery method
		if len(items) > 0:
			# muat cargo
			item_muat_cargo = []

			for item in items:
				# append item untuk cargo muat
				# ini format request ke cargo muat saat check harga
				item_muat_cargo.append({
					"description"	: item.get('item_name', ''),
					"weight"		: float(item.get('item_weight', 0)),
					"length"		: float(item.get('length', 0)),
					"width"			: float(item.get('width', 0)),
					"height"		: float(item.get('height', 0)),
					"qty"			: float(item.get('qty', 0)),
					"volume"		: float(item.get('length', 0)) * float(item.get('width', 0)) * float(item.get('height', 0))
				})

			if len(item_muat_cargo) > 0:
				result['muat_cargo'] = item_muat_cargo
			else:
				pass
		else:
			# jika tidak ditemukan item sama sekali
			return None
	except:
		frappe.log_error(frappe.get_traceback(), "Error: API Delivery Get Items")

	return result

def get_delivery_area(from_territory, to_territory):
	"""
	from dan to territory ini pasti yang paling bawah (subdistrict)
	"""
	result = []
	try:
		# perlu cari atas atasnya dari from dan to territory
		from_territory = frappe.get_doc("Territory", from_territory)
		from_territory_parent = frappe.get_all("Territory", fields=["name", "type"], filters=[['lft', '<=', from_territory.lft], ['rgt', '>=', from_territory.rgt], ['type', 'in', ['Subdistrict', 'District', 'City']]])

		to_territory = frappe.get_doc("Territory", to_territory)
		to_territory_parent = frappe.get_all("Territory", fields=["name", "type"], filters=[['lft', '<=', to_territory.lft], ['rgt', '>=', to_territory.rgt], ['type', 'in', ['Subdistrict', 'District', 'City']]])

		delivery_area_types = frappe.db.sql("""
			SELECT type
			FROM `tabDelivery Area`
			GROUP BY type
			""", as_dict=True)
		delivery_method = []
		used_delivery_method = []
		if len(delivery_area_types) > 0:
			# methodnya
			for types in delivery_area_types:
				delivery_method.append(types['type'])

			for ftp in from_territory_parent:
				for ttp in to_territory_parent:
					# cek jika sudah ketemu semua maka keluar
					if len(delivery_method) == 0:
						break
					else:
						pass

					# mencoba cari delivery area
					delivery_areas = frappe.db.sql("""
						SELECT
							a.type AS type,
							a.delivery_territory AS origin_territory,
							a.origin_id AS origin_id,
							b.delivery_territory AS destination_territory,
							b.destination_id AS destination_id
						FROM `tabDelivery Area` a
						INNER JOIN `tabDelivery Area` b
						ON
							a.type = b.type
							AND a.delivery_territory = %(from_territory)s
							AND b.delivery_territory = %(to_territory)s
							AND a.delivery_territory != b.delivery_territory
							AND a.type IN %(delivery_method_found)s
						GROUP BY
							type
						""", {
						"from_territory"			: ftp['name'],
						"to_territory"				: ttp['name'],
						"delivery_method_found"		: delivery_method
						}, as_dict=True)
					if len(delivery_areas) > 0:
						for da in delivery_areas:
							# hapus delivery method yang sudah ditemukan
							delivery_method.remove(da['type'])
							used_delivery_method.append(da['type'])

							da.update({
								"type_code"	: da['type'].replace(" ", "_").lower()
								})

							result.append(da)
					else:
						pass
		else:
			# jika tidak ada type berarti tidak ada delivery area sama sekali
			pass

		# tambahan baru jika menggunakan delivery cost
		result = add_delivery_method_that_uses_manual_formula(methods=result, used_delivery_method=used_delivery_method)
	except:
		# jika from dan to territory tidak ada di database
		frappe.log_error(frappe.get_traceback(), "Error: API Delivery Get Delivery Area")

	return result

def add_delivery_method_that_uses_manual_formula(methods, used_delivery_method):
	# tambahkan delivery method yang tidak menggunakan delivery area
	delivery_methods = frappe.get_all("Delivery Method", fields="name", filters=[['server', '=', '-'], ['token', '=', '-'], ['name', 'NOT IN', used_delivery_method]])
	if len(delivery_methods) > 0:
		for delivery_method in delivery_methods:
			if delivery_method['name'] == "Wijaya Online Indonesia":
				# asal alamat pengiriman dari store settings
				methods.append({
					"type"						: delivery_method['name'],
					"type_code"					: delivery_method['name'].replace(" ", "_").lower(),
					"origin_territory"			: frappe.get_value("Store Settings", "Store Settings", "from_territory"),
					"origin_id"					: None,
					"destination_territory"		: None,
					"destination_id"			: None
					})
			else:
				# delivery method yang lainnya
				pass
	else:
		# tidak ada delivery method yang menggunakan delivery cost
		pass
	return methods

def request_to_third_party(url_token, delivery_area, items):
	response = dict()
	try:
		if delivery_area['type'] == "Muat Cargo":
			header = {
				"Authorization"		: url_token['token']
			}
			body = {
				"pickup": {
					"name": delivery_area['origin_id']
				},
				"dropoff": {
					"name": delivery_area['destination_id']
				},
				"itemsData": items['muat_cargo']
			}

			# request ke muat
			r = get_request_session()
			res = r.post(url_token['api_get_price'], headers=header, data=frappe.as_json(body))
			response = res.json()
		else:
			# delivery method lainnya
			pass
	except:
		# gagal ketika request
		frappe.log_error(frappe.get_traceback(), "Error: API Delivery Request to Third Party")

	return response