from pyee import EventEmitter
from time import sleep

bus = EventEmitter()

def producer():
    while(True):
        bus.emit("message", "oi")
        sleep(10)

@bus.on('message')
def consumer(msg):
    print msg

def another_consumer(msg):
    print "another consumer: %s" % msg

def main():
    bus.on_event('message', another_consumer)
    producer()

if __name__ == "__main__":
    main()
