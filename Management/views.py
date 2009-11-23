from django.forms.formsets import formset_factory
import settings, inspect
import time
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import inlineformset_factory, modelformset_factory
from django.db.models import Avg, Max, Min, Count
from django.template import RequestContext
from datetime import datetime, date
from forms import *
from django.core import serializers
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from pdf import MonthDemandWriter, MultipleDemandWriter, EmployeeListWriter, EmployeeSalariesWriter, NHEmployeeSalariesWriter, PricelistWriter, BuildingClientsWriter
from mail import mail

def generate_unique_pdf_filename():
    return settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'

@login_required
def index(request):
    return render_to_response('Management/index.html',
                              {'locateHouseForm':LocateHouseForm(),
                               'nhbranches':NHBranch.objects.all()},
                              context_instance=RequestContext(request))
  
@login_required  
def locate_house(request):
    if request.method == 'POST':
        form = LocateHouseForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            try:
                building = project.buildings.get(num=form.cleaned_data['building_num'])
                house = building.houses.get(num=form.cleaned_data['house_num'])
                return HttpResponseRedirect('/projects/%s/buildings/%s/house/%s/type1' % (project.id, building.id, house.id))
            except:
                error = u'לא נמצאה דירה מס %s בבניין מס %s בפרוייקט %s' % (form.cleaned_data['house_num'],
                                                                           form.cleaned_data['building_num'],
                                                                           project)
        return render_to_response('Management/index.html',
                                  {'locateHouseForm':form, 'error':error},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')

@login_required
def limited_direct_to_template(request, permission=None, *args, **kwargs):
    if not permission or request.user.has_perm('Management.' + permission):
        return direct_to_template(request, *args, **kwargs)
    else:
        return HttpResponse('No permission. contact Elad.')

@login_required
def limited_create_object(request, permission=None, *args, **kwargs):
    if kwargs.has_key('model'):
        model = kwargs['model']
    elif kwargs.has_key('form_class'):
        model = kwargs['form_class']._meta.model
    if not permission:
        permission = 'Management.change_' + model.__name__.lower()
    if request.user.has_perm(permission):
        return create_object(request, *args, **kwargs)
    else:
        return HttpResponse('No permission. contact Elad.')
    
@login_required
def limited_delete_object(request, model, object_id, post_delete_redirect, permission=None):
    if not permission:
        permission = 'Management.change_' + model.__name__.lower()
    if request.user.has_perm(permission):
        obj = model.objects.get(pk=object_id)
        obj.delete()
        return HttpResponseRedirect(post_delete_redirect)
    else:
        return HttpResponse('No permission. contact Elad.')
    
@login_required
def limited_object_detail(request, permission=None, *args, **kwargs):
    if not permission or request.user.has_perm('Management.' + permission):
        return object_detail(request, *args, **kwargs)
    else:
        return HttpResponse('No permission. contact Elad.')

@login_required
def limited_update_object(request, permission=None, *args, **kwargs):
    if kwargs.has_key('model'):
        model = kwargs['model']
    elif kwargs.has_key('form_class'):
        model = kwargs['form_class']._meta.model
    if not permission:
        permission = 'Management.change_' + model.__name__.lower()
    if request.user.has_perm(permission):
        return update_object(request, *args, **kwargs)
    else:
        return HttpResponse('No permission. contact Elad.')

@login_required
def limited_object_list(request, permission=None, *args, **kwargs):
    if not permission or request.user.has_perm('Management.' + permission):
        return object_list(request, *args, **kwargs)
    else:
        return HttpResponse('No permission. contact Elad.')
    
@login_required
def house_details(request, id):
    return render_to_response('Management/house_details.html',
                              {'house':House.objects.get(pk=id)},
                              context_instance=RequestContext(request))
@login_required
def signup_details(request, house_id):
    s = House.objects.get(pk=house_id).get_signup()
    if not s:
        return HttpResponse('')
    else:
        return render_to_response('Management/signup_details.html',
                                  {'signup':s},
                                  context_instance=RequestContext(request))

@login_required
def employeecheck_list(request, year=None, month=None):
    if year and month:
        date = datetime(int(year), int(month), 1)
    else:
        date = datetime.now()
    return render_to_response('Management/employeecheck_list.html',
                              {'checks':EmployeeCheck.objects.filter(issue_date__year = date.year, 
                                                                     issue_date__month = date.month),
                                'date':date},
                              context_instance=RequestContext(request))

@permission_required('Management.delete_advancepayment')
def advance_payment_toloan(request, id):
    ap = AdvancePayment.objects.get(pk=id)
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            form.save()
            ap.to_loan()
    else:
        form = LoanForm(initial={'employee':ap.employee.id, 'amount':ap.amount, 'date':ap.date})
   
    return render_to_response('Management/object_edit.html',
                              {'form':form}, context_instance=RequestContext(request))

@login_required
def check_list(request, year=None, month=None):
    if year and month:
        date = datetime(int(year), int(month), 1)
    else:
        date = datetime.now()
    return render_to_response('Management/check_list.html',
                              {'checks':Check.objects.filter(issue_date__year = date.year, 
                                                             issue_date__month = date.month),
                                'date':date},
                              context_instance=RequestContext(request))

@login_required
def check_add(request):
    if request.method == "POST":
        accountForm = AccountForm(request.POST)
        form = CheckForm(request.POST)
        if accountForm.has_changed() and accountForm.is_valid():
            a = accountForm.save()
        else:
            a = None
        if form.is_valid():
            form.save(a)
    else:
        accountForm = AccountForm()
        form = CheckForm()
        
    return render_to_response('Management/check_edit.html', 
                              { 'accountForm':accountForm, 'form':form },
                              context_instance=RequestContext(request))
    
@login_required
def check_edit(request, id):
    c = Check.objects.get(pk=id)
    if request.method == "POST":
        accountForm = AccountForm(request.POST, instance = c.account)
        form = CheckForm(request.POST, instance = c)
        if accountForm.has_changed():
            if accountForm.is_valid() and form.is_valid():
                accountForm.save()
                form.save()
        else:
            if form.is_valid():
                form.save()
    else:
        accountForm = AccountForm()
        form = CheckForm()
        
    return render_to_response('Management/check_edit.html', 
                              { 'accountForm':accountForm, 'form':form },
                              context_instance=RequestContext(request))

def signup_list(request, project_id):
    month = date.today()
    y = int(request.GET.get('year', month.year))
    m = int(request.GET.get('month', month.month))
    month = datetime(y,m,1)
    form = MonthFilterForm(initial={'year':y,'month':m})
    p = Project.objects.get(pk = project_id)
    signups = p.signups(y, m)
    return render_to_response('Management/signup_list.html', 
                          { 'project':p, 'signups':signups, 'month':month, 'filterForm':filterForm },
                          context_instance=RequestContext(request))

@permission_required('Management.add_signup')
def signup_edit(request, id=None, house_id=None, project_id=None): 
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('add')
    else:
        if id:
            signup = Signup.objects.get(pk=id)
            h = signup.house
            form = SignupForm(instance=signup)
        elif house_id:
            h = House.objects.get(pk= house_id)  
            signup = h.get_signup()
            form = signup and SignupForm(instance = signup) or SignupForm()
        if house_id or id:
            form.fields['house'].initial = h.id
            form.fields['building'].initial = h.building.id
            form.fields['project'].initial = h.building.project.id
            form.fields['house'].queryset = h.building.houses.filter(is_deleted=False)
            form.fields['building'].queryset = h.building.project.non_deleted_buildings()
        elif project_id:
            form = SignupForm(initial = {'project':project_id})
        else:
            form = SignupForm()
            
    return render_to_response('Management/signup_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))

@permission_required('Management.change_signup')
def signup_cancel(request, id):
    s = Signup.objects.get(pk=id)
    cancel = s.cancel or SignupCancel()
    if request.method=='POST':
        form = SignupCancelForm(request.POST)
        if form.is_valid():
            s.cancel = form.save()
            s.save()
    else:
        form = SignupCancelForm(instance=cancel)
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))

@permission_required('Management.add_account')
def employee_account(request, id, model):
    employee = model.objects.get(pk=id)
    try:
        acc = employee.account
    except Account.DoesNotExist:
        acc = Account()
    if request.method == 'POST':
        form = AccountForm(data=request.POST, instance=acc) 
        if form.is_valid(): 
            employee.account = form.save()
            employee.save()
    else:
        form = AccountForm(instance=acc)
        
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))

@permission_required('Management.list_demand')
def demand_function(request,id , function):
    d = Demand.objects.get(pk=id)
    function(d)
    return HttpResponse('ok')

    for p_id in [21]:
        for m in range(1,9):
            q = Demand.objects.filter(project__id = p_id, year = 2009, month=m)
            if q.count() == 0:
                continue
            d = q[0]
            for ds in d.statuses.all():
                ds.delete()
            for diff in d.diffs.all():
                diff.delete()
            d.calc_sales_commission()
            d = Demand.objects.get(project__id = p_id, year = 2009, month=m)
            d.finish()
            time.sleep(1)

@permission_required('Management.list_demand')
def demand_calc(request, id):
    d = Demand.objects.get(pk=id)
    c = d.project.commissions
    if c.commission_by_signups or c.c_zilber:
        for d2 in Demand.objects.filter(project = d.project):
            for s in d2.statuses.all():
                s.delete()
            for s in d2.get_sales():
                for scd in s.commission_details.all():
                    for cl in ChangeLog.objects.filter(object_type='SaleCommissionDetail', object_id = scd.id):
                        cl.delete()
                    scd.delete()
            d2.calc_sales_commission()
            demand = Demand.objects.get(pk=d2.id)
            demand.finish()
            time.sleep(1)
    else:
        d.calc_sales_commission()
    return HttpResponseRedirect('/demandsold/?year=%s&month=%s' % (d.year,d.month))

def projects_profit(request):
    month = Demand.current_month()
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    demands, salaries = [], []
    current = date(int(from_year), int(from_month), 1)
    end = date(int(to_year), int(to_month), 1)
    while current <= end:
        q = Demand.objects.filter(year = current.year, month = current.month)
        if q.count() > 0:
            demands.extend(q)
        q = EmployeeSalary.objects.filter(year = current.year, month = current.month)
        if q.count() > 0:
            salaries.extend(q)
        current = date(current.month == 12 and current.year + 1 or current.year, current.month == 12 and 1 or current.month + 1, 1)
    projects = []
    for d in demands:
        if d.project not in projects:
            projects.append(d.project)
    total_income, total_expense, total_profit, avg_relative_expense_income, avg_relative_sales_expense, total_sale_count = 0,0,0,0,0,0
    for p in projects:
        p.sale_count, p.total_income, p.total_expense, p.profit, p.total_sales_amount = 0,0,0,0,0
        p.employee_expense = {}
    for d in demands:
        tax_val = Tax.objects.filter(date__lte=date(d.year, d.month,1)).latest().value / 100 + 1
        for p in projects:
            if p.id == d.project.id:
                total_amount = d.get_total_amount() / tax_val
                sale_count = d.get_sales().count()
                p.total_income += total_amount
                for s in d.get_sales().all():
                    p.total_sales_amount += s.include_tax and s.price or (s.price / tax_val)
                p.sale_count += sale_count
                total_sale_count += sale_count
                total_income += total_amount
                break
    for s in salaries:
        tax_val = Tax.objects.filter(date__lte=date(s.year, s.month,1)).latest().value / 100 + 1
        terms = s.employee.employment_terms
        if not terms: continue
        s.calculate()
        for project, salary in s.project_salary().items():
            for p in projects:
                if p.id == project.id:
                    if not p.employee_expense.has_key(s.employee):
                        p.employee_expense[s.employee]=0
                    fixed_salary = salary
                    if terms.hire_type.id == HireType.SelfEmployed:
                        fixed_salary = salary / tax_val
                    p.employee_expense[s.employee] += fixed_salary
                    p.total_expense += fixed_salary
                    total_expense += fixed_salary
                    break
    project_count = 0
    for p in projects:
        if p.sale_count > 0:
            project_count += 1
        p.relative_income = total_income and (p.total_income / total_income * 100) or 100
        if p.total_expense and p.total_sales_amount:
            p.relative_sales_expense = float(p.total_expense) / p.total_sales_amount * 100
            avg_relative_sales_expense += p.relative_sales_expense
        else:
            if p.total_expense == 0 and p.total_sales_amount == 0: p.relative_sales_expense_str = 'אפס'
            elif p.total_sales_amount == 0: p.relative_sales_expense_str = u'גרעון'
            elif p.total_expense == 0: p.relative_sales_expense_str = u'עודף'
        if p.total_income and p.total_expense:
            p.relative_expense_income = p.total_expense / p.total_income * 100
            avg_relative_expense_income += p.relative_expense_income
        else:
            if p.total_income == 0 and p.total_expense == 0: p.relative_expense_income_str = u'אפס'
            elif p.total_income == 0: p.relative_expense_income_str = u'גרעון'
            elif p.total_expense == 0: p.relative_expense_income_str = u'עודף'
        p.profit = p.total_income - p.total_expense
        total_profit += p.profit
    if project_count:
        avg_relative_expense_income = avg_relative_expense_income / project_count
        avg_relative_sales_expense = avg_relative_sales_expense / project_count
    
    return render_to_response('Management/projects_profit.html', 
                              { 'projects':projects,'from_year':from_year,'from_month':from_month, 
                                'to_year':to_year,'to_month':to_month,
                                'filterForm':SeasonForm(initial={'from_year':from_year,'from_month':from_month,
                                                                 'to_year':to_year,'to_month':to_month}),
                                'total_income':total_income,'total_expense':total_expense, 'total_profit':total_profit,
                                'avg_relative_expense_income':avg_relative_expense_income,'total_sale_count':total_sale_count,
                                'avg_relative_sales_expense':avg_relative_sales_expense},
                              context_instance=RequestContext(request))

@permission_required('Management.list_demand')
def demand_old_list(request):
    current = Demand.current_month()
    year = int(request.GET.get('year', current.year))
    month = int(request.GET.get('month', current.month))
    ds = Demand.objects.filter(year = year, month = month)
    total_sales_count,total_sales_amount, total_sales_commission, total_amount, expected_sales_count = 0,0,0,0,0
    for d in ds:
        total_sales_count += d.get_sales().count()
        total_sales_amount += d.get_final_sales_amount()
        total_sales_commission += d.get_sales_commission()
        total_amount += d.get_total_amount()
        expected_sales_count += d.sale_count
    unhandled_projects = []
    for p in Project.objects.active():
        try:
            d = ds.get(project=p)
        except Demand.DoesNotExist:
            unhandled_projects.append(p)
            continue
        if d.statuses.count()==0 or d.statuses.latest().type.id != DemandSent:
            unhandled_projects.append(p)
        
    return render_to_response('Management/demand_old_list.html', 
                              { 'demands':ds.all(), 'month':date(int(year), int(month), 1),
                                'filterForm':MonthFilterForm(initial={'year':year,'month':month}),
                                'total_sales_count':total_sales_count,
                                'total_sales_amount':total_sales_amount,
                                'total_sales_commission':total_sales_commission,
                                'total_amount':total_amount,
                                'expected_sales_count':expected_sales_count,
                                'unhandled_projects':unhandled_projects},
                              context_instance=RequestContext(request))

def nhemployee_salary_send(request, nhbranch_id, year, month):
    nhm = NHMonth.objects.get(nhbranch__id = nhbranch_id, year = year, month = month)
    filename = generate_unique_pdf_filename()

    NHEmployeeSalariesWriter(NHMonth.objects.get(nhbranch__id = int(nhbranch_id), year = int(year), month=int(month)),
                                                 bookkeeping=True).build(filename)

    mail('adush07@gmail.com', u'שכר עובדים %s לחודש %s/%s' % (nhm.nhbranch, nhm.month, nhm.year), '', filename)

    filename = generate_unique_pdf_filename()
    
    NHEmployeeSalariesWriter(NHMonth.objects.get(nhbranch__id = int(nhbranch_id), year = int(year), month=int(month)),
                                                 bookkeeping=False).build(filename)

    mail('adush07@gmail.com', u'שכר עובדים %s לחודש %s/%s' % (nhm.nhbranch, nhm.month, nhm.year), '', filename)
    '''
    for nhes in NHEmployeeSalary.objects.filter(nhemployee__nhbranch__id = nhbranch_id, year=year, month=month):
        if nhes.approved_date != None:
            nhes.send_to_bookkeeping()
            nhes.send_to_checks()
    '''
    return HttpResponseRedirect('/nhemployeesalaries/%s/%s' % (year,month))
    
def nhemployee_salary_pdf(request, nhbranch_id, year, month):
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    NHEmployeeSalariesWriter(NHMonth.objects.get(nhbranch__id = int(nhbranch_id), year = int(year), month=int(month)),
                                                 bookkeeping=True).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response 

@permission_required('Management.change_salaryexpenses')
def employee_salary_expenses(request, salary_id):
    es = EmployeeSalaryBase.objects.get(pk=salary_id)
    employee = es.get_employee()
    terms = employee.employment_terms
    expenses = es.expenses or SalaryExpenses(employee = employee, year = es.year, month = es.month)
    if request.method=='POST':
        form = SalaryExpensesForm(request.POST, instance= expenses)
        if form.is_valid():
            form.save()
    else:
        vacation = terms.salary_base and (terms.salary_base / 24) or (2500/12)
        form = SalaryExpensesForm(instance= expenses, initial={'vacation':vacation})
    return render_to_response('Management/salaryexpenses_edit.html', 
                              {'form':form, 'neto': es.neto or 0},
                               context_instance=RequestContext(request))

@permission_required('Management.change_employeesalary')
def employee_salary_approve(request, id):
    es = EmployeeSalaryBase.objects.get(pk=id)
    es.approve()
    if hasattr(es,'employeesalary'):
        return HttpResponseRedirect('/employeesalaries/?year=%s&month=%s' % (es.year, es.month))
    elif hasattr(es,'nhemployeesalary'):
        return HttpResponseRedirect('/nhemployeesalaries/?year=%s&month=%s' % (es.year, es.month))

@permission_required('Management.change_employeesalary')
def salary_expenses_approve(request, id):
    se = SalaryExpenses.objects.get(pk=id)
    se.approve()
    se.save()
    return HttpResponseRedirect('/salaryexpenses/?year=%s&month=%s' % (se.year, se.month))
    
@permission_required('Management.list_employeesalary')
def employee_salary_list(request):
    current = Demand.current_month()
    year = int(request.GET.get('year', current.year))
    month = int(request.GET.get('month', current.month))
    salaries = []
    today = date.today()
    if date(year, month, 1) <= today:
        for e in Employee.objects.all():
            terms = e.employment_terms
            if not terms:
                continue
            if year < e.work_start.year or (year == e.work_start.year and month < e.work_start.month):
                continue
            if e.work_end and (year > e.work_end.year or (year == e.work_end.year and month > e.work_end.month)):
                continue
            es, new = EmployeeSalary.objects.get_or_create(employee = e, month = month, year = year)
            if new:
                if year == e.work_start.year and month == e.work_start.month:
                    es.base = float(30 - e.work_start.day) / 30 * terms.salary_base 
                else:
                    es.base = terms.salary_base
                es.save()
            salaries.append(es)
    return render_to_response('Management/employee_salaries.html', 
                              {'salaries':salaries, 'month': date(int(year), int(month), 1),
                               'filterForm':MonthFilterForm(initial={'year':year,'month':month})},
                               context_instance=RequestContext(request))

@permission_required('Management.list_salaryexpenses')
def salary_expenses_list(request):
    current = Demand.current_month()
    year = int(request.GET.get('year', current.year))
    month = int(request.GET.get('month', current.month))
    salaries = list(EmployeeSalary.objects.filter(year = year, month= month))
    return render_to_response('Management/salaries_expenses.html', 
                              {'salaries':salaries, 'month': date(int(year), int(month), 1),
                               'filterForm':MonthFilterForm(initial={'year':year,'month':month})},
                               context_instance=RequestContext(request))

@permission_required('Management.list_salaryexpenses')
def nh_salary_expenses_list(request):
    current = Demand.current_month()
    year = int(request.GET.get('year', current.year))
    month = int(request.GET.get('month', current.month))
    salaries = list(NHEmployeeSalary.objects.filter(year = year, month= month))
    return render_to_response('Management/nh_salaries_expenses.html', 
                              {'salaries':salaries, 'month': date(int(year), int(month), 1),
                               'filterForm':MonthFilterForm(initial={'year':year,'month':month})},
                               context_instance=RequestContext(request))

@permission_required('Management.list_nhemployeesalary')
def nhemployee_salary_list(request):
    current = Demand.current_month()
    year = int(request.GET.get('year', current.year))
    month = int(request.GET.get('month', current.month))
    salaries = []
    for e in NHEmployee.objects.active():
        es, new = NHEmployeeSalary.objects.get_or_create(nhemployee = e, month = month, year = year)
        if new or not es.commissions or not es.base or not es.admin_commission: 
            es.calculate()
            es.save()
        salaries.append(es)
    return render_to_response('Management/nhemployee_salaries.html', 
                              {'salaries':salaries, 'month': date(int(year), int(month), 1),
                               'filterForm':MonthFilterForm(initial={'year':year,'month':month})},
                               context_instance=RequestContext(request))

def employee_salary_pdf(request, year, month):
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    EmployeeSalariesWriter([es for es in EmployeeSalary.objects.filter(year = year, month= month)
                            if es.approved_date], u'שכר עבודה למנהלי פרויקטים לחודש %s\%s' % (year, month),
                            show_month=False, show_employee=True, bookkeeping =False).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response    

def employee_salary_calc(request, model, id):
    es = model.objects.get(pk=id)
    es.calculate()
    es.save()
    if model == EmployeeSalary:
        return HttpResponseRedirect('/employeesalaries/?year=%s&month=%s' % (es.year, es.month))
    elif model == NHEmployeeSalary:
        return HttpResponseRedirect('/nhemployeesalaries/?year=%s&month=%s' % (es.year, es.month))

@permission_required('Management.list_demand')
def demands_all(request):
    error = None
    if request.method == 'POST':
        houseForm = LocateHouseForm(request.POST)
        demandForm = LocateDemandForm(request.POST)
        if houseForm.is_valid():
            houses = House.objects.filter(building__project = houseForm.cleaned_data['project'], 
                                          building__num = houseForm.cleaned_data['building_num'],
                                          num = houseForm.cleaned_data['house_num'])
            if houses.count() > 0:
                return HttpResponseRedirect('/buildings/%s/house/%s/type1' % (houses[0].building.id, houses[0].id))
            else:
                error = u'לא נמצאה דירה מס %s בבניין מס %s בפרוייקט %s' % (houseForm.cleaned_data['house_num'],
                                                                           houseForm.cleaned_data['building_num'],
                                                                           houseForm.cleaned_data['project'])
        if demandForm.is_valid():
            demands = Demand.objects.filter(project = demandForm.cleaned_data['project'], 
                                            month = demandForm.cleaned_data['month'],
                                            year = demandForm.cleaned_data['year'])
            if demands.count()>0:
                return HttpResponseRedirect('/reports/project_month/%s/%s/%s' % (demands[0].project.id,
                                                                         demands[0].year, demands[0].month))
    
    total_mispaid, total_unpaid, total_nopayment, total_noinvoice = 0,0,0,0
    amount_mispaid, amount_unpaid, amount_nopayment, amount_noinvoice = 0,0,0,0
    projects = Project.objects.all()
    for p in projects:
        for d in p.demands_mispaid():
            amount_mispaid += d.get_total_amount()
            total_mispaid += 1
        for d in p.demands_unpaid():
            amount_unpaid += d.get_total_amount()
            total_unpaid += 1
        for d in p.demands_nopayment():
            amount_nopayment += d.get_total_amount()
            total_nopayment += 1
        for d in p.demands_noinvoice():
            amount_noinvoice += d.get_total_amount()
            total_noinvoice += 1
    
    return render_to_response('Management/demands_all.html', 
                              { 'projects':projects, 'total_mispaid':total_mispaid, 'total_unpaid':total_unpaid,
                               'total_nopayment':total_nopayment, 'total_noinvoice':total_noinvoice,
                               'amount_mispaid':amount_mispaid, 'amount_unpaid':amount_unpaid, 
                               'amount_nopayment':amount_nopayment, 'amount_noinvoice':amount_noinvoice,
                               'houseForm':LocateHouseForm(), 
                               'demandForm':LocateDemandForm(),
                               'error':error },
                              context_instance=RequestContext(request))

def employee_list_pdf(request):
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    EmployeeListWriter(employees = Employee.objects.active(),
                       nhemployees = NHEmployee.objects.active()).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@permission_required('Management.nhmonth_season')
def nh_season_income(request):
    month, nhmonth_set, y, m = date.today(), [], 0, 0
    nhbranch_id = int(request.GET.get('nhbranch', 0))
    from_year = y = int(request.GET.get('from_year', month.year))
    from_month = m = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    if not request.user.has_perm('Management.nhbranch_' + str(nhbranch_id)):
        return HttpResponse('No Permission. Contact Elad.') 
    form = NHBranchSeasonForm(initial={'nhbranch':nhbranch_id,'from_year':from_year, 'from_month':from_month,
                                       'to_year':to_year, 'to_month':to_month})
    while date(y,m,1) <= date(to_year, to_month, 1):
        q = NHMonth.objects.filter(nhbranch__id = nhbranch_id, year = y, month = m)
        if q.count() > 0:
            nhmonth_set.append(q[0])
        y = m == 12 and y + 1 or y
        m = m == 12 and 1 or m + 1
    nhbranch = NHBranch.objects.get(pk=nhbranch_id)
    season_income, season_net_income, season_income_notax, season_net_income_notax = 0, 0, 0, 0
    total_avg_signed_commission, total_avg_actual_commission = 0,0
    from_date = date(from_year, from_month, 1)
    to_date = date(to_month == 12 and to_year + 1 or to_year, to_month == 12 and 1 or to_month + 1, 1)
    employees = nhbranch.nhemployees.filter(work_start__lt = to_date).exclude(work_end__isnull=False, work_end__lt = from_date)
    for e in employees:
        e.season_total, e.season_total_notax, e.season_branch_income_notax = 0, 0, 0
        e.season_branch_income_buyers_notax, e.season_branch_income_sellers_notax = 0, 0
    for nhm in nhmonth_set:
        nhm.employees = nhbranch.nhemployees.filter(work_start__lt = to_date).exclude(work_end__isnull=False, work_end__lt = from_date)
        tax = Tax.objects.filter(date__lte=date(nhm.year, nhm.month,1)).latest().value / 100 + 1
        for e in nhm.employees:
            e.month_total = 0
        for nhs in nhm.nhsales.all():
            for nhss in nhs.nhsaleside_set.all():
                for e in employees:
                    nhss.include_tax = True
                    e.season_total += nhss.get_employee_pay(e)
                    nhss.include_tax = False
                    e.season_total_notax += nhss.get_employee_pay(e)
                    if nhss.signing_advisor == e:
                        income_notax = nhss.income / tax
                        e.season_branch_income_notax += income_notax
                        if nhss.sale_type.id in [SaleType.SaleSeller, SaleType.RentRenter]:
                            e.season_branch_income_sellers_notax += income_notax
                        elif nhss.sale_type.id in [SaleType.SaleBuyer, SaleType.RentRentee]:
                            e.season_branch_income_buyers_notax += income_notax
                for e in nhm.employees:
                    nhss.include_tax = True
                    e.month_total += nhss.get_employee_pay(e)
        nhm.include_tax = False
        season_income_notax += nhm.total_income
        season_net_income_notax += nhm.total_net_income
        nhm.include_tax = True
        season_income += nhm.total_income
        season_net_income += nhm.total_net_income
        total_avg_signed_commission += nhm.avg_signed_commission
        total_avg_actual_commission += nhm.avg_actual_commission
    if len(nhmonth_set) > 0:
        total_avg_signed_commission /= len(nhmonth_set)
        total_avg_actual_commission /= len(nhmonth_set)
    else:
        total_avg_signed_commission = 0
        total_avg_actual_commission = 0        
    if season_net_income_notax:
        for e in employees:
            e.season_branch_income_ratio_notax = e.season_branch_income_notax / season_net_income_notax * 100
            e.season_branch_income_buyers_ratio_notax = e.season_branch_income_buyers_notax / season_net_income_notax * 100
            e.season_branch_income_sellers_ratio_notax = e.season_branch_income_sellers_notax / season_net_income_notax * 100
    return render_to_response('Management/nh_season_income.html', 
                              { 'nhmonths':nhmonth_set, 'filterForm':form, 'employees':employees,
                               'season_income':season_income,'season_net_income':season_net_income,
                               'season_income_notax':season_income_notax,'season_net_income_notax':season_net_income_notax,
                               'nhbranch':nhbranch, 'total_avg_actual_commission':total_avg_actual_commission,
                               'total_avg_signed_commission':total_avg_signed_commission },
                              context_instance=RequestContext(request))
    
def nhmonth_sales(request, nhbranch_id):
    if not request.user.has_perm('Management.nhbranch_' + nhbranch_id):
        return HttpResponse('No Permission. Contact Elad.') 
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    d = date(year, month, 1)
    if year and month:
        q = NHMonth.objects.filter(nhbranch__id = nhbranch_id, year=year, month=month)
    nhb = NHBranch.objects.get(pk=nhbranch_id)
    nhm = q.count() > 0 and q[0] or NHMonth(nhbranch = nhb, year = year, month = month)
    employees = nhb.nhemployees.filter(work_start__lt = d).exclude(work_end__isnull=False, work_end__lt = d)
    for e in employees:
        e.month_total = 0
    for sale in nhm.nhsales.all():
        for nhss in sale.nhsaleside_set.all():
            for e in employees:
                e.month_total += nhss.get_employee_pay(e)
    form = MonthFilterForm(initial={'year':nhm.year,'month':nhm.month})
    return render_to_response('Management/nhmonth_sales.html', 
                              { 'nhmonth':nhm, 'filterForm':form, 'employees':employees },
                              context_instance=RequestContext(request))

@permission_required('Management.change_nhmonth')
def nhmonth_close(request, id):
    nhm = NHMonth.objects.get(pk=id)
    if not request.user.has_perm('Management.nhbranch_' + str(nhm.nhbranch.id)):
        return HttpResponse('No Permission. Contact Elad.') 
    nhm.close()
    nhm.save()
    form = MonthFilterForm(initial={'year':nhm.year,'month':nhm.month})
    return render_to_response('Management/nhmonth_sales.html', 
                              { 'nhmonth':nhm, 'filterForm':form },
                              context_instance=RequestContext(request))

@permission_required('Management.add_demand')
def demand_list(request):
    current = Demand.current_month()
    year = int(request.GET.get('year', current.year))
    month = int(request.GET.get('month', current.month))
    ds = Demand.objects.filter(year = year, month = month)
    form = MonthFilterForm(initial={'year':year,'month':month})
    unhandled_projects = list(Project.objects.active())
    '''loop through all active projects and create demands for them if havent
    alredy created. if project has status other than Feed, it is handled'''        
    for p in Project.objects.active():
        if ds.filter(project = p).count() == 0:
            demand = Demand(project = p, month = month, year = year)
            demand.save()
	    if p.commissions.add_amount:
                demand.diffs.create(type=u'קבועה', amount = p.commissions.add_amount, reason = p.commissions.add_type)
        elif ds.get(project=p).statuses.count() > 0 and ds.get(project=p).statuses.latest().type.id != DemandFeed:
            unhandled_projects.remove(p)
    sales_count, expected_sales_count, sales_amount = 0,0,0
    for d in ds:
        sales_count += d.get_sales().count()
        sales_amount += d.get_final_sales_amount()
        expected_sales_count += d.sale_count
    return render_to_response('Management/demand_list.html', 
                              { 'demands':ds, 'unhandled_projects':unhandled_projects, 
                               'month':date(int(year), int(month), 1), 'filterForm':form, 'sales_count':sales_count ,
                               'sales_amount':sales_amount, 'expected_sales_count':expected_sales_count },
                              context_instance=RequestContext(request))

def employee_sales(request, id, year, month):
    es = EmployeeSalary.objects.get(employee__id = id, year = year, month = month)
    return render_to_response('Management/employee_sales.html', 
                              { 'es':es },
                              context_instance=RequestContext(request))

@permission_required('Management.add_employeesalary')
def employee_refund(request, year, month):
    if request.method == 'POST':
        form = EmployeeSalaryRefundForm(request.POST)
        if form.is_valid():
            form.instance = EmployeeSalary.objects.get_or_create(employee = form.cleaned_data['employee'], 
                                                                 year = year, 
                                                                 month = month)[0]
            form.save()
    else:
        form = EmployeeSalaryRefundForm()

    return render_to_response('Management/employee_salary_edit.html', 
                              { 'form':form, 'month':month, 'year':year },
                              context_instance=RequestContext(request))

@permission_required('Management.add_employeesalary')
def employee_remarks(request, year, month):
    if request.method == 'POST':
        form = EmployeeSalaryRemarksForm(request.POST)
        if form.is_valid():            
            form.instance = EmployeeSalary.objects.get_or_create(employee = form.cleaned_data['employee'], 
                                                                 year = year, 
                                                                 month = month)[0]
            form.save()
    else:
        form = EmployeeSalaryRemarksForm()

    return render_to_response('Management/employee_salary_edit.html', 
                              { 'form':form, 'month':month, 'year':year },
                              context_instance=RequestContext(request))

def nhemployee_sales(request, id, year, month):
    es = NHEmployeeSalary.objects.get(nhemployee__id = id, year = year, month = month)
    return render_to_response('Management/nhemployee_sales.html', 
                              { 'es':es },
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_nhemployeesalary')
def nhemployee_refund(request, year, month):
    if request.method == 'POST':
        form = NHEmployeeSalaryRefundForm(request.POST)
        if form.is_valid():
            form.instance = NHEmployeeSalary.objects.get_or_create(nhemployee = form.cleaned_data['nhemployee'], 
                                                                   year = year, 
                                                                   month = month)[0]
            form.save()
    else:
        form = NHEmployeeSalaryRefundForm()

    return render_to_response('Management/nhemployee_salary_edit.html', 
                              { 'form':form, 'month':month, 'year':year },
                              context_instance=RequestContext(request))

@permission_required('Management.add_nhemployeesalary')
def nhemployee_remarks(request, year, month):
    if request.method == 'POST':
        form = EmployeeSalaryRemarksForm(request.POST)
        if form.is_valid():            
            form.instance = NHEmployeeSalary.objects.get_or_create(nhemployee = form.cleaned_data['nhemployee'], 
                                                                   year = year, 
                                                                   month = month)[0]
            form.save()
    else:
        form = NHEmployeeSalaryRemarksForm()

    return render_to_response('Management/nhemployee_salary_edit.html', 
                              { 'form':form, 'month':month, 'year':year },
                              context_instance=RequestContext(request))
        
@permission_required('Management.change_demand')
def demand_close(request, id):
    d = Demand.objects.get(pk=id)
    return render_to_response('Management/demand_close.html', 
                              { 'demand':d },
                              context_instance=RequestContext(request))

@permission_required('Management.change_demand')
def demand_zero(request, id):
    d = Demand.objects.get(pk=id)
    if d.statuses.count() == 0:
        d.close()
    return HttpResponseRedirect('/demands')

def demand_send_mail(demand, addr):
    filename = generate_unique_pdf_filename()
    MonthDemandWriter(demand, to_mail=True).build(filename)
    mail(addr,
         u'עמלה לפרויקט %s לחודש %s/%s' % (demand.project, demand.month, demand.year),
         '', filename)
    demand.send()

@permission_required('Management.change_demand')
def demands_send(request):
    current = Demand.current_month()
    y = int(request.GET.get('year', current.year))
    m = int(request.GET.get('month', current.month))
    form = MonthFilterForm(initial={'year':y,'month':m})
    month = datetime(y,m,1)
    ds = Demand.objects.filter(year = y, month = m)
    forms=[]
    if request.method == 'POST':
        error = False
        for d in ds:
            f = DemandSendForm(request.POST, instance=d, prefix = str(d.id))
            if f.is_valid():
                if f.cleaned_data['is_finished']:
                    d.finish()
                if f.cleaned_data['by_mail']:
                    demand_send_mail(d, f.cleaned_data['mail'])
                if f.cleaned_data['by_fax']:
                    pass
            else:
                error=True
            forms.append(f)
        if not error:
            return HttpResponseRedirect('/demandsold')
    else:
        for d in ds:
            if d.project.demand_contact:
                initial = {'mail':d.project.demand_contact.mail,
                           'fax':d.project.demand_contact.fax}
            else:
                initial = {}
            f = DemandSendForm(instance=d, prefix=str(d.id), initial = initial)
            forms.append(f)
            
    return render_to_response('Management/demands_send.html', 
                              { 'forms':forms,'filterForm':form, 'month':month },
                              context_instance=RequestContext(request))

@permission_required('Management.change_demand')
def demand_closeall(request):
    for d in Demand.objects.current():
        if d.statuses.latest().type.id == DemandFeed:
            d.close()
    return HttpResponseRedirect('/demands')
        
@permission_required('Management.delete_sale')
def demand_sale_del(request, id):
    sale = Sale.objects.get(pk=id)
    if sale.demand.statuses.latest().type.id != DemandSent:
        sale.delete()
        return HttpResponseRedirect('../../../')
    else:
        sc = SaleCancel(sale = sale, date = date.today(), fee = 0)
        sc.save()
        return HttpResponseRedirect('/salecancel/%s' % sc.id)
        
@permission_required('Management.delete_sale')
def demand_sale_reject(request, id):
    sale = Sale.objects.get(pk=id)
    y,m = sale.demand.year, sale.demand.month
    try:
        sr = sale.salereject
    except SaleReject.DoesNotExist:
        sr = SaleReject(sale = sale, employee_pay = date(y,m,1))
    sr.date = date.today()
    sr.to_month = date(m==12 and y+1 or y, m==12 and 1 or m+1,1)
    sr.save()
    return HttpResponseRedirect('/salereject/%s' % sr.id)

@permission_required('Management.add_invoice')
def invoice_add(request, initial=None):
    if request.method == 'POST':
        form = DemandInvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.has_key('addanother'):
                form = DemandInvoiceForm(initial=initial)
            if request.POST.has_key('addpayment'):
                return HttpResponseRedirect('/payments/add')
    else:
        form = DemandInvoiceForm(initial=initial)
    return render_to_response('Management/invoice_edit.html', {'form':form}, context_instance=RequestContext(request))


@permission_required('Management.add_invoice')
def demand_invoice_add(request, id):
    demand = Demand.objects.get(pk=id)
    return invoice_add(request, {'project':demand.project.id, 'month':demand.month, 'year':demand.year})

@permission_required('Management.demand_invoices')
def demand_invoice_list(request):
    month = Demand.current_month()
    project_id = int(request.GET.get('project') or 0)
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    from_date = date(from_year, from_month, 1)
    to_date = date(to_month == 12 and to_year + 1 or to_year, to_month == 12 and 1 or to_month + 1, 1)
    q = project_id and Invoice.objects.filter(demands__project__id = project_id).reverse() or Invoice.objects.reverse()
    q = q.filter(date__range = (from_date, to_date)).annotate(Count('demands'))
    form = ProjectSeasonForm(initial={'from_year':from_year,'from_month':from_month,'to_year':to_year,'to_month':to_month,
                                      'project':project_id})
    paginator = Paginator([i for i in q if i.demands__count > 0], 25) 

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        invoices = paginator.page(page)
    except (EmptyPage, InvalidPage):
        invoices = paginator.page(paginator.num_pages)

    return render_to_response('Management/demand_invoice_list.html', {'page': invoices,'filterForm':form},
                              context_instance = RequestContext(request))    
 
 
@permission_required('Management.demand_payments')
def demand_payment_list(request):
    month = Demand.current_month()
    project_id = int(request.GET.get('project') or 0)
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    from_date = date(from_year, from_month, 1)
    to_date = date(to_month == 12 and to_year + 1 or to_year, to_month == 12 and 1 or to_month + 1, 1)
    q = project_id and Payment.objects.filter(demands__project__id = project_id).reverse() or Payment.objects.reverse()
    q = q.filter(payment_date__range = (from_date, to_date)).annotate(Count('demands'))
    form = ProjectSeasonForm(initial={'from_year':from_year,'from_month':from_month,'to_year':to_year,'to_month':to_month,
                                      'project':project_id})

    paginator = Paginator([i for i in q if i.demands__count > 0], 25) 

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        payments = paginator.page(page)
    except (EmptyPage, InvalidPage):
        payments = paginator.page(paginator.num_pages)

    return render_to_response('Management/demand_payment_list.html', {'page': payments,'filterForm':form},
                              context_instance = RequestContext(request))    
   
@permission_required('Management.add_invoice')
def project_invoice_add(request, id):
    return invoice_add(request, {'project':id})

@permission_required('Management.delete_invoice')
def invoice_del(request, id):
    i = Invoice.objects.get(pk=id)
    demand_id = i.demands.all()[0].id
    i.delete()
    return HttpResponseRedirect('/demands/%s' % demand_id)

@permission_required('Management.add_invoiceoffset')
def invoice_offset(request, id=None):
    if request.method == 'POST':
        form = InvoiceOffsetForm(request.POST)
        if form.is_valid():
            invoice_num = form.cleaned_data['invoice_num']
            invoice = Invoice.objects.get(num = invoice_num) 
            invoice.offset = form.save()
            invoice.save()
    else:
        if id:
            i = Invoice.objects.get(pk=id)
            invoice_num = i.num
            offset = i.offset or InvoiceOffset()
        else:
            offset = InvoiceOffset()
            invoice_num = 0
        form = InvoiceOffsetForm(instance = offset, initial={'invoice_num':invoice_num})
    
    return render_to_response('Management/invoiceoffset_edit.html', 
                              {'form': form, 'title':u'זיכוי חשבונית'}, 
                              context_instance = RequestContext(request))    

@permission_required('Management.delete_invoiceoffset')
def invoice_offset_del(request, id):
    io = InvoiceOffset.objects.get(pk=id)
    demand_id = io.invoice.demands.all()[0].id
    #unlink invoice from the offset
    invoice = io.invoice
    invoice.offset = None
    invoice.save()
    io.invoice = None
    io.delete()
    return HttpResponseRedirect('/demands/%s' % demand_id)

@permission_required('Management.add_payment')
def split_payment_add(request):
    DemandFormset = formset_factory(SplitPaymentDemandForm, extra=5)
    error = ''
    if request.method == 'POST':
        spf = SplitPaymentForm(request.POST)
        spdForms = DemandFormset(request.POST)
        if spf.is_valid() and spdForms.is_valid():
            for form in spdForms.forms:
                if not form.is_valid() or not form.cleaned_data.has_key('amount'):
                    continue
                p = Payment()
                for attr, value in spf.cleaned_data.items():
                    setattr(p, attr, value)
                p.amount = form.cleaned_data['amount']
                p.save()
                project, year, month = form.cleaned_data['project'], form.cleaned_data['year'], form.cleaned_data['month']
                q = Demand.objects.filter(project = project, year = year, month = month)
                if q.count() == 1:
                    q[0].payments.add(p)
                else:
                    error += '\r\n' + u'לא קיימת דרישה לפרוייקט %s לחודש %s\%s' % (project, year, month)
            if error == '':
                return HttpResponseRedirect('/demandpayments')
    else:
        spf = SplitPaymentForm()
        spdForms = DemandFormset()
        
    return render_to_response('Management/split_payment_add.html', 
                              { 'spf':spf, 'spdForms':spdForms, 'error':error }, context_instance=RequestContext(request))

@permission_required('Management.add_payment')
def payment_add(request, initial=None):
    if request.method == 'POST':
        form = DemandPaymentForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.has_key('addanother'):
                form = DemandPaymentForm(initial=initial)
            if request.POST.has_key('addinvoice'):
                return HttpResponseRedirect('/invoices/add')
    else:
        form = DemandPaymentForm(initial=initial)
    return render_to_response('Management/payment_edit.html', 
                              { 'form':form }, context_instance=RequestContext(request))
    
def payment_details(request, project, year, month):
    try:
        d = Demand.objects.get(project = project, year = year, month = month)
        return render_to_response('Management/demand_payment_details.html', 
                                  { 'payments':d.payments.all()}, context_instance=RequestContext(request))
    except Demand.DoesNotExist:
        return HttpResponse('')
    
def invoice_details(request, project, year, month):
    try:
        d = Demand.objects.get(project = project, year = year, month = month)
        return render_to_response('Management/demand_invoice_details.html', 
                                  { 'invoices':d.invoices.all()}, context_instance=RequestContext(request))
    except Demand.DoesNotExist:
        return HttpResponse('')
    
def demand_details(request, project, year, month):
    try:
        d = Demand.objects.get(project = project, year = year, month = month)
        return render_to_response('Management/demand_details.html', 
                                  { 'demand':d}, context_instance=RequestContext(request))
    except Demand.DoesNotExist:
        return HttpResponse('')

@permission_required('Management.add_demanddiff')
def demand_adddiff(request, object_id, type = None):
    demand = Demand.objects.get(pk=object_id)
    if request.method == 'POST':
        form = DemandDiffForm(request.POST)
        if form.is_valid():
            form.instance.demand = demand
            form.save()
    else:
        form = DemandDiffForm(initial={'type':type})
    return render_to_response('Management/object_edit.html', 
                              { 'form':form }, context_instance=RequestContext(request))

@permission_required('Management.add_demanddiff')
def demand_adddiff_adjust(request, object_id):
    return demand_adddiff(request, object_id, u'התאמה')

@permission_required('Management.delete_demanddiff')
def demanddiff_del(request, object_id):
    diff = DemandDiff.objects.get(pk=object_id)
    url = diff.demand.get_absolute_url()
    diff.delete()
    return HttpResponseRedirect(url)

@permission_required('Management.add_payment')
def demand_payment_add(request, id):
    demand = Demand.objects.get(pk=id)
    return payment_add(request, {'project':demand.project.id, 'month':demand.month, 'year':demand.year})
    
@permission_required('Management.add_payment')
def project_payment_add(request, id):    
    demand = Demand.objects.get(pk=id)
    return payment_add(request, {'project':id})

@permission_required('Management.add_payment')
def nhsaleside_payment_add(request, object_id):
    nhs = NHSaleSide.objects.get(pk=object_id)
    if not request.user.has_perm('Management.nhbranch_' + str(nhs.nhsale.nhmonth.nhbranch.id)):
        return HttpResponse('No Permission. Contact Elad.') 
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            p = form.save()
            nhs.payments.add(p)
            if request.POST.has_key('addanother'):
                form = PaymentForm()
    else:
        form = PaymentForm()
    return render_to_response('Management/object_edit.html', 
                              { 'form':form }, context_instance=RequestContext(request))
    
@permission_required('Management.add_invoice')
def nhsaleside_invoice_add(request, object_id):
    nhs = NHSaleSide.objects.get(pk=object_id)
    if not request.user.has_perm('Management.nhbranch_' + str(nhs.nhsale.nhmonth.nhbranch.id)):
        return HttpResponse('No Permission. Contact Elad.') 
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            i = form.save()
            nhs.invoices.add(i)
    else:
        form = InvoiceForm()
    return render_to_response('Management/object_edit.html', 
                              { 'form':form }, context_instance=RequestContext(request))

 
@permission_required('Management.delete_payment')
def payment_del(request, id):
    p = Payment.objects.get(pk=id)
    if p.demands.count() == 1:
        next = '/demands/%s' % p.demands.all()[0].id
    elif i.nhsaleside_set.count() == 1:
        next = '/nhsale/%s' % p.nhsaleside_set.all()[0].nhsale.id
    p.delete()
    return HttpResponseRedirect(next)

@login_required
def project_list(request):    
    projects = Project.objects.filter(end_date = None)
    return render_to_response('Management/project_list.html',
                              {'projects': projects}, 
                              context_instance=RequestContext(request))

@permission_required('Management.change_nhsale')
def nhsale_edit(request, object_id):
    nhs = NHSale.objects.get(pk=object_id)
    if not request.user.has_perm('Management.nhbranch_' + str(nhs.nhmonth.nhbranch.id)):
        return HttpResponse('No Permission. Contact Elad.') 
    return render_to_response('Management/nhsale_edit.html',
                              {'nhs': nhs}, 
                              context_instance=RequestContext(request))

@permission_required('Management.add_nhsale')
def nhsale_add(request, branch_id):
    if not request.user.has_perm('Management.nhbranch_' + str(branch_id)):
        return HttpResponse('No Permission. Contact Elad.') 
    PaymentFormset = modelformset_factory(Payment, PaymentForm, extra=5)
    if request.method=='POST':
        saleForm = NHSaleForm(request.POST, prefix='sale')
        monthForm = NHMonthForm(request.POST, prefix='month')
        if monthForm.is_valid():
            q = NHMonth.objects.filter(nhbranch = monthForm.cleaned_data['nhbranch'],
                                       year = monthForm.cleaned_data['year'],
                                       month = monthForm.cleaned_data['month'])
            saleForm.instance.nhmonth = q.count() == 1 and q[0] or monthForm.save()
        side1Form = NHSaleSideForm(request.POST, prefix='side1')
        side2Form = NHSaleSideForm(request.POST, prefix='side2')
        invoice1Form = InvoiceForm(request.POST, prefix='invoice1')
        payment1Forms = PaymentFormset(request.POST, prefix='payments1')
        invoice2Form = InvoiceForm(request.POST, prefix='invoice2')
        payment2Forms = PaymentFormset(request.POST, prefix='payments2')
        if saleForm.is_valid() and side1Form.is_valid() and side2Form.is_valid():
            nhsale = saleForm.save()
            side1Form.instance.nhsale = side2Form.instance.nhsale = nhsale
            side1, side2 = side1Form.save(), side2Form.save()
            error = False
            if invoice1Form.has_changed() and invoice1Form.is_valid():
                side1.invoices.add(invoice1Form.save())
            else:
                error = invoice1Form.has_changed()
            if payment1Forms.is_valid():
                for p in payment1Forms.save():
                    side1.payments.add(p)
            else:
                error = True
            if invoice2Form.has_changed() and invoice2Form.is_valid():
                side2.invoices.add(invoice2Form.save())
            else:
                error = invoice2Form.has_changed()
            if payment2Forms.is_valid():
                for p in payment2Forms.save():
                    side2.payments.add(p)
            else:
                error = True
            if not error:
                if request.POST.has_key('addanother'):
                    return HttpResponseRedirect('add')
                elif request.POST.has_key('tomonth'):
                    return HttpResponseRedirect('/nhbranch/%s/sales' % nhsale.nhbranch.id)
    else:
        branch = NHBranch.objects.get(pk=branch_id)
        saleForm = NHSaleForm(prefix='sale')
        monthForm = NHMonthForm(prefix='month')
        monthForm.fields['nhbranch'].initial = branch_id
        side1Form = NHSaleSideForm(prefix='side1')
        side1Form.fields['employee1'].queryset = branch.nhemployees.active()
        side1Form.fields['employee2'].queryset = branch.nhemployees.active()
        side1Form.fields['signing_advisor'].queryset = branch.nhemployees.active()
        side1Form.fields['director'].queryset = EmployeeBase.objects.active()
        side2Form = NHSaleSideForm(prefix='side2')
        side2Form.fields['employee1'].queryset = branch.nhemployees.active()
        side2Form.fields['employee2'].queryset = branch.nhemployees.active()
        side2Form.fields['signing_advisor'].queryset = branch.nhemployees.active()
        side2Form.fields['director'].queryset = EmployeeBase.objects.active()
        invoice1Form = InvoiceForm(prefix='invoice1')
        payment1Forms = PaymentFormset(prefix='payments1', queryset=Payment.objects.none())
        invoice2Form = InvoiceForm(prefix='invoice2')
        payment2Forms = PaymentFormset(prefix='payments2', queryset=Payment.objects.none())
        
    return render_to_response('Management/nhsale_add.html',
                              {'monthForm':monthForm, 'saleForm':saleForm, 
                               'side1form':side1Form, 'side2form':side2Form, 
                               'invoice1Form':invoice1Form, 'payment1Forms':payment1Forms, 
                               'invoice2Form':invoice2Form, 'payment2Forms':payment2Forms}, 
                              context_instance=RequestContext(request))

@permission_required('Management.change_pricelist')
def building_pricelist(request, object_id, type_id):
    b = Building.objects.get(pk = object_id)
    InlineFormSet = inlineformset_factory(Pricelist, ParkingCost, can_delete=False, extra=5, max_num=5)
    if request.method == 'POST':
        form = PricelistForm(request.POST, instance=b.pricelist)
        formset = InlineFormSet(request.POST, instance = b.pricelist)
        updateForm = PricelistUpdateForm(request.POST, prefix='upd')
        if form.is_valid():
            form.save()
            if formset.is_valid():
                formset.save()
        if updateForm.is_valid():
            amount, precentage, date = (updateForm.cleaned_data['amount'], updateForm.cleaned_data['precentage'],
                                        updateForm.cleaned_data['date'])
            pricelist_types = updateForm.cleaned_data['all_pricelists'] and Pricelist.objects.all() or [updateForm.cleaned_data['pricelisttype']]
            houses = [k.replace('house-','') for k in request.POST if k.startswith('house-')]
            for id in houses:
                h = House.objects.get(pk=id)
                for type in pricelist_types:
                    f = h.versions.filter(type=type)
                    if f.count() == 0: continue
                    price = f.latest().price
                    new = HouseVersion(house=h, type=type, date = date)
                    if amount:
                        new.price = price + amount
                    elif precentage:
                        new.price = price * (100 + precentage) / 100
                    new.save()
    else:
        form = PricelistForm(instance = b.pricelist)
        formset = InlineFormSet(instance = b.pricelist)
        updateForm = PricelistUpdateForm(prefix='upd')
    houses = b.houses.filter(is_deleted=False)
    signup_count = 0
    sale_count = 0
    for h in houses:
        try:
            if h.get_sale() or h.is_sold:
                sale_count = sale_count+1
            elif h.get_signup():
                signup_count = signup_count+1
            h.price = h.versions.filter(type__id = type_id).latest().price
        except HouseVersion.DoesNotExist:
            h.price = None
    avaliable_count = houses.count() - signup_count - sale_count
    return render_to_response('Management/building_pricelist.html',
                              {'form': form, 'formset': formset, 'updateForm':updateForm, 
                               'houses' : houses, 'signup_count':signup_count, 
                               'sale_count':sale_count, 'avaliable_count':avaliable_count,
                               'type':PricelistType.objects.get(pk=type_id), 
                               'types':PricelistType.objects.all()}, 
                              context_instance=RequestContext(request))

@permission_required('Management.change_pricelist')
def building_pricelist_pdf(request, object_id, type_id):
    type = request.GET.get('type', '')
    b = Building.objects.get(pk = object_id)
    pricelist_type = PricelistType.objects.get(pk = type_id)
    houses = b.houses.filter(is_deleted=False)
    if type == 'avaliable':
        houses = [h for h in houses.filter(is_sold=False) if h.get_sale() == None]
    for h in houses:
        try:
            h.price = h.versions.filter(type__id = type_id).latest().price
        except HouseVersion.DoesNotExist:
            h.price = None
    
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    title = u'מחירון לפרוייקט %s' % unicode(b.project)
    subtitle = u'בניין %s' % b.num
    subtitle += ' - %s' % unicode(pricelist_type)
    q = HouseVersion.objects.filter(house__building = b, type=pricelist_type)
    if q.count > 0:
        subtitle += u' לתאריך ' + q.latest().date.strftime('%d/%m/%Y')
    PricelistWriter(b.pricelist, houses, title, subtitle).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@permission_required('Management.building_clients')
def building_clients(request, object_id):
    b = Building.objects.get(pk = object_id)
    for h in b.houses.all():
        try:
            h.price = h.versions.filter(type__id = PricelistType.Company).latest().price
        except HouseVersion.DoesNotExist:
            h.price = None
    return render_to_response('Management/building_clients.html',
                              { 'object':b},
                              context_instance=RequestContext(request))

@permission_required('Management.building_clients_pdf')
def building_clients_pdf(request, object_id):
    b = Building.objects.get(pk = object_id)
    houses = [h for h in b.houses.filter(is_deleted=False) if h.get_sale() != None or h.is_sold == True]
    for h in houses:
        try:
            h.price = h.versions.filter(type__id = PricelistType.Company).latest().price
        except HouseVersion.DoesNotExist:
            h.price = None
    
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    title = u'מצבת רוכשים לפרוייקט %s' % unicode(b.project)
    subtitle = u'בניין %s' % b.num
    BuildingClientsWriter(houses, title, subtitle).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@permission_required('Management.add_project')
def project_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        ecForm = ExistContactForm(request.POST)
        contactForm = ContactForm(request.POST, prefix='contact')
        if form.is_valid():
            project = form.save()
            if contactForm.is_valid():
                project.demand_contact = contactForm.save()
            elif ecForm.is_valid():
                project.demand_contact = ecForm.cleaned_data['contact']
            project.save()
            return HttpResponseRedirect('../%s/' % project.id)
        else:
            ecForm = ExistContactForm()
    else:
        form = ProjectForm()
        ecForm = ExistContactForm()
        contactForm = ContactForm(prefix='contact')
    return render_to_response('Management/project_add.html',
                              { 'form':form,'ecForm':ecForm, 'contactForm':contactForm },
                              context_instance=RequestContext(request))

@permission_required('Management.change_salecommissiondetail')
def salecommissiondetail_edit(request, sale_id):
    sale = Sale.objects.get(pk=sale_id)
    InlineFormSet = inlineformset_factory(Sale, SaleCommissionDetail, can_delete=False)
    if request.method == 'POST':
        formset = InlineFormSet(request.POST, instance=sale)
        if formset.is_valid():
            formset.save()
    else:
        formset = InlineFormSet(instance=sale)
        
    return render_to_response('Management/objectset_edit.html', 
                              { 'formset':formset },
                              context_instance=RequestContext(request))
    
@permission_required('Management.change_project')
def project_edit(request, id):
    project = Project.objects.get(pk=id)
    details = project.details or ProjectDetails()
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        detailsForm = ProjectDetailsForm(request.POST, instance=details, prefix='det')
        if form.is_valid():
            form.save()
        if detailsForm.is_valid():
            project.details = detailsForm.save()
            project.save()
    else:
        form = ProjectForm(instance=project)
        detailsForm = ProjectDetailsForm(instance=details, prefix='det')
        
    return render_to_response('Management/project_edit.html', 
                              { 'form':form, 'detailsForm':detailsForm, 'project':project },
                              context_instance=RequestContext(request))
  
@login_required  
def project_commission_del(request, project_id, commission):
    project = Project.objects.get(pk = project_id)
    c = project.commissions    
    for field in c._meta.fields:
        if abbrevate(field.name) == commission:
            obj = getattr(c, field.name)
            break
    #unlink commission from project
    setattr(c, commission, None)
    project.commissions.save()
    #delete commission
    obj.delete()
    return HttpResponseRedirect('/projects/%s' % project.id)

@login_required
def project_commission_add(request, project_id, commission):
    return getattr(inspect.getmodule(project_commission_add), 'project_' + commission)(request, project_id)

@login_required
def employee_commission_del(request, employee_id, project_id, commission):
    employee = Employee.objects.get(pk = employee_id)
    c = employee.commissions.filter(project__id = project_id)[0]
    for field in c._meta.fields:
        if abbrevate(field.name) == commission:
            obj = getattr(c, field.name)
            break
    #unlink commission from employee
    setattr(c, commission, None)
    c.save()
    #delete commission
    obj.delete()
    return HttpResponseRedirect('/employees/%s' % employee.id)

def abbrevate(s):
    s2 = ''
    for part in s.split('_'):
        s2 += part[0]
    return s2

@login_required
def employee_commission_add(request, employee_id, project_id, commission):
    return getattr(inspect.getmodule(employee_commission_add), 'employee_' + commission)(request, employee_id, project_id)
        
@permission_required('Management.add_cvarprecentage')
def project_cvp(request, project_id):
    project = Project.objects.get(pk=project_id)
    c = project.commissions
    cvp = c.c_var_precentage or CVarPrecentage()
    InlineFormSet = inlineformset_factory(CVarPrecentage, CPrecentage, can_delete=False)
    if request.method == "POST":
        formset = InlineFormSet(request.POST, instance=cvp)
        form = CVarPrecentageForm(instance=cvp, data=request.POST)
        if formset.is_valid() and form.is_valid():
            c.c_var_precentage = form.save()
            c.save()
            formset.save()
    else:
        formset = InlineFormSet(instance=cvp)
        form = CVarPrecentageForm(instance=cvp)
    return render_to_response('Management/commission_inline.html', 
                              { 'formset':formset,'form':form, 'show_house_num':True },
                              context_instance=RequestContext(request))

@permission_required('Management.add_cvarprecentagefixed')
def project_cvpf(request, project_id):
    project = Project.objects.get(pk = project_id)
    c = project.commissions
    cvpf = c.c_var_precentage_fixed or CVarPrecentageFixed()
    if request.method == 'POST':
        form = CVarPrecentageFixedForm(request.POST, instance = cvpf)
        if form.is_valid():
            c.c_var_precentage_fixed = form.save()
            c.save()
    else:
        form = CVarPrecentageFixedForm(instance= cvpf)
            
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_czilber')
def project_cz(request, project_id):
    project = Project.objects.get(pk = project_id)
    c = project.commissions
    cz = c.c_zilber or CZilber()
    if request.method == 'POST':
        form = CZilberForm(request.POST, instance= cz)
        if form.is_valid():
            c.c_zilber = form.save()
            c.save()
    else:
        form = CZilberForm(instance= cz)
            
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))

@permission_required('Management.add_bdiscountsaveprecentage')
def project_bdsp(request, project_id):
    project = Project.objects.get(pk = project_id)
    c = project.commissions
    bdsp = c.b_discount_save_precentage or BDiscountSavePrecentage()
    if request.method == 'POST':
        form = BDiscountSavePrecentageForm(request.POST, instance = bdsp)
        if form.is_valid():
            c.b_discount_save_precentage = form.save()
            c.save()
    else:
        form = BDiscountSavePrecentageForm(instance=bdsp)
            
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_contact')
def project_contact(request, project_id, demand=False, payment=False):
    project = Project.objects.get(pk=project_id)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        existForm = ExistContactForm(request.POST)
        if existForm.is_valid():
            c = existForm.cleaned_data['contact']
            form = ContactForm()
        elif form.is_valid():
            existForm = ExistContactForm(initial={'contact':(demand and project.demand_contact and project.demand_contact.id) or (payment and project.payment_contact and project.payment_contact.id)})
            c = form.save()
        else:
            c=None
        if c:
            if demand:
                project.demand_contact = c
            elif payment:
                project.payment_contact = c
            else:
                project.contacts.add(c)
            project.save()
    else:
        form = ContactForm()
        existForm = ExistContactForm(initial={'contact':(demand and project.demand_contact and project.demand_contact.id) or (payment and project.payment_contact and project.payment_contact.id)})
        
    return render_to_response('Management/project_contact_edit.html', 
                              { 'form':form, 'existForm':existForm },
                              context_instance=RequestContext(request))

@permission_required('Management.change_employee')
def employee_project_add(request, employee_id):
    if request.method == 'POST':
        form = EmployeeAddProjectForm(request.POST)
        if form.is_valid():
            project, employee, start_date = form.cleaned_data['project'], form.cleaned_data['employee'], form.cleaned_data['start_date']
            employee.projects.add(project)
            employee.commissions.add(EPCommission(project = project, start_date = date.today()))
    else:
        form = EmployeeAddProjectForm(initial={'employee':employee_id})
    return render_to_response('Management/object_edit.html', 
                              { 'form':form, 'title':u'העסקה בפרוייקט חדש' },
                              context_instance=RequestContext(request))

@permission_required('Management.change_employee')
def employee_project_remove(request, employee_id, project_id):
    project = Project.objects.get(pk = project_id)
    employee = Employee.objects.get(pk = employee_id)
    if request.method == 'POST':
        form = EmployeeRemoveProjectForm(request.POST)
        if form.is_valid():
            project, employee, end_date = form.cleaned_data['project'], form.cleaned_data['employee'], form.cleaned_data['end_date']
            for epc in employee.commissions.filter(project=project):
                epc.end_date = end_date
                epc.save()
            employee.projects.remove(project)
    else:
        form = EmployeeRemoveProjectForm(initial={'employee':employee_id, 'project':project.id})
    return render_to_response('Management/object_edit.html', 
                              { 'form':form, 'title':u'סיום העסקה בפרוייקט' },
                              context_instance=RequestContext(request))

@permission_required('Management.change_contact')
def project_removecontact(request, id, project_id):
    p = Project.objects.get(pk=project_id)
    contact = Contact.objects.get(pk=id)
    try:
        contact.projects.remove(p)
    except:
        pass
    try:
        contact.projects_demand.remove(p)
    except:
        pass
    try:
        contact.projects_payment.remove(p)
    except:
        pass
    return HttpResponseRedirect('/projects/%s' % p.id)

@permission_required('Management.delete_contact')
def project_deletecontact(request, id, project_id):
    p = Project.objects.get(pk=project_id)
    contact = Contact.objects.get(pk=id)
    contact.projects.clear()
    contact.projects_demand.clear()
    contact.projects_payment.clear()
    contact.delete()
    return HttpResponseRedirect('/projects/%s' % p.id)
    
@permission_required('Management.delete_contact')
def contact_delete(request, id):
    contact = Contact.objects.get(pk=id)
    contact.projects.clear()
    contact.projects_demand.clear()
    contact.projects_payment.clear()
    contact.delete()
    return HttpResponseRedirect('/contacts')

@permission_required('Management.add_attachment')
def obj_add_attachment(request, obj_id, model):
    obj = model.objects.get(pk= obj_id)
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES, initial={'is_private':False})
        form.instance.user_added = request.user
        form.instance.file = request.FILES['file']
        if form.is_valid():
            a = form.save()
            obj.attachments.add(a)
            return HttpResponseRedirect('../attachments')
    else:
        form = AttachmentForm()
    
    return render_to_response('Management/attachment_edit.html',
                              {'form': form, 'obj':obj}, context_instance=RequestContext(request))

@login_required
def obj_attachments(request, obj_id, model):
    obj = model.objects.get(pk= obj_id)
    if request.user.is_staff:
        attachments = obj.attachments.all()
    else:
        attachments = obj.attachments.filter(is_private=False)        
    return render_to_response('Management/object_attachment_list.html',
                              {'attachments': attachments, 'obj':obj}, context_instance=RequestContext(request))

@permission_required('Management.add_reminder')
def obj_add_reminder(request, obj_id, model):
    obj = model.objects.get(pk= obj_id)
    if request.method == 'POST':
        form = ReminderForm(data= request.POST)
        if form.is_valid():
            r = form.save()
            obj.reminders.add(r)
            return HttpResponseRedirect('reminders')
    else:
        form = ReminderForm(initial={'status':ReminderStatusType.Added})
    
    return render_to_response('Management/object_edit.html',
                              {'form': form}, context_instance=RequestContext(request))

@login_required
def obj_reminders(request, obj_id, model):
    obj = model.objects.get(pk = obj_id)
    return render_to_response('Management/reminder_list.html',
                              {'reminders': obj.reminders}, context_instance=RequestContext(request))

@permission_required('Management.delete_reminder')
def reminder_del(request, id):
    r = Reminder.objects.get(pk= id)
    if r.statuses.latest().type.id == ReminderStatusType.Deleted:
        return HttpResponse('reminder is already deleted')
    else:
        r.delete()
        return HttpResponse('ok')
    
@permission_required('Management.change_reminder')
def reminder_do(request, id):
    r = Reminder.objects.get(pk= id)
    if r.statuses.latest().type.id == ReminderStatusType.Done:
        return HttpResponse('reminder is already done')
    else:
        r.do()
        return HttpResponse('ok')

@login_required
def project_buildings(request, project_id):
    p = Project.objects.get(pk = project_id)
    buildings = p.buildings.filter(is_deleted=False)
    total_signed_houses, total_houses, total_avalible_houses = (0,0,0)
    for b in buildings.all():
        total_houses = total_houses + b.house_count
        total_signed_houses = total_signed_houses + len(b.signed_houses())
        total_avalible_houses = total_avalible_houses + len(b.avalible_houses())
    return render_to_response('Management/building_list.html', 
                              { 'buildings' : buildings,'total_houses':total_houses,'project':p,
                               'total_signed_houses':total_signed_houses, 'total_avalible_houses':total_avalible_houses},
                              context_instance=RequestContext(request))

@permission_required('Management.add_building')
def building_add(request, project_id=None):
    if request.method == 'POST':
        form = BuildingForm(request.POST)
        if form.is_valid():
            building = form.save()
            return HttpResponseRedirect('../buildings')
    else:
        form = BuildingForm()
        if project_id:
            project = Project.objects.get(pk=project_id)
            form.initial = {'project':project.id}
            
    return render_to_response('Management/object_edit.html', 
                              {'form' : form})

@permission_required('Management.add_parking')
def building_addparking(request, building_id = None):
    if request.method == 'POST':
        form = ParkingForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ParkingForm()
        if building_id:
            b = Building.objects.get(pk=building_id)
            form.initial = {'building':b.id}
            form.fields['house'].queryset = b.houses.filter(is_deleted=False)
    return render_to_response('Management/object_edit.html', 
                              {'form' : form},
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_storage')
def building_addstorage(request, building_id = None):
    if request.method == 'POST':
        form = StorageForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = StorageForm()
        if building_id:
            b = Building.objects.get(pk=building_id)
            form.initial = {'building':b.id}
            form.fields['house'].queryset = b.houses.filter(is_deleted=False)
    return render_to_response('Management/object_edit.html', 
                              {'form' : form},
                              context_instance=RequestContext(request))
        
@permission_required('Management.delete_building')
def building_delete(request, building_id):
    building = Building.objects.get(pk = building_id)
    building.is_deleted = True
    building.save()
    return HttpResponse('ok')
    
@permission_required('Management.add_house')
def building_addhouse(request, type_id, building_id):
    b = Building.objects.get(pk=building_id)
    if request.method == 'POST':
        form = HouseForm(type_id, data = request.POST)
        form.instance.building = b
        if form.is_valid():
            form.save(type_id)
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect('type%s' % type_id)
            elif request.POST.has_key('finish'):
                return HttpResponseRedirect('../pricelist/type%s' % type_id)
    else:
        form = HouseForm(type_id)
        form.instance.building = b
        if b.is_cottage():
            form.initial['type'] = HouseType.Cottage

    ps = Parking.objects.filter(building = b)
    ss = Storage.objects.filter(building = b)
    for f in ['parking1','parking2','parking3']:
        form.fields[f].queryset = ps
    for f in ['storage1','storage2']:
        form.fields[f].queryset = ss
    return render_to_response('Management/house_edit.html', 
                              {'form' : form, 'type':PricelistType.objects.get(pk = type_id) })

@permission_required('Management.change_house')
def house_edit(request,id , type_id):
    h = House.objects.get(pk=id)
    b = h.building
    if request.method == 'POST':
        form = HouseForm(type_id, data = request.POST, instance = h)
        if form.is_valid():
            form.save(type_id)
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect('../../addhouse/type%s' % type_id)
            elif request.POST.has_key('finish'):
                return HttpResponseRedirect('../../pricelist/type%s' % type_id)
    else:
        form = HouseForm(type_id, instance = h)
        if b.is_cottage():
            form.initial['type'] = HouseType.Cottage

    ps = Parking.objects.filter(building = b)
    ss = Storage.objects.filter(building = b)
    for f in ['parking1','parking2','parking3']:
        form.fields[f].queryset = ps
    for f in ['storage1','storage2']:
        form.fields[f].queryset = ss
    return render_to_response('Management/house_edit.html', 
                              {'form' : form, 'type':PricelistType.objects.get(pk = type_id) })
        
@permission_required('Management.add_loan')
def employee_addloan(request, employee_id):
    employee = Employee.objects.get(pk = employee_id)
    if request.method=='POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            form.save() 
    else:
        form = LoanForm(initial={'employee':employee.id})
    
    return render_to_response('Management/object_edit.html',
                              {'form' : form}, context_instance=RequestContext(request))
    
@permission_required('Management.add_loanpay')
def employee_loanpay(request, employee_id):
    e = Employee.objects.get(pk=employee_id)
    if request.method == 'POST':
        form = LoanPayForm(request.POST)
        if form.is_valid():
            form.instance.employee = e
            form.save()
    else:
        form = LoanPayForm(initial={'employee':e.id})
    return render_to_response('Management/object_edit.html',
                              {'form' : form}, context_instance=RequestContext(request))
    
@permission_required('Management.change_nhcbase')
def nhemployee_nhcb(request, employee_id):
    employee = NHEmployee.objects.get(pk = employee_id)
    nhcb = employee.nhcbase or NHCBase()
    if request.method=='POST':
        form = NHCBaseForm(request.POST, instance = nhcb)
        if form.is_valid():
            employee.nhcbase = form.save()
            employee.save() 
    else:
        form = NHCBaseForm(instance = nhcb)
    
    return render_to_response('Management/object_edit.html',
                              {'form' : form}, context_instance=RequestContext(request))
    
@permission_required('Management.change_nhcbranchincome')
def nhemployee_nhcbi(request, employee_id):
    employee = NHEmployee.objects.get(pk = employee_id)
    nhcb = employee.nhcbranchincome or NHCBranchIncome()
    if request.method=='POST':
        form = NHCBranchIncomeForm(request.POST, instance = nhcb)
        if form.is_valid():
            employee.nhcbranchincome = form.save() 
            employee.save()
    else:
        form = NHCBranchIncomeForm(instance = nhcb)
    
    return render_to_response('Management/object_edit.html',
                              {'form' : form}, context_instance=RequestContext(request))

def nhemployee_commission_del(request, employee_id, attr):
    employee = NHEmployee.objects.get(pk = employee_id)
    obj = getattr(employee, attr)
    #unlink commission from employee
    setattr(c, attr, None)
    c.save()
    #delete commission
    obj.delete()
    return HttpResponseRedirect('/nhemployees/%s' % employee.id)

@permission_required('Management.add_loan')
def nhemployee_addloan(request, employee_id):
    employee = NHEmployee.objects.get(pk = employee_id)
    if request.method=='POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            form.save() 
    else:
        form = LoanForm(initial={'employee':employee.id})
    
    return render_to_response('Management/object_edit.html',
                              {'form' : form}, context_instance=RequestContext(request))
    
@permission_required('Management.add_loanpay')
def nhemployee_loanpay(request, employee_id):
    e = NHEmployee.objects.get(pk=employee_id)
    if request.method == 'POST':
        form = LoanPayForm(request.POST)
        if form.is_valid():
            form.instance.nhemployee = e
            form.save()
    else:
        form = LoanPayForm(initial={'employee':e.id})
    return render_to_response('Management/object_edit.html',
                              {'form' : form}, context_instance=RequestContext(request))

@permission_required('Management.add_employmentterms')
def employee_employmentterms(request, id, model):
    employee = model.objects.get(pk = id)
    terms = employee.employment_terms or EmploymentTerms()
    if request.method == "POST":
        form = EmploymentTermsForm(request.POST, instance=terms)
        if form.is_valid():
            employee.employment_terms = form.save()
            employee.save()
    else:
        form = EmploymentTermsForm(instance=terms)
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_cvar')
def employee_cv(request, employee_id, project_id):
    employee = Employee.objects.get(pk = employee_id)
    pc = employee.commissions.filter(project__id = project_id)[0]
    cv = pc.c_var or CVar()
    InlineFormSet = inlineformset_factory(CVar, CAmount, can_delete=False)
    if request.method == "POST":
        formset = InlineFormSet(request.POST, instance=cv)
        form = CVarForm(instance=cv, data=request.POST)
        if formset.is_valid() and form.is_valid():
            pc.c_var = form.save()
            pc.save()
            formset.save()
    else:
        formset = InlineFormSet(instance=cv)
        form = CVarForm(instance=cv)
    return render_to_response('Management/commission_inline.html', 
                              { 'formset':formset,'form':form, 'show_house_num':True },
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_cvarprecentage')
def employee_cvp(request, employee_id, project_id):
    employee = Employee.objects.get(pk = employee_id)
    pc = employee.commissions.filter(project__id = project_id)[0]
    cvp = pc.c_var_precentage or CVarPrecentage()
    InlineFormSet = inlineformset_factory(CVarPrecentage, CPrecentage, can_delete=False)
    if request.method == "POST":
        formset = InlineFormSet(request.POST, instance=cvp)
        form = CVarPrecentageForm(instance=cvp, data=request.POST)
        if formset.is_valid() and form.is_valid():
            pc.c_var_precentage = form.save()
            pc.save()
            formset.save()
    else:
        formset = InlineFormSet(instance=cvp)
        form = CVarPrecentageForm(instance=cvp)
    return render_to_response('Management/commission_inline.html', 
                              { 'formset':formset,'form':form, 'show_house_num':True },
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_cbyprice')
def employee_cbp(request, employee_id, project_id):
    employee = Employee.objects.get(pk = employee_id)
    pc = employee.commissions.filter(project__id = project_id)[0]
    cbp = pc.c_by_price or CByPrice()
    InlineFormSet = inlineformset_factory(CByPrice, CPriceAmount, can_delete=False)
    if request.method == "POST":
        formset = InlineFormSet(request.POST, instance=cbp)
        if formset.is_valid():
            cbp.save()
            pc.c_by_price = cbp
            pc.save()
            formset.save()
    else:
        formset = InlineFormSet(instance=cbp)
        
    return render_to_response('Management/commission_inline.html', 
                              { 'formset':formset, 'show_house_num':False },
                              context_instance=RequestContext(request))

@permission_required('Management.add_bsalerate')
def employee_bsr(request, employee_id, project_id):
    employee = Employee.objects.get(pk = employee_id)
    pc = employee.commissions.filter(project__id = project_id)[0]
    bsr = pc.b_sale_rate or BSaleRate()
    InlineFormSet = inlineformset_factory(BSaleRate, SaleRateBonus, can_delete=False)
    if request.method == "POST":
        formset = InlineFormSet(request.POST, instance=bsr)
        if formset.is_valid():
            bsr.save()
            pc.b_sale_rate = bsr
            pc.save()
            formset.save()
    else:
        formset = InlineFormSet(instance=bsr)
    return render_to_response('Management/commission_inline.html', 
                              { 'formset':formset, 'show_house_num':False},
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_bhousetype')
def employee_bht(request, employee_id, project_id):
    employee = Employee.objects.get(pk = employee_id)
    pc = employee.commissions.filter(project__id = project_id)[0]
    htb = pc.b_house_type or BHouseType()
    InlineFormSet = inlineformset_factory(BHouseType, HouseTypeBonus, can_delete=False)
    if request.method == "POST":
        formset = InlineFormSet(request.POST, instance=htb)
        if formset.is_valid():
            htb.save()
            pc.b_house_type = htb
            pc.save()
            formset.save()
    else:
        formset = InlineFormSet(instance=htb)
        
    return render_to_response('Management/commission_inline.html', 
                              { 'formset':formset, 'show_house_num':False},
                              context_instance=RequestContext(request))
    
@permission_required('Management.add_bdiscountsave')
def employee_bds(request, employee_id, project_id):
    employee = Employee.objects.get(pk = employee_id)
    pc = employee.commissions.filter(project__id = project_id)[0]
    bds = pc.b_discount_save or BDiscountSave()
    if request.method == 'POST':
        form = BDiscountSaveForm(request.POST, instance = bds)
        if form.is_valid():
            pc.b_discount_save = form.save()
            pc.save()
    else:
        form = BDiscountSaveForm(instance=bds)
            
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))

@permission_required('Management.add_bdiscountsaveprecentage')
def employee_bdsp(request, employee_id, project_id):
    employee = Employee.objects.get(pk = employee_id)
    c = employee.commissions.filter(project__id = project_id)[0]
    bdsp = c.b_discount_save_precentage or BDiscountSavePrecentage()
    if request.method == 'POST':
        form = BDiscountSavePrecentageForm(request.POST, instance = bdsp)
        if form.is_valid():
            c.b_discount_save_precentage = form.save()
            c.save()
    else:
        form = BDiscountSavePrecentageForm(instance=bdsp)
            
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
                              context_instance=RequestContext(request))
    
@login_required
def json_buildings(request, project_id):
    data = serializers.serialize('json', Project.objects.get(pk= project_id).non_deleted_buildings(), 
                                 fields=('id','name','num'))
    return HttpResponse(data)

@login_required
def json_employees(request, project_id):
    l = [EmployeeBase.objects.get(pk=e.id) for e in Project.objects.get(pk=project_id).employees.active()]
    data = serializers.serialize('json', l, 
                                 fields=('id','pid','first_name','last_name'))
    return HttpResponse(data)

@login_required
def json_houses(request, building_id):
    houses=[]
    for house in Building.objects.get(pk= building_id).houses.filter(is_deleted=False):
        if house.get_sale() == None:
            houses.append(house)
    data = serializers.serialize('json', houses, fields=('id','num'))
    return HttpResponse(data)

@login_required
def json_house(request, house_id):
    data = serializers.serialize('json', [House.objects.get(pk= house_id),])
    return HttpResponse(data)
    house = House.objects.get(pk= house_id)
    fields = {}
    for field in ['id', 'num', 'floor', 'rooms', 'allowed_discount', 'parking', 'warehouse', 'remarks']:
        fields[field] = 1 and getattr(house, field) or ''
    fields['price'] = house.prices.latest().price
    a = '[' + unicode({'pk':house.id, 'model':'Management.house', 'fields':fields}) + ']'
    return HttpResponse(a)
  
@login_required
def json_links(request):
    data = serializers.serialize('json', Link.objects.all())
    return HttpResponse(data)

@login_required
def task_list(request):
    sender = request.GET.get('sender', 'others')
    status = request.GET.get('status', 'undone')
    filterForm = TaskFilterForm(initial={'sender':sender, 'status':status})
    tasks = request.user.tasks.filter(is_deleted = False)
    if sender == 'me':
        tasks = tasks.filter(sender = request.user)
    if sender == 'others':
        tasks = tasks.filter(user = request.user)
    if status == 'done':
        tasks = tasks.filter(is_done = True)
    if status == 'undone':
        tasks = tasks.filter(is_done = False)
    
    return render_to_response('Management/task_list.html',
                              {'tasks': tasks, 'filterForm' : filterForm}, context_instance=RequestContext(request))

@permission_required('Management.add_task')
def task_add(request):
    if request.method=='POST':
        form = TaskForm(data = request.POST)
        if form.is_valid():
            t = form.instance
            t.sender = request.user
            form.save()
    else:
        form = TaskForm()
    
    return render_to_response('Management/object_edit.html',
                              {'form' : form}, context_instance=RequestContext(request))
    
@permission_required('Management.change_task')
def task_do(request, id):
    t = Task.objects.get(pk = id)
    if t.is_done:
        return HttpResponse('task is already done')
    else:
        t.do()
        return HttpResponseRedirect('/tasks')    

@permission_required('Management.delete_task')
def task_del(request, id):
    t = Task.objects.get(pk = id)
    if t.is_deleted:
        return HttpResponse('task is already deleted')
    else:
        t.delete()
        return HttpResponseRedirect('/tasks')

@permission_required('Management.delete_attachment')
def attachment_delete(request, id):
    a = Attachment.objects.get(pk= id)
    back = (a.project and '/projects/%s/attachments' % a.project.id) or (
        a.employee and '/employees/%s/attachments' % a.employee.id) or '/attachments'   
    a.delete()
    return HttpResponseRedirect(back)

@permission_required('Management.add_attachment')
def attachment_add(request):
    if request.method == "POST":
        form = AttachmentForm(request.POST, request.FILES)
        form.instance.user_added = request.user
        form.instance.file = request.FILES['file']
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/attachments')
    else:
        form = AttachmentForm()
    return render_to_response('Management/attachment_edit.html', 
                              {'form':form },
                              context_instance=RequestContext(request))

@permission_required('Management.change_sale')
def sale_edit(request, id):
    sale = Sale.objects.get(pk=id)
    if request.POST:
        form = SaleForm(request.POST, instance = sale)
        #handles the case when the building changes, and the house is not
        #in the queryset of the house field
        form.fields['house'].queryset = House.objects.all()
        if form.is_valid():
            project = form.cleaned_data['project']
            next = None
            #temp fix. should remove
            if sale.demand.statuses.count() == 0:
                sale.demand.feed()
            if sale.demand.statuses.latest().type.id == DemandSent:
                #check for mods:
                if sale.price != form.cleaned_data['price']:
                    spm = SalePriceMod(sale = sale, old_price = sale.price, date=date.today())
                    spm.save()
                    next = '/salepricemod/%s' % spm.id
                    sale.price = sale.project_price()
                if sale.house != form.cleaned_data['house']:
                    shm = SaleHouseMod(sale = sale, old_house = sale.house, date=date.today())
                    shm.save()
                    next = '/salehousemod/%s' % shm.id
            form.save()
            sale.demand.calc_sales_commission()
            year, month = sale.demand.year, sale.demand.month
            for employee in project.employees.all():
                if employee.work_end and employee.work_end < date(year, month, 1):
                    continue
                es = employee.salaries.get_or_create(year = year, month = month)
                es[0].calculate()
                es[0].save()
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect(next or '/demands/%s/sale/add' % sale.demand.id)
            elif request.POST.has_key('todemand'):
                return HttpResponseRedirect(next or '/demands/%s' % sale.demand.id)
    else:
        form = SaleForm(instance= sale)
    return render_to_response('Management/sale_edit.html', 
                              {'form':form, 'year':sale.actual_demand.year, 'month':sale.actual_demand.month},
                              context_instance=RequestContext(request))    

@permission_required('Management.add_sale')
def sale_add(request, demand_id=None):
    if demand_id:
        demand = Demand.objects.get(pk = demand_id)
        year, month = demand.year, demand.month
    else:
        year, month = Demand.current_month().year, Demand.current_month().month
    if request.POST:
        form = SaleForm(request.POST)
        if form.is_valid():
            if not demand_id:
                demand = Demand.objects.get(year = year, month = month, project = form.cleaned_data['project'])
            form.instance.demand = demand
            form.save()
            next = None
            if demand.statuses.count() == 0:
                demand.feed()
            if demand.statuses.latest().type.id == DemandSent:
                y,m = demand.year, demand.month
                sp = SalePre(sale = form.instance, date=date.today(),
                             employee_pay = date(m==12 and y+1 or y,m==12 and 1 or m, 1))
                sp.save()
                next = '/salepre/%s' % sp.id 
            demand.calc_sales_commission()
            for employee in demand.project.employees.all():
                if employee.work_end and employee.work_end < date(year, month, 1):
                    continue
                es = employee.salaries.get_or_create(year = year, month = month)
                es[0].calculate()
                es[0].save()
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect(next or (demand_id and '/demands/%s/sale/add' % demand_id or '/sale'))
            elif request.POST.has_key('todemand'):
                return HttpResponseRedirect(next or '/demands/%s' % demand.id)
    else:
        form = SaleForm()
        if demand_id:
            p = demand.project
            form.fields['project'].initial = p.id
            form.fields['employee'].queryset = p.employees.all()
            form.fields['building'].queryset = p.buildings.all()
    return render_to_response('Management/sale_edit.html', 
                              {'form':form, 'year':year, 'month':month},
                              context_instance=RequestContext(request))

def demand_sale_list(request):
    demand_id = int(request.GET.get('demand_id', 0))
    project_id = int(request.GET.get('project_id', 0))
    from_year = int(request.GET.get('from_year', 0))
    from_month = int(request.GET.get('from_month', 0))
    to_year = int(request.GET.get('to_year', 0))
    to_month = int(request.GET.get('to_month', 0))
    if demand_id:
        d = Demand.objects.get(pk=demand_id)
        sales = d.get_sales()
        sales_amount = d.get_sales_amount()
        title = u'ריכוז מכירות לפרוייקט %s לחודש %s/%s' % (unicode(d.project), d.month, d.year)
    elif project_id:
        current = date(from_year, from_month, 1)
        end = date(to_year, to_month, 1)
        sales = []
        sales_amount = 0
        project = Project.objects.get(pk=project_id)
        while current <= end:
            q = Demand.objects.filter(project__id = project_id, year = current.year, month = current.month)
            if q.count() > 0:
                sales.extend(list(q[0].get_sales()))
                sales_amount += q[0].get_sales_amount()
            current = date(current.month == 12 and current.year + 1 or current.year, 
                           current.month == 12 and 1 or current.month + 1, 1)
        title = u'ריכוז מכירות לפרוייקט %s מחודש %s/%s עד חודש %s/%s' % (unicode(project), from_month, from_year,
                                                                         to_month, to_year)
    else:
        raise ValueError
    return render_to_response('Management/sale_list.html', 
                              {'sales':sales, 'sales_amount':sales_amount,'title':title},
                              context_instance=RequestContext(request))  
       
def demand_sales(request, project_id, year, month):
    salesTotal = 0
    try:
        d = Demand.objects.get(project__id = project_id, year=year, month=month)
        sales = d.get_sales().all()
        for s in sales:
            salesTotal = salesTotal + s.price
    except Demand.DoesNotExist:
        sales=[]
    return render_to_response('Management/sale_table.html', 
                              {'sales':sales, 'salesTotal':salesTotal },
                              context_instance=RequestContext(request))  
@login_required
def project_demands(request, project_id, func, template_name):
    p = Project.objects.get(pk = project_id)
    demands = getattr(p, func)
    return render_to_response(template_name,
                               {'demands':demands(), 'project':p},
                               context_instance=RequestContext(request))

@permission_required('Management.report_project_month')
def report_project_month(request, project_id, year, month):
    demand = Demand.objects.get(project__id = project_id, year = year, month = month)
    if demand.get_sales().count() == 0:
        return render_to_response('Management/error.html', 
                                  {'error':u'לדרישה שנבחרה אין מכירות'},
                                  context_instance=RequestContext(request))
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    
    MonthDemandWriter(demand, to_mail=False).build(filename)
    
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@permission_required('Management.report_projects_month')
def report_projects_month(request, year, month):
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    demands = Demand.objects.filter(year = year, month=month).all()
    MultipleDemandWriter(demands, u'ריכוז דרישות לפרוייקטים לחודש %s\%s' % (year, month),
                         show_month=False, show_project=True).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@login_required
def report_project_season(request, project_id=None, from_year=Demand.current_month().year, from_month=Demand.current_month().month, 
                          to_year=Demand.current_month().year, to_month=Demand.current_month().month):
    ds = []
    current = date(int(from_year), int(from_month), 1)
    end = date(int(to_year), int(to_month), 1)
    while current <= end:
        q = Demand.objects.filter(project__id = project_id, year = current.year, month = current.month)
        if q.count() > 0:
            ds.append(q[0])
        current = date(current.month == 12 and current.year + 1 or current.year,
                       current.month == 12 and 1 or current.month + 1, 1)
    
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    MultipleDemandWriter(ds, u'ריכוז דרישות תקופתי לפרוייקט %s' % Project.objects.get(pk=project_id),
                         show_month=True, show_project=False).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@login_required
def report_employeesalary_season(request, employee_id=None, from_year=Demand.current_month().year, from_month=Demand.current_month().month, 
                          to_year=Demand.current_month().year, to_month=Demand.current_month().month):
    salaries = []
    current = date(int(from_year), int(from_month), 1)
    end = date(int(to_year), int(to_month), 1)
    while current <= end:
        q = EmployeeSalary.objects.filter(employee__id = employee_id, year = current.year, month = current.month)
        if q.count() > 0:
            salaries.append(q[0])
        current = date(current.month == 12 and current.year + 1 or current.year,
                       current.month == 12 and 1 or current.month + 1, 1)
    
    filename = generate_unique_pdf_filename()
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    EmployeeSalariesWriter(salaries, u'ריכוז שכר תקופתי לעובד - %s' % Employee.objects.get(pk=employee_id),
                           show_month=True, show_employee=False, bookkeeping =False).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@permission_required('Management.demand_season')
def demand_season_list(request):
    month=Demand.current_month()
    project_id = int(request.GET.get('project') or 0)
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    form = ProjectSeasonForm(initial={'from_year':from_year,'from_month':from_month,'to_year':to_year,'to_month':to_month,
                                      'project':project_id})
    ds = []
    total_sales_count,total_sales_amount, total_sales_commission, total_amount = 0,0,0,0
    if project_id:
        current = date(from_year, from_month, 1)
        end = date(to_year, to_month, 1)
        while current <= end:
            q = Demand.objects.filter(project__id = project_id, year = current.year, month = current.month)
            if q.count() > 0:
                ds.append(q[0])
            current = date(current.month == 12 and current.year + 1 or current.year,
                           current.month == 12 and 1 or current.month + 1, 1)
        for d in ds:
            total_sales_count += d.get_sales().count()
            total_sales_amount += d.get_final_sales_amount()
            total_sales_commission += d.get_sales_commission()
            total_amount += d.get_total_amount()
        
    return render_to_response('Management/demand_season_list.html', 
                              { 'demands':ds, 'start':date(from_year, from_month, 1), 'end':date(to_year, to_month, 1),
                                'project':project_id and Project.objects.get(pk=project_id), 'filterForm':form,
                                'total_sales_count':total_sales_count,
                                'total_sales_amount':total_sales_amount,
                                'total_sales_commission':total_sales_commission,
                                'total_amount':total_amount},
                              context_instance=RequestContext(request))

@permission_required('Management.season_income')
def season_income(request):
    month=Demand.current_month()
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    start = date(from_year, from_month, 1)
    current = date(from_year, from_month, 1)
    end = date(to_year, to_month, 1)
    form = SeasonForm(initial={'from_year':from_year,'from_month':from_month,'to_year':to_year,'to_month':to_month})
    ds = []
    while current <= end:
        q = Demand.objects.filter(year = current.year, month = current.month)
        ds.extend(q)
        current = date(current.month == 12 and current.year + 1 or current.year, current.month == 12 and 1 or current.month + 1, 1)
    projects = []
    total_sale_count, total_amount, total_amount_notax = 0,0,0
    for d in ds:
        tax = Tax.objects.filter(date__lte=date(d.year, d.month,1)).latest().value / 100 + 1
        if not d.project in projects:
            projects.append(d.project)
        p = projects[projects.index(d.project)]
        if not hasattr(p,'total_amount'): p.total_amount = 0
        if not hasattr(p,'total_amount_notax'): p.total_amount_notax = 0
        if not hasattr(p,'total_sale_count'): p.total_sale_count = 0
        amount = d.get_total_amount()
        p.total_amount += amount
        p.total_amount_notax += amount / tax
        p.total_sale_count += d.get_sales().count()
        total_sale_count += d.get_sales().count()
        total_amount += amount
        total_amount_notax += amount / tax
    for p in projects:
        if p.end_date:
            end_date = min(end, p.end_date)
        else:
            end_date = end
        start_date = max(p.start_date, start)
        active_months = round((end_date - start_date).days/30) + 1
        p.avg_sale_count = p.total_sale_count / active_months
        
    month_count = round((end-start).days/30) + 1
    return render_to_response('Management/season_income.html', 
                              { 'start':date(from_year, from_month, 1), 'end':date(to_year, to_month, 1),
                                'projects':projects, 'filterForm':form,'total_amount':total_amount,'total_sale_count':total_sale_count,
                                'total_amount_notax':total_amount_notax,'avg_amount':total_amount/month_count,
                                'avg_amount_notax':total_amount_notax/month_count,'avg_sale_count':total_sale_count/month_count},
                              context_instance=RequestContext(request))

def demand_followup_list(request):
    month=Demand.current_month()
    project_id = int(request.GET.get('project') or 0)
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    form = ProjectSeasonForm(initial={'from_year':from_year,'from_month':from_month,'to_year':to_year,'to_month':to_month,
                                      'project':project_id})
    ds = []
    total_amount, total_invoices, total_payments, total_diff_invoice, total_diff_invoice_payment = 0,0,0,0,0
    if project_id:
        current = date(int(from_year), int(from_month), 1)
        end = date(int(to_year), int(to_month), 1)
        while current <= end:
            q = Demand.objects.filter(project__id = project_id, year = current.year, month = current.month)
            if q.count() > 0:
                ds.append(q[0])
            current = date(current.month == 12 and current.year + 1 or current.year,
                           current.month == 12 and 1 or current.month + 1, 1)
        for d in ds:
            total_amount += d.get_total_amount()
            total_invoices += d.invoices_amount
            total_payments += d.payments_amount
            total_diff_invoice += d.diff_invoice
            total_diff_invoice_payment += d.diff_invoice_payment
        
    return render_to_response('Management/demand_followup_list.html', 
                              { 'demands':ds, 'start':date(int(from_year), int(from_month), 1), 'end':date(int(to_year), int(to_month), 1),
                                'project':project_id and Project.objects.get(pk=project_id), 'filterForm':form,
                                'total_amount':total_amount, 'total_invoices':total_invoices, 'total_payments':total_payments,
                                'total_diff_invoice':total_diff_invoice, 'total_diff_invoice_payment':total_diff_invoice_payment},
                              context_instance=RequestContext(request))

def employeesalary_season_list(request):
    month=Demand.current_month()
    employee_id = int(request.GET.get('employee', 0))
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    form = EmployeeSeasonForm(initial={'from_year':from_year,'from_month':from_month,'to_year':to_year,'to_month':to_month,
                                       'employee':employee_id})
    salaries = []
    total_neto, total_check_amount, total_loan_pay, total_bruto, total_refund, total_sale_count = 0,0,0,0,0,0
    if employee_id:
        current = date(from_year, from_month, 1)
        end = date(to_year, to_month, 1)
        while current <= end:
            q = EmployeeSalary.objects.filter(employee__id = employee_id, year = current.year, month = current.month)
            if q.count() == 1:
                salary = q[0]
                salaries.append(salary)
                total_neto += salary.neto or 0
                total_check_amount += salary.check_amount or 0
                total_loan_pay += salary.loan_pay or 0
                total_bruto += salary.bruto or 0
                total_refund += salary.refund or 0
                total_sale_count += salary.sales_count
            current = date(current.month == 12 and current.year + 1 or current.year,
                           current.month == 12 and 1 or current.month + 1, 1)
        
    return render_to_response('Management/employeesalary_season_list.html', 
                              { 'salaries':salaries, 'start':date(from_year, from_month, 1), 'end':date(to_year, to_month, 1),
                                'employee':employee_id and Employee.objects.get(pk=employee_id), 'filterForm':form,
                                'total_neto':total_neto,'total_check_amount':total_check_amount,
                                'total_loan_pay':total_loan_pay,'total_bruto':total_bruto,
                                'total_refund':total_refund,'total_sale_count':total_sale_count},
                              context_instance=RequestContext(request))

def employeesalary_season_expenses(request):
    month=Demand.current_month()
    employee_id = int(request.GET.get('employee', 0))
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    form = EmployeeSeasonForm(initial={'from_year':from_year,'from_month':from_month,'to_year':to_year,'to_month':to_month,
                                       'employee':employee_id})
    salaries = []
    total_neto, total_check_amount, total_loan_pay, total_bruto, total_bruto_employer, total_refund = 0,0,0,0,0,0
    total_sale_count = 0
    if employee_id:
        current = date(from_year, from_month, 1)
        end = date(to_year, to_month, 1)
        while current <= end:
            q = EmployeeSalary.objects.filter(employee__id = employee_id, year = current.year, month = current.month)
            if q.count() == 1:
                salary = q[0]
                salaries.append(salary)
                total_neto += salary.neto or 0
                total_check_amount += salary.check_amount or 0
                total_loan_pay += salary.loan_pay or 0
                total_bruto += salary.bruto or 0
                total_bruto_employer += salary.bruto_employer_expense or 0
                total_refund += salary.refund or 0
                total_sale_count += salary.sales_count
            current = date(current.month == 12 and current.year + 1 or current.year,
                           current.month == 12 and 1 or current.month + 1, 1)
        
    return render_to_response('Management/employeesalary_season_expenses.html', 
                              { 'salaries':salaries, 'start':date(from_year, from_month, 1), 'end':date(to_year, to_month, 1),
                                'employee':employee_id and Employee.objects.get(pk=employee_id), 'filterForm':form,
                                'total_neto':total_neto,'total_check_amount':total_check_amount,
                                'total_loan_pay':total_loan_pay,'total_bruto':total_bruto,'total_bruto_employer':total_bruto_employer,
                                'total_refund':total_refund,'total_sale_count':total_sale_count},
                              context_instance=RequestContext(request))

def employeesalary_season_total_expenses(request):
    month=Demand.current_month()
    from_year = int(request.GET.get('from_year', month.year))
    from_month = int(request.GET.get('from_month', month.month))
    to_year = int(request.GET.get('to_year', month.year))
    to_month = int(request.GET.get('to_month', month.month))
    form = SeasonForm(initial={'from_year':from_year,'from_month':from_month,'to_year':to_year,'to_month':to_month})
    employees = Employee.objects.all()
    for e in employees:
        e.total_neto, e.total_bruto, e.total_bruto_employer_expense = 0,0,0
    current = date(from_year, from_month, 1)
    end = date(to_year, to_month, 1)
    while current <= end:
        salaries = EmployeeSalary.objects.filter(year = current.year, month = current.month)
        for e in employees:
            q = salaries.filter(employee = e)
            if q.count() != 1: continue
            salary = q[0]
            e.total_neto += salary.neto or 0
            e.total_bruto += salary.bruto or 0
            e.total_bruto_employer_expense += salary.bruto_employer_expense or 0
        current = date(current.month == 12 and current.year + 1 or current.year,
                       current.month == 12 and 1 or current.month + 1, 1)
            
    return render_to_response('Management/employeesalary_season_total_expenses.html', 
                              { 'employees':employees, 'start':date(from_year, from_month, 1), 'end':date(to_year, to_month, 1),
                                'filterForm':form},
                              context_instance=RequestContext(request))
        
def sale_analysis(request):
    sales = []
    include_clients = None
    if request.method == 'POST':
        form = SaleAnalysisForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            rooms_num, house_type = form.cleaned_data['rooms_num'], form.cleaned_data['house_type']
            current = date(int(form.cleaned_data['from_year']), int(form.cleaned_data['from_month']), 1)
            end = date(int(form.cleaned_data['to_year']), int(form.cleaned_data['to_month']), 1)
            while current <= end:
                query = Sale.objects.filter(house__building__project = project, contractor_pay__year = current.year,
                                            contractor_pay__month = current.month)
                if rooms_num:
                    query = query.filter(house__rooms = rooms_num)
                if house_type:
                    query = query.filter(house__type = house_type)
                sales.extend(list(query))
                current = date(current.month == 12 and current.year + 1 or current.year,
                               current.month == 12 and 1 or current.month + 1, 1)
            include_clients = form.cleaned_data['include_clients']
    else:
        form = SaleAnalysisForm()
    return render_to_response('Management/sale_analysis.html', 
                              { 'filterForm':form, 'sales':sales, 'include_clients':include_clients },
                              context_instance=RequestContext(request))