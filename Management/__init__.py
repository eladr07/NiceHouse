import reversion
from worker import Worker
from threading import Thread, enumerate

initialize = True

for thread in enumerate():
    if thread.name in ['demand thread','salary thread']:
        initialize = False
        break

if initialize:
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