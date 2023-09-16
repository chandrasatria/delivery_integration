# -*- coding: utf-8 -*-
# Copyright (c) 2020, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

import json
from frappe.utils import get_request_session
from frappe import _
from api_integration.validation import error_format, success_format


"Delivery Method diisi dengan name dari delivery method"
@frappe.whitelist(allow_guest=False)
def get_tracking(awb,delivery_method):
	try:
		# declare untuk result akhir dari api
		result = []
		# api untuk mengetahui cost dari dan ke territory
		url_token = get_url_and_token(delivery_method_name = delivery_method)
		method = delivery_method.replace(" ", "_").lower()
		# jika muat, (sicepat ,jne)
		if not url_token:
			frappe.log_error(frappe.get_traceback(), "Error: API Get Tracking")
			return error_format(_("An error occurred with the server, please try again in a few minutes. Thank you!"))	
		print(url_token[method])
		result = request_to_third_party_tracking(url_token[method],awb)
		return success_format(result)
	except:
		frappe.log_error(frappe.get_traceback(), "Error: API Get Tracking")
		return error_format(_("An error occurred with the server, please try again in a few minutes. Thank you!"))

def get_url_and_token(delivery_method_name = ""):
	url_token = {}
	try:
		with_filter = [["name","=",delivery_method_name]] if delivery_method_name else None 
		delivery_methods = frappe.get_all("Delivery Method", fields="name, image, server, token, api_get_tracking", filters=with_filter)
		print(delivery_methods)
		if len(delivery_methods) > 0:
			for delivery_method in delivery_methods:
				print("a")
				method = delivery_method['name'].replace(" ", "_").lower()
				if not delivery_method['api_get_tracking']:
					frappe.log_error(frappe.get_traceback(), "Error: API Get Tracking is None")
				url_token.update({
					method	: {
						"api_get_tracking"		: "{server}{api}".format(server=delivery_method['server'], api=delivery_method['api_get_tracking']),
						"token"					: delivery_method['token'],
						"image"					: delivery_method['image'],
						"delivery_method"		: delivery_method['name']
						}
					})
			return url_token
		else:
			return url_token
	except:
		frappe.log_error(frappe.get_traceback(), "Error: API Tracking Get URL Token")
		print("errr")

def request_to_third_party_tracking(url_token_dict,awb):
	final_response = dict()
	print(url_token_dict)
	try:
		if url_token_dict["delivery_method"] == "Muat Cargo":
			header = {
				"Authorization"		: url_token_dict['token']
			}
			body = {
				"identifier" : "Get Load Order Update",
				"load_order" : awb
			}
			# request ke muat
			r = get_request_session()
			res = r.post(url_token_dict['api_get_tracking'], headers=header, data=frappe.as_json(body))
			response = res.json()
			print(response)
			print("------------")
			final_response = muat_converter(response=response)
			print(final_response)

			
		else:
			# Kalo tidak ada coba cari di
			final_response = search_and_convert_delivery_tracking(delivery_receipt=awb)
	except:
		# gagal ketika request
		frappe.log_error(frappe.get_traceback(), "Error: API Tracking Request to Third Party")
		frappe

	return final_response


""" pilih salah satu delivery receipt atau external id """
def search_and_convert_delivery_tracking(delivery_receipt="",external_id=""):
	response = []
	fga_delivery_tracking = frappe.get_list("Delivery Tracking",fields="*", or_filters=[["delivery_receipt","=",delivery_receipt],["external_id","=",external_id]], order_by = "posted_on DESC")
	print(fga_delivery_tracking)
	for item in fga_delivery_tracking:
		temp_dict = {"note" : item["note"] or "", "posted_on" : item["posted_on"] or ""}
		response.append(temp_dict)
	return response

# MUAT------------------

def muat_converter(response):
	converted_response = []
	for item in response["message"]["data"]:
		note = item
		temp_dict = {"note" : item["status"] + " - " + item["remarks"]  or "", "posted_on" : item["update_on"] or ""}
		converted_response.append(temp_dict)
		print(item["update_on"])
	
	return converted_response




# -- Contoh Response Muat
""" {
    "message": {
        "code": 200,
        "data": [
            {
                "name": "82f77a584e",
                "creation": "2021-02-17 14:19:44.255247",
                "modified": "2021-02-17 14:27:03.192948",
                "modified_by": "ricardo.wardhana@gmail.com",
                "owner": "sapan@muat.co",
                "docstatus": 0,
                "parent": null,
                "parentfield": null,
                "parenttype": null,
                "idx": 0,
                "load_order": "C21AGELG1852",
                "customer_email": "ricardo.wardhana@gmail.com",
                "update_on": "2021-02-17 14:27:03.403864",
                "confirmation_deadline": "2021-02-18 14:19:44.307755",
                "status": "Completed",
                "tracker": "Wardhana",
                "remarks": "",
                "index_number": 1,
                "_user_tags": null,
                "_comments": null,
                "_assign": null,
                "_liked_by": null
            },
            {
                "name": "21353d72e5",
                "creation": "2021-02-17 14:19:03.704986",
                "modified": "2021-02-17 14:19:03.704986",
                "modified_by": "sapan@muat.co",
                "owner": "sapan@muat.co",
                "docstatus": 0,
                "parent": null,
                "parentfield": null,
                "parenttype": null,
                "idx": 0,
                "load_order": "C21AGELG1852",
                "customer_email": "ricardo.wardhana@gmail.com",
                "update_on": "2021-02-17 14:19:03.557388",
                "confirmation_deadline": null,
                "status": "On Delivery",
                "tracker": "System",
                "remarks": "Delivery at 2021-02-17 14:19:03.557540",
                "index_number": 0,
                "_user_tags": null,
                "_comments": null,
                "_assign": null,
                "_liked_by": null
            }
        ]
    }
}"""