#!/usr/bin/python3
import cherrypy
#import requests
import os
import json


class Root(object):
    @cherrypy.expose
    def index(self):        
        return 'No service found'

    @cherrypy.expose
    def post_orders_meli(self):
        postdata = cherrypy.request.body.read()

        '''
        postdata = cherrypy.request.body.read()
        req = cherrypy.request
        print (req)
        incoming_dict_object = req.json
        print(incoming_dict_object)

        cherrypy.log("bang")
        try:
            cherrypy.log("kaboom!")
        except Exception as e:
            cherrypy.log("kaboom!", str(e) ,traceback=True)
        return "hello world"
        '''

        


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port':8080,'server.thread_pool': 150,'server.socket_queue_size': 100,'log.screen': True,})
    cherrypy.tree.mount(Root(), '/')
    cherrypy.engine.start()
    #cherrypy.engine.block()
    
    

