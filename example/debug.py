from sessiontracer import SessionTracer

if __name__ == "__main__":
	session = SessionTracer(debug_level="DEBUG")
	session.request(method="GET", url="http://localhost:3010", timeout=10, verify=False)
	session.get(method="POST", url="https://localhost:3010")
	
	print("Errors occurred in session:")
	for req, ex in session.errors():
		print(f"Request {req.request_options.request_identifier} - {req.request_options.method} {req.request_options.url}")
