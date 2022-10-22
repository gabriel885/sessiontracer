"""
sessiontracer.models
--------------
This module contains data models for sessiontracer library
"""

import json
import uuid
from typing import Dict, Union

import requests

from .constants import MAX_REQUEST_TIMEOUT, MIN_REQUEST_TIMEOUT
from .exceptions import InvalidRequestException


class METHOD:
	GET = "GET"
	POST = "POST"
	DELETE = "DELETE"
	PUT = "PUT"
	PATCH = "PATCH"


class RequestOptions(object):
	"""
	Request Options is a wrapper for arguments that are passed to public requests.Session methods such as get/post/request etc.
	It's similar to PreparedRequest but intended for tracer's use
	"""
	
	def __init__(
			self,
			method: str,
			url: str,
			headers: Dict,
			data: Dict,
			request_timeout: float,
			cookies: Dict,
			verify_ssl: bool
	):
		self.method: str = method
		self.url: str = url
		self.verify_ssl: bool = verify_ssl
		self.request_timeout: float = request_timeout
		
		self._headers: dict = headers
		self._data: Union[dict, bytes, bytearray] = data
		self._cookies: dict = cookies
		
		self.request_identifier: uuid.UUID = uuid.uuid4()
		
		self._validate()
	
	def _validate(self):
		if self.method not in vars(METHOD).keys():
			raise InvalidRequestException(f"Request method {self.method} is not valid!")
		if isinstance(self.request_timeout, (float, int)) and not MIN_REQUEST_TIMEOUT <= self.request_timeout <= MAX_REQUEST_TIMEOUT:
			raise InvalidRequestException(f"Request timeout {self.request_timeout} is not in range [{MIN_REQUEST_TIMEOUT} - {MAX_REQUEST_TIMEOUT}]!")
	
	def clean_headers(self):
		self._headers.clear()
	
	def update_headers(self, headers: Dict):
		self._headers.update(headers)
	
	def _is_payload_json(self):  # Todo: move to utils
		try:
			json.dumps(self._data)
			return True
		except TypeError:
			return False
	
	def _prepare_cookies(self, options) -> Dict:
		if self._cookies:
			options.update({"cookies": self._cookies})
		return options
	
	def _prepare_payload(self, options) -> Dict:
		if self.method == METHOD.GET:
			options.update({"params": self._data})
		elif self.method == METHOD.POST:
			if self._is_payload_json():
				options["json"] = self._data
				self.update_headers({"Content-Type": "application/json"})
		# Todo: handle data argument for non-json requests
		else:
			raise NotImplementedError(f"Method {self.method} is not implemented!")
		return options
	
	def _prepare_headers(self, options) -> Dict:
		if self._headers:
			options.update({"headers": self._headers})
		return options
	
	def to_request_arguments(self) -> Dict:
		options = {
			"method": self.method,
			"url": self.url,
			"headers": self._headers or {},
			"timeout": self.request_timeout,
			"verify": self.verify_ssl
		}
		self._prepare_cookies(options)
		self._prepare_payload(options)
		self._prepare_headers(options)  # Todo: add tests in case _prepare_headers is not last!
		return options
	
	@staticmethod
	def to_object(options: Dict):
		return RequestOptions(
			method=options.get("method"),
			url=options.get("url"),
			headers=options.get("headers", {}),
			data=options.get("data", {}),
			request_timeout=options.get("timeout"),
			cookies=options.get("cookies", {}),
			verify_ssl=options.get("verify")
		)


class RequestError(object):
	def __init__(self, request: RequestOptions, response: requests.Response = None):
		self.request_options = request
		self.response = response
