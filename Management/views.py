﻿import settings
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import inlineformset_factory, modelformset_factory
from django.template import RequestContext
from datetime import datetime, date
from forms import *
from django.core import serializers
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list 
from django.contrib.auth.decorators import login_required, permission_required
from pdf import MonthDemandWriter, MonthProjectsWriter
from mail import mail

@login_required
def index(request):
    return render_to_response('Management/index.html',
                              {'locateHouseForm':LocateHouseForm()},
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
def limited_create_object(request, permission, *args, **kwargs):
    if request.user.has_perm('Management.' + permission):
        return create_object(request, *args, **kwargs)
    else:
        return HttpResponse('No permission. contact Elad.')

@login_required
def limited_update_object(request, permission, *args, **kwargs):
    if request.user.has_perm('Management.' + permission):
        return update_object(request, *args, **kwargs)
    else:
        return HttpResponse('No permission. contact Elad.')

@login_required
def limited_object_list(*args, **kwargs):
    return object_list(*args, **kwargs)
    
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
    
@login_required
def employeecheck_del(request, id):
    ec = EmployeeCheck.objects.get(pk=id)
    ec.delete()
    return HttpResponseRedirect('/employeechecks') 

@permission_required('Management.delete_advancepayment')
def advance_payment_del(request, id):
    ap = AdvancePayment.objects.get(pk=id)
    ap.delete()
    return HttpResponseRedirect('/advancepayments') 

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

@permission_required('Management.delete_loan')
def loan_del(request, id):
    l = Loan.objects.get(pk=id)
    l.delete()
    return HttpResponseRedirect('/loans') 

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
    
@login_required
def check_del(request, id):
    c = Check.objects.get(pk=id)
    c.delete()
    return HttpResponseRedirect('checks') 

def signup_list(request, project_id):
    p = Project.objects.get(pk = project_id)
    if request.method == 'POST':
        filterForm = MonthFilterForm(request.POST)
        if filterForm.is_valid():
            y = int(filterForm.cleaned_data['year'])
            m = int(filterForm.cleaned_data['month'])
            month = datetime(y,m,1)
            signups = p.signups(y, m)
    else:
        filterForm = MonthFilterForm()
        signups = p.signups()
        month = datetime.now()
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
def employee_account(request, id):
    employee = Employee.objects.get(pk=id)
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
    
@permission_required('Management.delete_account')
def employee_account_delete(request, id):
    e = Employee.objects.get(pk=id)
    e.account.delete()
    return HttpResponseRedirect('./')

@permission_required('Management.list_demand')
def demand_function(request,id , function):
    d = Demand.objects.get(pk=id)
    function(d)
    return HttpResponse('ok')

@permission_required('Management.list_demand')
def demand_old_list(request):
    if request.method=='POST':
        form = MonthFilterForm(request.POST)
        if form.is_valid():
            month = datetime(int(form.cleaned_data['year']), int(form.cleaned_data['month']), 1)
            ds = Demand.objects.filter(year = month.year, month = month.month)
    else:
        form = MonthFilterForm()
        ds = Demand.objects.current()
        month = datetime.now()
        if month.day <= 22:
            month = datetime(month.year, month.month == 1 and 12 or month.month - 1, month.day)
    total_sales_count,total_sales_amount, total_sales_commission, total_amount = (0,0,0,0)
    for d in ds.all():
        d.calc_sales_commission()
        total_sales_count += d.get_sales().count()
        total_sales_amount += d.get_sales_amount()
        total_sales_commission += d.get_sales_commission()
        total_amount += d.get_total_amount()
    unhandled_projects = []
    for p in Project.objects.active():
        d = ds.get(project=p)
        if d.statuses.count()==0 or d.statuses.latest().type.id != DemandSent:
            unhandled_projects.append(p)
        
    return render_to_response('Management/demand_old_list.html', 
                              { 'demands':ds, 'month':month,'filterForm':form,'total_sales_count':total_sales_count,
                                'total_sales_amount':total_sales_amount,'total_sales_commission':total_sales_commission,
                                'total_amount':total_amount, 'unhandled_projects':unhandled_projects},
                              context_instance=RequestContext(request))

@permission_required('Management.change_employeesalary')
def employee_salary_approve(request, id):
    es = EmployeeSalary.objects.get(pk=id)
    es.approved = True
    es.save()
    return HttpResponse('ok')

@permission_required('Management.list_employeesalary')
def employee_salary_list(request):
    if request.method=='POST':
        form = MonthFilterForm(request.POST)
        if form.is_valid():
            month = datetime(int(form.cleaned_data['year']), int(form.cleaned_data['month']), 1)
            for e in Employee.objects.active().filter(work_start__lt = month):
                try:
                    es = EmployeeSalary.objects.get(employee=e, year = month.year, month = month.month)
                except EmployeeSalary.DoesNotExist:
                    es = EmployeeSalary(employee = e, month = month.month, year = month.year, approved=False)
                es.base = e.employment_terms and e.employment_terms.salary_base or 0
                es.calculate()
                es.save()
            salaries = EmployeeSalary.objects.filter(year = month.year, month = month.month)
    else:
        form = MonthFilterForm()
        salaries = EmployeeSalary.objects.current()
        month = datetime.now()
        if month.day <= 22:
            month = datetime(month.year, month.month == 1 and 12 or month.month - 1, month.day)
        
    return render_to_response('Management/employee_salaries.html', 
                              { 'salaries':salaries, 'month':month,'filterForm':form},
                              context_instance=RequestContext(request))

@permission_required('Management.list_demand')
def demands_all(request):
    if request.method == 'POST':
        error = None
        houseForm = LocateHouseForm(request.POST)
        demandForm = LocateDemandForm(request.POST)
        if houseForm.is_valid():
            houses = House.objects.filter(building__project = houseForm.cleaned_data['project'], 
                                          building__num = houseForm.cleaned_data['building_num'],
                                          num = houseForm.cleaned_data['house_num'])
            if houses.count() > 0:
                return HttpResponseRedirect('/buildings/%s/house/%s' % (houses[0].building.id, houses[0].id))
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
    return render_to_response('Management/demands_all.html', 
                              { 'projects':Project.objects.all(),
                               'houseForm':LocateHouseForm(), 
                               'demandForm':LocateDemandForm(),
                               'error':error },
                              context_instance=RequestContext(request))

@permission_required('Management.add_demand')
def demand_list(request):
    if request.method == 'POST':
        form = MonthFilterForm(request.POST)
        if form.is_valid():
            ds = Demand.objects.filter(year = form.cleaned_data['year'], month = form.cleaned_data['month'])
            month = datetime(int(form.cleaned_data['year']),int(form.cleaned_data['month']),1)
        else:
            return HttpResponseRedirect('/demands')
    else:
        ds = Demand.objects.current()
        form = MonthFilterForm()
        month = datetime.now()
        if month.day <= 22:
            month = datetime(month.year, month.month == 1 and 12 or month.month - 1, month.day)
    unhandled_projects = list(Project.objects.active())
    '''loop through all active projects and create demands for them if havent
    alredy created. if project has status other than Feed, it is handled'''        
    for p in Project.objects.active():
        if ds.filter(project = p).count() == 0:
            demand = Demand(project = p, month = month.month, year = month.year, fixed_pay = p.commissions.add_amount,
                            fixed_pay_type = p.commissions.add_type)
            demand.save()
        elif ds.get(project=p).statuses.count() > 0 and ds.get(project=p).statuses.latest().type.id != DemandFeed:
            unhandled_projects.remove(p)
    return render_to_response('Management/demand_list.html', 
                              { 'demands':ds, 'unhandled_projects':unhandled_projects, 'month':month,
                               'filterForm':form },
                              context_instance=RequestContext(request))

@permission_required('Management.list_demand')
def demand_unpaid_list(request):
    ds = Demand.objects.current()
    ds = [d for d in ds.all() if d.statuses.latest().type.id == 3 and d.payments.count() == 0]
    return render_to_response('Management/demand_charge_list.html', 
                              { 'demands':ds },
                              context_instance=RequestContext(request))

@permission_required('Management.list_demand')
def demand_paidsome_list(request):
    ds = Demand.objects.current()
    ds = [d for d in ds.all() if d.statuses.latest().type.id == 3 and d.diff() != 0]
    return render_to_response('Management/demand_charge_list.html', 
                              { 'demands':ds },
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
        
def demand_sales(request, id):
    return render_to_response('Management/demand_sales.html', 
                              { 'demand':Demand.objects.get(pk=id) },
                              context_instance=RequestContext(request))

@permission_required('Management.change_demand')
def demand_close(request, id):
    d = Demand.objects.get(pk=id)
    if d.statuses.count() == 0 or d.statuses.latest().type.id == DemandFeed:
        d.close()
    return HttpResponseRedirect('/demands')

@permission_required('Management.change_demand')
def demand_zero(request, id):
    d = Demand.objects.get(pk=id)
    if d.statuses.count() == 0:
        d.feed()
    return HttpResponseRedirect('/demands')

@permission_required('Management.change_demand')
def demand_send(request, id):
    d = Demand.objects.get(pk=id)
    d.send()
    filename = settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
    write_demand_pdf(d, filename)
    mail(d.project.demand_contact.mail,
         u'עמלה לפרויקט %s לחודש %s/%s' % (d.project, d.month, d.year),
         '', filename)
    return HttpResponseRedirect('/demandsold')

@permission_required('Management.change_demand')
def demand_closeall(request):
    for d in Demand.objects.current():
        if d.statuses.latest().type.id == DemandFeed:
            d.close()
    return HttpResponseRedirect('/demands')

@permission_required('Management.change_demand')
def demand_sendall(request):
    if request.method == 'POST':
        for d in Demand.objects.current():
            d.send()
        return HttpResponseRedirect('/reports')
    else:
        now = datetime.now()
        projects = [p for p in Project.objects.all() if p.current_demand() == None]   
        employees = []
        for e in Employee.objects.filter(work_end = None):
            for s in e.sales.all():
                if s.demand.month.year == now.year and s.demand.month.month == now.month:  
                    out = True
            if not out:
                employees.append(e)
        if len(employees) == 0 and len(projects) == 0:
            for d in Demand.objects.current():
                finish_demand(d)
                d.send()
            return HttpResponseRedirect('/reports')
        else:
            return render_to_response('Management/demand_send_confirm.html', 
                                      { 'projects':projects, 'employees' : employees },
                                      context_instance=RequestContext(request))
            
def finish_demand(demand):
    demand.finish()
        
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
    y,m = (sale.demand.year, sale.demand.month)
    sr = SaleReject(sale = sale, date = date.today(), to_month=date(m+1==13 and y+1 or y, m+1==13 and 1 or m+1,1),
                    employee_pay = date(y,m,1))
    sr.save()
    return HttpResponseRedirect('/salereject/%s' % sr.id)

@permission_required('Management.add_invoice')
def invoice_add(request, initial=None):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.has_key('addanother'):
                form = InvoiceForm(initial=initial)
    else:
        form = InvoiceForm(initial=initial)
    return render_to_response('Management/invoice_edit.html', {'form':form}, context_instance=RequestContext(request))


@permission_required('Management.add_invoice')
def demand_invoice_add(request, id):
    demand = Demand.objects.get(pk=id)
    return invoice_add(request, {'project':demand.project.id, 'month':demand.month, 'year':demand.year})
   
@permission_required('Management.add_invoice')
def project_invoice_add(request, id):
    return invoice_add(request, {'project':id})

@permission_required('Management.delete_invoice')
def invoice_del(request, id):
    i = Invoice.objects.get(pk=id)
    i.delete()
    return HttpResponseRedirect('/demands/%s' % i.demand.id)

@permission_required('Management.add_payment')
def payment_add(request, initial=None):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.has_key('addanother'):
                form = PaymentForm(initial=initial)
    else:
        form = PaymentForm(initial=initial)
    return render_to_response('Management/payment_edit.html', 
                              { 'form':form }, context_instance=RequestContext(request))
def payment_details(request, project, year, month):
    try:
        d = Demand.objects.get(project = project, year = year, month = month)
        return render_to_response('Management/demand_payment_details.html', 
                                  { 'demand':d}, context_instance=RequestContext(request))
    except Demand.DoesNotExist:
        return HttpResponse('')
def invoice_details(request, project, year, month):
    try:
        d = Demand.objects.get(project = project, year = year, month = month)
        return render_to_response('Management/demand_invoice_details.html', 
                                  { 'demand':d}, context_instance=RequestContext(request))
    except Demand.DoesNotExist:
        return HttpResponse('')
@permission_required('Management.add_payment')
def demand_payment_add(request, id):
    demand = Demand.objects.get(pk=id)
    return payment_add(request, {'project':demand.project.id, 'month':demand.month, 'year':demand.year})
    
@permission_required('Management.add_payment')
def project_payment_add(request, id):    
    demand = Demand.objects.get(pk=id)
    return payment_add(request, {'project':id})
 
@permission_required('Management.delete_payment')
def payment_del(request, id):
    p = Payment.objects.get(pk=id)
    p.delete()
    return HttpResponseRedirect('/demands/%s' % p.demand.id)

@login_required
def project_list(request):    
    projects = Project.objects.filter(end_date = None)
    return render_to_response('Management/project_list.html',
                              {'projects': projects}, 
                              context_instance=RequestContext(request))

@login_required
def project_archive(request):    
    projects = Project.objects.exclude(end_date = None)
    return render_to_response('Management/project_archive.html',
                              {'projects': projects}, 
                              context_instance=RequestContext(request))

@permission_required('Management.change_pricelist')
def building_pricelist(request, object_id, type_id):
    b = Building.objects.get(pk = object_id)
    InlineFormSet = inlineformset_factory(Pricelist, ParkingCost, can_delete=False, extra=5, max_num=5)
    if request.method == 'POST':
        form = PricelistForm(request.POST, instance=b.pricelist)
        formset = InlineFormSet(request.POST, instance = b.pricelist)
        if form.is_valid():
            form.save()
            if formset.is_valid():
                formset.save()            
    else:
        form = PricelistForm(instance = b.pricelist)
        formset = InlineFormSet(instance = b.pricelist)
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
                              {'form': form, 'formset': formset, 'houses' : houses, 'signup_count':signup_count, 
                               'sale_count':sale_count, 'avaliable_count':avaliable_count,
                               'type':PricelistType.objects.get(pk=type_id), 'types':PricelistType.objects.all()}, 
                              context_instance=RequestContext(request))

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
    
@permission_required('Management.change_project')
def project_end(request, id):
    project = Project.objects.get(pk= id)
    project.end()
    project.save()
    return HttpResponseRedirect('/projects')
    
@permission_required('Management.change_project')
def project_edit(request, id):
    project = Project.objects.get(pk=id)
    details = project.details or ProjectDetails()
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        pcForm = ProjectCommissionForm(request.POST, request.FILES, instance=project.commissions, prefix='pc')
        if request.FILES.has_key('pc-agreement'):
            pcForm.instance.agreement = request.FILES['pc-agreement']
        detailsForm = ProjectDetailsForm(request.POST, instance=details, prefix='det')
        if form.is_valid():
            form.save()
        if pcForm.is_valid():
            pcForm.save()        
        if detailsForm.is_valid():
            project.details = detailsForm.save()
            project.save()
    else:
        form = ProjectForm(instance=project)
        detailsForm = ProjectDetailsForm(instance=details, prefix='det')
        pcForm = ProjectCommissionForm(instance=project.commissions, prefix='pc')
        
    return render_to_response('Management/project_edit.html', 
                              { 'form':form, 'pcForm':pcForm, 'detailsForm':detailsForm, 'project':project },
                              context_instance=RequestContext(request))
  
@login_required  
def project_commission_del(request, project_id, attribute):
    project = Project.objects.get(pk = project_id)
    c = project.commissions
    obj = getattr(c, attribute)
    #unlink commission from project
    setattr(c, attribute, None)
    project.commissions.save()
    #delete commission
    obj.delete()
    return HttpResponseRedirect('/projects/%s' % project.id)

@login_required
def employee_commission_del(request, employee_id, project_id, attribute):
    employee = Employee.objects.get(pk = employee_id)
    c = employee.commissions.filter(project__id = project_id)[0]
    obj = getattr(c, attribute)
    #unlink commission from employee
    setattr(c, attribute, None)
    c.save()
    #delete commission
    obj.delete()
    return HttpResponseRedirect('/employees/%s' % employee.id)
        
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
                              { 'formset':formset,'form':form, 'project':project,'show_house_num':True },
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
            
    return render_to_response('Management/commission.html', 
                              { 'form':form, 'project':project},
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
            
    return render_to_response('Management/commission.html', 
                              { 'form':form, 'project':project},
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
            
    return render_to_response('Management/commission.html', 
                              { 'form':form, 'project':project},
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

def contact_list(request):
    c = Contact.objects.all()
    if request.method=='POST':
        form = ContactFilterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['first_name']:
                c = c.filter(first_name = form.cleaned_data['first_name'])
            if form.cleaned_data['last_name']:
                c = c.filter(last_name = form.cleaned_data['last_name'])
            if form.cleaned_data['role']:
                c = c.filter(role = form.cleaned_data['role'])
            if form.cleaned_data['company']:
                c = c.filter(company = form.cleaned_data['company'])
    else:
        form = ContactFilterForm()
    return render_to_response('Management/contact_list.html', 
                              { 'object_list':c.all(), 'filterForm':form },
                              context_instance=RequestContext(request))
    
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
        form = ReminderForm(initial={'status':ReminderStatusAdded})
    
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
    if r.statuses.latest().type.id == ReminderStatusDeleted:
        return HttpResponse('reminder is already deleted')
    else:
        r.delete()
        return HttpResponse('ok')
    
@permission_required('Management.change_reminder')
def reminder_do(request, id):
    r = Reminder.objects.get(pk= id)
    if r.statuses.latest().type.id == ReminderStatusDone:
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
            form.save()
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect('../addhouse/type%s' % type_id)
            elif request.POST.has_key('finish'):
                return HttpResponseRedirect('../pricelist/type%s' % type_id)
    else:
        form = HouseForm(type_id)
        form.instance.building = b
        if b.is_cottage():
            form.initial['type'] = HouseTypeCottage

    ps = Parking.objects.filter(building = b)
    ss = Storage.objects.filter(building = b)
    for f in ['parking1','parking2','parking3']:
        form.fields[f].queryset = ps
    for f in ['storage1','storage2']:
        form.fields[f].queryset = ss
    return render_to_response('Management/house_edit.html', 
                              {'form' : form, 'type':PricelistType.objects.get(pk = type_id) })

@permission_required('Management.add_house')
def house_edit(request,id , type_id):
    h = House.objects.get(pk=id)
    b = h.building
    if request.method == 'POST':
        form = HouseForm(type_id, data = request.POST, instance = h)
        if form.is_valid():
            form.save()
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect('../../addhouse/type%s' % type_id)
            elif request.POST.has_key('finish'):
                return HttpResponseRedirect('../../pricelist/type%s' % type_id)
    else:
        form = HouseForm(type_id, instance = h)
        if b.is_cottage():
            form.initial['type'] = HouseTypeCottage

    ps = Parking.objects.filter(building = b)
    ss = Storage.objects.filter(building = b)
    for f in ['parking1','parking2','parking3']:
        form.fields[f].queryset = ps
    for f in ['storage1','storage2']:
        form.fields[f].queryset = ss
    return render_to_response('Management/house_edit.html', 
                              {'form' : form, 'type':PricelistType.objects.get(pk = type_id) })
        
@login_required
def employee_end(request, id):
    e = Employee.objects.get(pk= id)
    e.end()
    e.save()
    return HttpResponseRedirect('/employees')

@login_required
def employee_archive(request):
    return render_to_response('Management/employee_archive.html', 
                              { 'employee_list': Employee.objects.archive()},
                              context_instance=RequestContext(request)) 
@login_required
def employee_list(request):
    return render_to_response('Management/employee_list.html', 
                              { 'employee_list': Employee.objects.active()},
                              context_instance=RequestContext(request)) 

@permission_required('Management.add_loan')
def employee_loans(request, employee_id):
    return render_to_response('Management/employee_loans.html', 
                              { 'employee': Employee.objects.get(pk=employee_id)},
                              context_instance=RequestContext(request))
    
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
        form = LoanPayForm()
    return render_to_response('Management/object_edit.html',
                              {'form' : form}, context_instance=RequestContext(request))

@permission_required('Management.add_employmentterms')
def employee_employmentterms(request, id):
    employee = Employee.objects.get(pk = id)
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
                              { 'formset':formset,'form':form, 'employee':employee, 'show_house_num':True },
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
                              { 'formset':formset,'form':form, 'employee':employee, 'show_house_num':True },
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
                              { 'formset':formset, 'employee':employee, 'show_house_num':False },
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
                              { 'formset':formset, 'employee':employee, 'show_house_num':False},
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
                              { 'formset':formset, 'employee':employee, 'show_house_num':False},
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
            
    return render_to_response('Management/commission.html', 
                              { 'form':form, 'employee':employee },
                              context_instance=RequestContext(request))
        
@login_required
def json_buildings(request, project_id):
    data = serializers.serialize('json', Project.objects.get(pk= project_id).non_deleted_buildings(), 
                                 fields=('id','name','num'))
    return HttpResponse(data)

@login_required
def json_employees(request, project_id):
    data = serializers.serialize('json', Project.objects.get(pk= project_id).employees.all(), 
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
    tasks = request.user.tasks.filter(is_deleted = False)
    if request.method=='POST':
        filterForm = TaskFilterForm(request.POST)
        if filterForm.is_valid():
            sender = filterForm.cleaned_data['sender']
            status = filterForm.cleaned_data['status']
            if sender == 'me':
                tasks = tasks.filter(sender = request.user)
            if sender == 'others':
                tasks = tasks.filter(user = request.user)
            if status == 'done':
                tasks = tasks.filter(is_done = True)
            if status == 'undone':
                tasks = tasks.filter(is_done = False)
        else:
            tasks = tasks.filter(is_done= False, user = request.user)
            filterForm = TaskFilterForm()            
    else:
        tasks = tasks.filter(is_done= False, user = request.user)
        filterForm = TaskFilterForm()
    
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

@permission_required('Management.delete_link')
def link_del(request, id):
    l = Link.objects.get(pk = id)
    l.delete()
    return HttpResponseRedirect('/links')

@permission_required('Management.delete_car')
def car_del(request, id):
    c = Car.objects.get(pk = id)
    c.delete()
    return HttpResponseRedirect('/cars')

@login_required
def attachment_list(request):
    attachments = Attachment.objects.all()
    return render_to_response('Management/attachment_list.html',
                              {'attachments': attachments}, context_instance=RequestContext(request))

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
@login_required
def madad_list(request):
    return render_to_response('Management/madad_list.html', 
                              {'madads':Madad.objects.all()},
                              context_instance=RequestContext(request))   
    
@permission_required('Management.delete_madad')
def madad_del(request, id):
    Madad.objects.get(pk=id).delete()
    return HttpResponseRedirect('/madad')

@login_required
def tax_list(request):
    return render_to_response('Management/tax_list.html', 
                              {'taxs':Tax.objects.all()},
                              context_instance=RequestContext(request))   
    
@permission_required('Management.delete_madad')
def tax_del(request, id):
    Tax.objects.get(pk=id).delete()
    return HttpResponseRedirect('/tax')

@permission_required('Management.change_sale')
def sale_edit(request, id):
    sale = Sale.objects.get(pk=id)
    if request.POST:
        form = SaleForm(request.POST, instance = sale)
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
                if sale.house != form.cleaned_data['house']:
                    shm = SaleHouseMod(sale = sale, old_house = sale.house, date=date.today())
                    shm.save()
                    next = '/salehousemod/%s' % shm.id
            form.save()
            sale.demand.calc_sales_commission()
            for employee in project.employees.all():
                es = employee.salaries.get_or_create(year = sale.demand.year, month = sale.demand.month)
                es[0].calculate()
                es[0].save()
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect(next or '/demands/%s/sale/add' % sale.demand.id)
            elif request.POST.has_key('todemand'):
                return HttpResponseRedirect(next or '/demands/%s' % sale.demand.id)
    else:
        form = SaleForm(instance= sale)
    return render_to_response('Management/sale_edit.html', 
                              {'form':form},
                              context_instance=RequestContext(request))    

@permission_required('Management.add_sale')
def sale_add(request, demand_id=None):
    if request.POST:
        form = SaleForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            demand = demand_id and Demand.objects.get(pk=demand_id) or project.current_demand()
            form.instance.demand = demand
            form.save()
            next = None
            if demand.statuses.count() == 0:
                demand.feed()
            if demand.statuses.latest().type.id == DemandSent:
                y,m = (demand.year, demand,month)
                sp = SalePre(sale = form.instance, date=date.today(),
                             employee_pay = date(m+1==13 and y+1 or y,m+1==13 and 1 or m, 1))
                sp.save()
                next = '/salepre/%s' % sp.id 
            demand.calc_sales_commission()
            for employee in project.employees.all():
                es = employee.salaries.get_or_create(year = demand.year, month = demand.month)
                es[0].calculate()
                es[0].save()
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect(next or (demand_id and '/demands/%s/sale/add' % demand_id or '/sale'))
            elif request.POST.has_key('todemand'):
                return HttpResponseRedirect(next or '/demands/%s' % demand.id)
    else:
        form = SaleForm()
        if demand_id:
            p = Demand.objects.get(pk=demand_id).project
            form.fields['project'].initial = p.id
            form.fields['employee'].queryset = p.employees.all()
            form.fields['building'].queryset = p.buildings.all()
    return render_to_response('Management/sale_edit.html', 
                              {'form':form},
                              context_instance=RequestContext(request))
       
def project_sales(request, id):
    p = Project.objects.get(pk=id)
    d = p.current_demand()
    salesTotal = 0
    if d:    
        sales = d.get_sales().all()
        for s in sales:
            salesTotal = salesTotal + s.price
    else:
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

def write_demand_pdf(demand, filename):
    p = open(filename,'w+')
    p.flush()
    p.close()
    MonthDemandWriter(demand).build(filename)    

@permission_required('Management.report_project_month')
def report_project_month(request, project_id, year, month):
    filename = settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    demand = Demand.objects.get(project__id = project_id, year = year, month = month)
    write_demand_pdf(demand, filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@permission_required('Management.report_projects_month')
def report_projects_month(request, year, month):
    filename = settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    p = open(filename,'w+')
    p.flush()
    p.close()
    MonthProjectsWriter(year, month).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

@login_required
def report_project_time(request):
    if request.method=='POST':
        form = DemandReportForm(request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            salaries = ProjectSalary.objects.filter(project=project, month__year = datetime.now().year).all()
            salesTotal, amountTotal = (0,0)
            for s in salaries:
                salesTotal = salesTotal + s.sales_total
                amountTotal = amountTotal + s.amount_total
            return render_to_response('Management/report_project_year.html', 
                                      {'project':project, 'salaries':salaries, 'salesTotal':salesTotal, 'amountTotal':amountTotal},
                                      context_instance=RequestContext(request))
    return HttpResponseRedirect('/reports')