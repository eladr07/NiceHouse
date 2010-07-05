import threading

# todo : add logging!!

class Worker:
    
    def __init__(self, func):
        super(Worker, self).__init__()
        # lock used to make the list synchronized
        self._lock = threading.Lock()
        # the list of items
        self._list = []
        # the function to run for each item
        self._func = func
        #event to activate/pause the worker
        self._event = threading.Event()
        
    def add(self, item):
        try:
            self._lock.acquire()
            self._list.append(item)
        finally:
            self._lock.release()
            
        self._event.set()
        
    def start(self):
        while (True):
            try:
                # wait for incoming items
                self._event.wait()
                
                try:
                    self._lock.acquire()
                    item = self._list.pop(0)
                    self._lock.release()
                except IndexError:
                    self._lock.release()
                    self._event.clear()
                else:
                    self._func(item)
            except:
                continue