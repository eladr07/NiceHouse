######## workers setup #########
import logging, inspect

logger = logging.getLogger('commission')

logger.debug('importing...')
logger.debug(inspect.stack())

import reversion
from worker import Worker
from threading import Thread, enumerate

logger.debug(len(enumerate()))

@reversion.revision.create_on_success
def calc_demand(demand):
    demand.calc_sales_commission()
    
@reversion.revision.create_on_success    
def calc_salary(salary):
    salary.calculate()
    salary.save()

demand_worker = Worker(calc_demand)
salary_worker = Worker(calc_salary)

demand_thread = Thread(target = lambda: demand_worker.start(), name='demand thread')
demand_thread.setDaemon(True)
demand_thread.start()

salary_thread = Thread(target = lambda: salary_worker.start(), name='salary thread')
salary_thread.setDaemon(True)
salary_thread.start()