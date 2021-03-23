from http.server import HTTPServer, SimpleHTTPRequestHandler

class MyHandler(SimpleHTTPRequestHandler):

	def do_GET(self):
		mytxt = "bluefuzzy708"
		response = f'<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><h1>{mytxt}!</h1></body></html>'
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.send_header("Content-length", len(response))
		self.end_headers()
		self.wfile.write(str.encode(response))

print("hello World!")
httpd = HTTPServer(('0.0.0.0', 8081), MyHandler)

httpd.serve_forever()