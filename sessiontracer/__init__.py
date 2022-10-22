"""
Session Tracer library
~~~~~~~~~~~~~~~~~~~~~
Session Tracer is wrapper library for Request's session library object.

Basic GET usage:
   >>> import requests
   >>> from sessiontracer import SessionTracer
   >>> session = SessionTracer(debug_level="DEBUG")
   >>> session.request(method="GET", url="http://localhost:3010", timeout=10, verify=False)
   >>> session.get(method="POST", url="https://localhost:3010")
    DEBUG:SessionTracer:[604619e5-ddd8-459a-8840-0db513a41b13] 	- START -	 GET - http://localhost:3010 (verify=False|timeout=10)
	DEBUG:SessionTracer:[604619e5-ddd8-459a-8840-0db513a41b13] 	- END   -	 200 (OK) - 2195 microseconds
	DEBUG:SessionTracer:[3d99943b-4a27-47c5-b9fa-cc1e3ea2dc12] 	- START -	 GET - https://localhost:3010 (verify=None|timeout=None)
	ERROR:SessionTracer:[3d99943b-4a27-47c5-b9fa-cc1e3ea2dc12] 	- FATAL -	 HTTPSConnectionPool(host='localhost', port=3010): Max retries exceeded with url: / (Caused by SSLError(SSLError(1, '[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1056)')))
   >>> print("Errors occurred in session:")
   >>> for req, ex in session.errors():
   >>>     print(f"Request {req.request_options.request_identifier} - {req.request_options.method} {req.request_options.url}")
	Request 3d99943b-4a27-47c5-b9fa-cc1e3ea2dc12 - GET https://localhost:3010
"""

from .tracer import SessionTracer
