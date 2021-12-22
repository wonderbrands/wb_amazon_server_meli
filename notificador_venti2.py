#from StringIO import StringIO
from io import StringIO
import unittest
import urllib

import cherrypy

local = cherrypy.lib.httputil.Host('127.0.0.1', 8081, "")
remote = cherrypy.lib.httputil.Host('127.0.0.1',8081, "")

class Root(object):
    @cherrypy.expose
    def index(self):
        return "hello world"

    @cherrypy.expose
    def echo(self, msg):
        return msg

def setUpModule():
    cherrypy.config.update({'environment': "test_suite"})

    # prevent the HTTP server from ever starting
    cherrypy.server.unsubscribe()

    cherrypy.tree.mount(Root(), '/')
    cherrypy.engine.start()
setup_module = setUpModule

def tearDownModule():
    cherrypy.engine.exit()
teardown_module = tearDownModule

class BaseCherryPyTestCase(unittest.TestCase):
    def webapp_request(self, path='/', method='GET', **kwargs):
        headers = [('Host', '127.0.0.1')]
        qs = fd = None

        if method in ['POST', 'PUT']:
            qs = urllib.urlencode(kwargs)
            headers.append(('content-type', 'application/x-www-form-urlencoded'))
            headers.append(('content-length', '%d' % len(qs)))
            fd = StringIO(qs)
            qs = None
        elif kwargs:
            qs = urllib.urlencode(kwargs)

        # Get our application and run the request against it
        app = cherrypy.tree.apps['']
        # Let's fake the local and remote addresses
        # Let's also use a non-secure scheme: 'http'
        request, response = app.get_serving(local, remote, 'http', 'HTTP/1.1')
        try:
            response = request.run(method, path, qs, 'HTTP/1.1', headers, fd)
        finally:
            if fd:
                fd.close()
                fd = None

        if response.output_status.startswith('500'):
            print (response.body)
            raise AssertionError("Unexpected error")

        # collapse the response into a bytestring
        response.collapse_body()
        return response

class TestCherryPyApp(BaseCherryPyTestCase):
    def test_index(self):
        response = self.webapp_request('/')
        self.assertEqual(response.output_status, '200 OK')
        # response body is wrapped into a list internally by CherryPy
        self.assertEqual(response.body, ['hello world'])

    def test_echo(self):
        response = self.webapp_request('/echo', msg="hey there")
        self.assertEqual(response.output_status, '200 OK')
        self.assertEqual(response.body, ["hey there"])

        response = self.webapp_request('/echo', method='POST', msg="hey there")
        self.assertEqual(response.output_status, '200 OK')
        self.assertEqual(response.body, ["hey there"])

if __name__ == '__main__':
    unittest.main()