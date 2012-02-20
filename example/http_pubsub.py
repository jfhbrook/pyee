# gevent + bottle http pubsub
# open a term and run: http://localhost:8082/sub
# another term and issue: curl -x 'msg=hello' http://localhost:8082/pub

import gevent
import gevent.queue

from pyee import EventEmitter
from bottle import route, run, debug, abort, request, response, get, post

bus = EventEmitter()

@post("/pub")
def post_messsage():
    msg = request.POST['msg']
    bus.emit('message', msg)

@get("/sub")
def broadcast():
    glue = gevent.queue.Queue()
    yield 'Connected\n'
    def c(m):
        glue.put(m)
    bus.on_event('message', c)
    while(True):
        m = glue.get(block=True)
        yield "%s\n" % m

debug(True)
run(host="localhost", port=8082, server='gevent')

