import http.server
import socketserver
import os
import requests
import sys

PORT = 8080
#whitelist = ["","0.0.0.0"]
countries = ["QA"]


if len(sys.argv)<2:
    print("[    USAGE: server.py <./path_to_serve>  ]")
    exit()

path = sys.argv[1]

if os.path.isdir(path) == False:
    print("Path not found")
    exit()

web_dir = os.path.join(os.path.dirname(__file__), path)
os.chdir(web_dir)


def IP2Country(ip):
    response = requests.get("https://geolocation-db.com/json/" + ip + "&position=true").json()
    return response['country_code']

class MyHandler(http.server.SimpleHTTPRequestHandler):
    #def handle_one_request(self):
        #print(self.request.getpeername()[0])
        #return http.server.SimpleHTTPRequestHandler.handle_one_request(self)
    def do_GET(self):
        if IP2Country(self.request.getpeername()[0]) not in countries:
        #if self.request.getpeername()[0] not in whitelist:
            self.send_response(302)
            self.send_header('Location', 'https://www.google.com/404.html')
            self.end_headers()
        else:
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()

httpd = socketserver.TCPServer(("0.0.0.0", PORT), MyHandler)
print("serving at port", PORT)
httpd.serve_forever()

