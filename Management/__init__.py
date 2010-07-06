from worker import Worker
from threading import Thread

def calc_demand(demand):
    demand.calc_sales_commission()
    
def calc_salary(salary):
    salary.calculate()
    salary.save()

demand_worker = Worker(calc_demand)
salary_worker = Worker(calc_salary)

demand_thread = Thread(target = lambda: demand_worker.start())
demand_thread.setDaemon(True)
demand_thread.start()

salary_thread = Thread(target = lambda: salary_worker.start())
salary_thread.setDaemon(True)
salary_thread.start()
