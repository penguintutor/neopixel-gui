from bottle import Bottle, get, run, ServerAdapter
# Provides SSL for Bottle
# SSL info from https://github.com/mfm24/miscpython/blob/master/bottle_ssl.py
# openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes

class SSLWSGIRefServer(ServerAdapter):

    def set_certificate(self, certificate):
        self.certificate = certificate

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        import ssl
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        srv = make_server(self.host, self.port, handler, **self.options)
        srv.socket = ssl.wrap_socket (
        	srv.socket,
        	certfile=self.certificate,  # path to certificate
        	server_side=True)
        srv.serve_forever()