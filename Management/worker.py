import threading, logging

class Worker:
    
    def __init__(self, func):
        # lock used to make the list synchronized
        self._lock = threading.Lock()
        # the list of items
        self._list = []
        # the function to run for each item
        self._func = func
        #event to activate/pause the worker
        self._event = threading.Event()
        
    def add(self, item):
        added = False
        
        logger = logging.getLogger('worker')
        
        try:
            self._lock.acquire()
            if item not in self._list:
                self._list.append(item)
                added = True
                logger.info('added item to the list: item - %s' % item)
            else:
                logger.warning('tried to add item that is already in the list: item - %s' % item)
        finally:
            self._lock.release()
        
        # notify the worker he can start iterating the list
        self._event.set()
        
        return added
    
    def start(self):
        logger = logging.getLogger('worker')
        
        while (True):
            try:
                # wait for incoming items
                self._event.wait()
                
                logger.info('starting to iterate over the list - %s items' % len(self._list))
                
                try:
                    self._lock.acquire()
                    item = self._list.pop(0)
                    self._lock.release()
                except IndexError:
                    self._lock.release()
                    self._event.clear()
                    logger.info('ran out of items, waiting for new items')
                else:
                    # execute func for the current item
                    try:
                        self._func(item)
                    except:
                        logger.exception('exception while executing func for item %s' % item)
                    else:
                        logger.info('executed func successfully: item - %s' % item)
            except:
                logger.exception('general error, continuing')
                continue