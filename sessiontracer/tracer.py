"""
sessiontracer.tracer
--------------
This module contains tracer wrappers for Request's session object
"""

import functools
import inspect
import logging
import sys
from typing import Dict, List, Tuple

import requests

from .models import RequestError, RequestOptions

logging.basicConfig(stream=sys.stdout)


class SessionTracer(requests.Session):
	"""
	Tracer responsible for tracing session requests
	"""
	
	SESSION_METHODS = ["request"]
	
	def __init__(self, debug_level: str = "ERROR"):
		super().__init__()
		self._logger = logging.getLogger(SessionTracer.__name__)
		self._logger.setLevel(debug_level)
		self._trace_session()
		self._errors: List[Tuple[RequestError, Exception]] = []
	
	@staticmethod
	def _is_callable(attr: object) -> bool:
		return hasattr(attr, '__call__')
	
	@staticmethod
	def _handle_function_arguments(*args, **kwargs) -> Dict:
		if args:
			kwargs.update({  # mandatory parameters
				"method": args[0],
				"url": args[1]
			})
		return kwargs
	
	def _trace_session(self):
		# override traceable session methods
		for name, method in inspect.getmembers(self, lambda x: self._is_callable(x) and x.__name__ in self.SESSION_METHODS):
			setattr(self, name, self.trace(method))
	
	def trace(self, func):
		
		@functools.wraps(func)
		def _trace(*args, **kwargs):
			try:
				arguments = self._handle_function_arguments(*args, **kwargs)
				options = RequestOptions.to_object(arguments)
			except Exception as ex:
				self._logger.error(f"Function call for {func.__name__} got an exception. Error is: {ex}")
				raise
			
			try:
				self._trace_start(options)
				response = func(**options.to_request_arguments())
				response.raise_for_status()
				self._trace_end(options, response)
				return response
			except Exception as ex:
				self._trace_exception(options, ex)
		
		return _trace
	
	def _trace_start(self, options: RequestOptions):
		"""
		Trace requests. In case of an exception raise Exception
		:return:
		"""
		self._logger.debug(f"[{options.request_identifier}] \t- START -\t {options.method} - {options.url} (verify={options.verify_ssl}|timeout={options.request_timeout})")
	
	def _trace_end(self, options: RequestOptions, response: requests.Response):
		"""
		End tracing
		:para options: {RequestOptions} Request's options
		:param response: {requests.Response} Request's response object
		:return:
		"""
		self._logger.debug(f"[{options.request_identifier}] \t- END   -\t {response.status_code} ({response.reason}) - {f'{response.elapsed.microseconds} microseconds'}")
	
	def _trace_exception(self, options: RequestOptions, ex: Exception):
		"""
		End tracing faced an exception
		:param options: {RequestOptions} Request's options
		:param ex: {Exception} Exception occurred
		:return:
		"""
		self._logger.error(f"[{options.request_identifier}] \t- FATAL -\t {ex}")
		self._errors.append((RequestError(options), ex))
	
	def errors(self) -> List[Tuple[RequestError, Exception]]:
		"""
		Get list of occurred exceptions throw
		:return:
		"""
		return self._errors
