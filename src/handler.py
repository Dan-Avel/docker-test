import os
from http.server import HTTPServer, CGIHTTPRequestHandler
os.chdir(".")
server_object=HTTPServer(server_address=("", 8000), RequestHandlerClass=CGIHTTPRequestHandler)
print("hello World!")
server_object.serve_forever()