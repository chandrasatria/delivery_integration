# -*- coding: utf-8 -*-
# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DeliveryTracking(Document):
	def before_insert(self):
		self.fill_default_value()

	
	def fill_default_value(self):
		if not self.posted_on:
			self.posted_on = frappe.utils.now()
