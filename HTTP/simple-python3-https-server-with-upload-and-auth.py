#!/usr/bin/env python3

import os
import http.server
import urllib.parse
import cgi
import shutil
import mimetypes
import sys
import base64
import ssl
import io

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP request handler with GET/HEAD/POST commands.
    This serves files, supports file uploads via HTML form & curl, and includes basic authentication.
    """
    server_version = "SimpleHTTPWithUpload/" 

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Test"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global key
        auth_header = self.headers.get('Authorization')
        if auth_header is None:
            print("[AUTH] No Authorization header received.")
            self.do_AUTHHEAD()
            self.wfile.write(b'No auth header received')
        elif auth_header == 'Basic ' + key:
            print(f"[AUTH] Successful login with {auth_header}")
            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()
        else:
            print(f"[AUTH] Failed authentication attempt: {auth_header}")
            self.do_AUTHHEAD()
            self.wfile.write(b'Not authenticated')

    def do_POST(self):
        """Handles file uploads and saves them with their original filename."""
        content_type, pdict = cgi.parse_header(self.headers.get('Content-Type'))
        
        if content_type == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            fields = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            
            if 'file' not in fields or not fields['file'].filename:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'No file uploaded')
                return

            file_item = fields['file']
            filename = os.path.basename(file_item.filename)  # Extract filename safely

            with open(filename, "wb") as f:
                f.write(file_item.file.read())

            self.send_response(200)
            self.end_headers()
            self.wfile.write(f'File "{filename}" uploaded successfully'.encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            try:
                listing = os.listdir(path)
            except OSError:
                self.send_error(403, "Permission denied")
                return None
            html = "<html><body><h2>Directory listing for {}</h2><ul>".format(self.path)
            for name in listing:
                fullname = os.path.join(path, name)
                displayname = name + "/" if os.path.isdir(fullname) else name
                html += '<li><a href="{}">{}</a></li>'.format(urllib.parse.quote(name), displayname)
            html += "</ul>"
            # Add HTML file upload form
            html += """
            <h2>Upload a File</h2>
            <form enctype="multipart/form-data" method="post">
                <input type="file" name="file" />
                <input type="submit" value="Upload" />
            </form>
            """
            html += "</body></html>"
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(html.encode())))
            self.end_headers()
            self.wfile.write(html.encode())
            return None
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", mimetypes.guess_type(path)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(os.fstat(f.fileno()).st_size))
        self.end_headers()
        return f

    def translate_path(self, path):
        path = urllib.parse.unquote(path)
        path = os.path.normpath(path)
        words = path.split('/')
        words = [w for w in words if w]
        path = os.getcwd()
        for word in words:
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 server.py <port> <username:password>")
        sys.exit(1)

    port = int(sys.argv[1])
    username, password = sys.argv[2].split(":")
    key = base64.b64encode(f"{username}:{password}".encode()).decode('ascii')

    print(f"\n==============================")
    print(f"Server is running on port {port} with authentication")
    print(f"Access the server via:")
    print(f"  Web Browser: https://127.0.0.1:{port}/")
    print(f"  Upload via HTML Form on the web interface")
    print(f"  Upload via CURL:")
    print(f"    curl -u {username}:{password} -F 'file=@example.txt' https://127.0.0.1:{port}/ --insecure")
    print(f"==============================\n")
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.pem")
    httpd = http.server.HTTPServer(("", port), SimpleHTTPRequestHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()
