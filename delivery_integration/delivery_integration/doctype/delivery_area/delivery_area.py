# -*- coding: utf-8 -*-
# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class DeliveryArea(Document):
	def before_insert(self):
		self.duplicate_delivery_area()

	def duplicate_delivery_area(self):
		delivery_areas = frappe.get_list("Delivery Area", fields="name", filters=[['type', '=', self.type], ['delivery_territory', '=', self.delivery_territory], ['name', '!=', self.name]])
		if len(delivery_areas) > 0:
			frappe.throw(_("""Duplicate Delivery Area. Please check here <a href="/desk#Form/Delivery%20Area/{delivery_area}">{delivery_area}</a>""".format(delivery_area=delivery_areas[0]['name'])))
		else:
			return