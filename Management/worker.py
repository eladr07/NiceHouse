from Queue import Queue, Empty
from threading import Event

class Worker:
    
    def __init__(self, func):
        super(Worker, self).__init__()
        self._queue = Queue()
        self._func = func
        self._event = Event()
        
    def add(self, item):
        self._queue.put(item)
        self._event.set()
        
    def start(self):
        while (True):
            try:
                item = self._queue.get()
                self._func(item)
            except Empty:
                self._event.clear()
                continue
            except:
                continue