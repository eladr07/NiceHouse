import settings
import time
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
from pdf import MonthDemandWriter, MonthProjectsWriter, EmployeeListWriter, EmployeeSalariesWriter
from mail import mail

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

@permission_required('Management.list_demand')
def demand_calc(request, id):
    d = Demand.objects.get(pk=id)
    d.calc_sales_commission()
    return HttpResponseRedirect('/demandsold/%s/%s' % (d.year,d.month))

@permission_required('Management.list_demand')
def demand_old_list(request, year=demand_month().year, month=demand_month().month):
    ds = Demand.objects.filter(year = year, month = month)
    total_sales_count,total_sales_amount, total_sales_commission, total_amount = (0,0,0,0)
    for d in ds:
        total_sales_count += d.get_sales().count()
        total_sales_amount += d.get_sales_amount()
        total_sales_commission += d.get_sales_commission()
        total_amount += d.get_total_amount()
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
                              { 'demands':ds, 'month':date(int(year), int(month), 1),
                                'filterForm':MonthFilterForm(initial={'year':year,'month':month}),
                                'total_sales_count':total_sales_count,
                                'total_sales_amount':total_sales_amount,
                                'total_sales_commission':total_sales_commission,
                                'total_amount':total_amount, 
                                'unhandled_projects':unhandled_projects},
                              context_instance=RequestContext(request))

@permission_required('Management.change_employeesalary')
def employee_salary_approve(request, model, id):
    es = model.objects.get(pk=id)
    es.approved = True
    es.save()
    return HttpResponse('ok')

def employee_salary_details(request, model, id):
    return render_to_response('Management/employee_commission_details.html', 
                              { 'salary':model.objects.get(pk=id)},
                              context_instance=RequestContext(request))

def employee_salary_check_details(request, model, id):
    return render_to_response('Management/employee_salary_check_details.html', 
                              { 'salary':model.objects.get(pk=id)},
                              context_instance=RequestContext(request))

def employee_salary_total_details(request, model, id):
    return render_to_response('Management/employee_salary_total_details.html', 
                              { 'salary':model.objects.get(pk=id)},
                              context_instance=RequestContext(request))

@permission_required('Management.list_employeesalary')
def employee_salary_list(request, year = date.today().year, month = date.today().month):
    for e in Employee.objects.active():
        es, new = EmployeeSalary.objects.get_or_create(employee = e, month = month, year = year)
        if new or not es.commissions or not es.base: 
            es.calculate()
            es.save()
    return render_to_response('Management/employee_salaries.html', 
                              {'salaries':EmployeeSalary.objects.filter(year = year, month = month), 
                               'month': date(int(year), int(month), 1),
                               'filterForm':MonthFilterForm(initial={'year':year,'month':month})},
                               context_instance=RequestContext(request))

@permission_required('Management.list_nhemployeesalary')
def nhemployee_salary_list(request, year=demand_month().year, month=demand_month().month):
    for e in NHEmployee.objects.active():
        es, new = NHEmployeeSalary.objects.get_or_create(nhemployee = e, month = month, year = year)
        if new or not es.commissions or not es.base: 
            es.calculate()
            es.save()
    return render_to_response('Management/nhemployee_salaries.html', 
                              {'salaries':NHEmployeeSalary.objects.filter(year = year, month = month), 
                               'month': date(int(year), int(month), 1),
                               'filterForm':MonthFilterForm(initial={'year':year,'month':month})},
                               context_instance=RequestContext(request))

def employee_salary_pdf(request, year, month):
    filename = settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    p = open(filename,'w+')
    p.flush()
    p.close()
    EmployeeSalariesWriter(year, month).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response    

def employee_salary_calc(request, model, id):
    es = model.objects.get(pk=id)
    es.calculate()
    es.save()
    return HttpResponseRedirect('/employeesalaries/%s/%s' % (es.year, es.month))

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
    return render_to_response('Management/demands_all.html', 
                              { 'projects':Project.objects.all(),
                               'houseForm':LocateHouseForm(), 
                               'demandForm':LocateDemandForm(),
                               'error':error },
                              context_instance=RequestContext(request))

def employee_list_pdf(request):
    filename = settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    p = open(filename,'w+')
    p.flush()
    p.close()
    EmployeeListWriter(employees = Employee.objects.active(),
                       nhemployees = NHEmployee.objects.active()).build(filename)
    p = open(filename,'r')
    response.write(p.read())
    p.close()
    return response

def nhmonth_sales(request, nhbranch_id, year=None, month=None):
    if year and month:
        q = NHMonth.objects.filter(nhbranch__id = nhbranch_id, year=year, month=month)
    else:
        q = NHMonth.objects.filter(nhbranch__id = nhbranch_id)
    nhb = NHBranch.objects.get(pk=nhbranch_id)
    nhm = q.count() > 0 and q[0] or NHMonth(nhbranch = nhb, year = year or date.today().year, month = month or date.today().month)
    total_net_income = 0
    for sale in nhm.nhsales.all():
        for saleside in sale.nhsaleside_set.all():
            total_net_income += saleside.net_income
    form = MonthFilterForm(initial={'year':nhm.year,'month':nhm.month})
    return render_to_response('Management/nhmonth_sales.html', 
                              { 'nhmonth':nhm, 'filterForm':form, 'total_net_income':total_net_income },
                              context_instance=RequestContext(request))

@permission_required('Management.change_nhmonth')
def nhmonth_close(request, id):
    nhm = NHMonth.objects.get(pk=id)
    nhm.close()
    nhm.save()
    form = MonthFilterForm(initial={'year':nhm.year,'month':nhm.month})
    return render_to_response('Management/nhmonth_sales.html', 
                              { 'nhmonth':nhm, 'filterForm':form },
                              context_instance=RequestContext(request))

@permission_required('Management.add_demand')
def demand_list(request, year=demand_month().year, month=demand_month().month):
    ds = Demand.objects.filter(year = year, month = month)
    form = MonthFilterForm(initial={'year':year,'month':month})
    unhandled_projects = list(Project.objects.active())
    '''loop through all active projects and create demands for them if havent
    alredy created. if project has status other than Feed, it is handled'''        
    for p in Project.objects.active():
        if ds.filter(project = p).count() == 0:
            demand = Demand(project = p, month = month, year = year, fixed_pay = p.commissions.add_amount,
                            fixed_pay_type = p.commissions.add_type)
            demand.save()
        elif ds.get(project=p).statuses.count() > 0 and ds.get(project=p).statuses.latest().type.id != DemandFeed:
            unhandled_projects.remove(p)
    sales_count, sales_amount = (0,0)
    for d in ds:
        sales_count += d.get_sales().count()
        sales_amount += d.get_final_sales_amount()
    return render_to_response('Management/demand_list.html', 
                              { 'demands':ds, 'unhandled_projects':unhandled_projects, 
                               'month':date(int(year), int(month), 1), 'filterForm':form,
                               'sales_count':sales_count ,'sales_amount':sales_amount },
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
    return render_to_response('Management/employee_sales.html', 
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
        d.close()
    return HttpResponseRedirect('/demands')

def demand_send_mail(demand, addr):
    filename = settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
    write_demand_pdf(demand, filename)
    mail(addr,
         u'עמלה לפרויקט %s לחודש %s/%s' % (demand.project, demand.month, demand.year),
         '', filename)
    demand.send()

@permission_required('Management.change_demand')
def demands_send(request):
    forms=[]
    if request.method == 'POST':
        form = MonthFilterForm(request.POST)
        if form.is_valid():
            ds = Demand.objects.filter(year = form.cleaned_data['year'], month = form.cleaned_data['month'])
            month = datetime(int(form.cleaned_data['year']),int(form.cleaned_data['month']),1)
            error = True
        else:
            month = demand_month()
            error = False
        for d in Demand.objects.filter(year=month.year, month=month.month):
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
        month = demand_month()
        form = MonthFilterForm()
        for d in Demand.objects.filter(year=month.year, month=month.month):
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
    if sale.demand.statuses.latest().type.id == DemandSent:
        y,m = (sale.demand.year, sale.demand.month)
        sr = sale.salereject or SaleReject(sale = sale, employee_pay = date(y,m,1))
        sr.date = date.today()
        sr.to_month = date(m+1==13 and y+1 or y, m+1==13 and 1 or m+1,1)
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
    else:
        form = DemandInvoiceForm(initial=initial)
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
    demand_id = i.demands.all()[0].id
    i.delete()
    return HttpResponseRedirect('/demands/%s' % demand_id)

@permission_required('Management.add_payment')
def payment_add(request, initial=None):
    if request.method == 'POST':
        form = DemandPaymentForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.has_key('addanother'):
                form = DemandPaymentForm(initial=initial)
    else:
        form = DemandPaymentForm(initial=initial)
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

@permission_required('Management.add_payment')
def nhsaleside_payment_add(request, object_id):
    nhs = NHSaleSide.objects.get(pk=object_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            p = form.save()
            nhs.payments.add(p)
            if request.POST.has_key('addanother'):
                form = PaymentForm()
    else:
        form = PaymentForm()
    return render_to_response('Management/payment_edit.html', 
                              { 'form':form }, context_instance=RequestContext(request))
    
@permission_required('Management.invoice')
def nhsaleside_invoice_add(request, object_id):
    nhs = NHSaleSide.objects.get(pk=object_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            i = form.save()
            nhs.invoices.add(i)
    else:
        form = InvoiceForm()
    return render_to_response('Management/invoice_edit.html', 
                              { 'form':form }, context_instance=RequestContext(request))

 
@permission_required('Management.delete_payment')
def payment_del(request, id):
    p = Payment.objects.get(pk=id)
    if i.demands.count() == 1:
        next = '/demands/%s' % i.demands.all()[0].id
    elif i.nhsaleside_set.count() == 1:
        next = '/nhsale/%s' % i.nhsaleside_set.all()[0].nhsale.id
    p.delete()
    return HttpResponseRedirect(next)

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

@permission_required('Management.change_nhsale')
def nhsale_edit(request, object_id):
    nhs = NHSale.objects.get(pk=object_id)
    return render_to_response('Management/nhsale_edit.html',
                              {'nhs': nhs}, 
                              context_instance=RequestContext(request))

@permission_required('Management.add_nhsale')
def nhsale_add(request, branch_id):
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
            side1, side2 = (side1Form.save(), side2Form.save())
            error = False
            if invoice1Form.is_valid():
                side1.invoices.add(invoice1Form.save())
            else:
                error = invoice1Form.has_changed()
            if payment1Forms.is_valid():
                for p in payment1Forms.save():
                    side1.payments.add(p)
            else:
                error = payment1Forms.has_changed()
            if invoice2Form.is_valid():
                side2.invoices.add(invoice2Form.save())
            else:
                error = invoice2Form.has_changed()
            if payment2Forms.is_valid():
                for p in payment2Forms.save():
                    side2.payments.add(p)
            else:
                error = payment2Forms.has_changed()
            if not error:
                if request.POST.has_key('addanother'):
                    return HttpResponseRedirect('add')
                elif request.POST.has_key('tomonth'):
                    return HttpResponseRedirect('/nhbranch/%s/sales' % nhsale.nhbranch.id)
    else:
        saleForm = NHSaleForm(prefix='sale')
        monthForm = NHMonthForm(prefix='month')
        monthForm.fields['nhbranch'].initial = branch_id
        side1Form = NHSaleSideForm(prefix='side1')
        side2Form = NHSaleSideForm(prefix='side2')
        invoice1Form = InvoiceForm(prefix='invoice1')
        payment1Forms = PaymentFormset(prefix='payments1')
        invoice2Form = InvoiceForm(prefix='invoice2')
        payment2Forms = PaymentFormset(prefix='payments2')
        
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
            amount, precentage = (updateForm.cleaned_data['amount'],
                                  updateForm.cleaned_data['precentage'])
            pricelist_types = updateForm.cleaned_data['all_pricelists'] and Pricelist.objects.all() or [updateForm.cleaned_data['pricelisttype']]
            houses = [k.replace('house-','') for k in request.POST if k.startswith('house-')]
            for id in houses:
                h = House.objects.get(pk=id)
                for type in pricelist_types:
                    f = h.versions.filter(type=type)
                    if f.count() == 0:
                        continue
                    price = f.latest().price
                    new = HouseVersion(house=h, type=type)
                    if amount:
                        new.price = price + amount
                    elif precentage:
                        new.price = price * (100 + amount) / 100
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
def projectcommission_edit(request, project_id):
    p = Project.objects.get(pk=project_id)
    if request.method == 'POST':
        form = ProjectCommissionForm(request.POST, request.FILES, instance=p.commissions)
        if request.FILES.has_key('agreement'):
            form.instance.agreement = request.FILES['agreement']
        if form.is_valid():
            form.save()
    else:
        form = ProjectCommissionForm(instance = p.commissions)
        
    return render_to_response('Management/object_edit.html', 
                              { 'form':form },
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
            form.save(type_id)
            if request.POST.has_key('addanother'):
                return HttpResponseRedirect('type%s' % type_id)
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
def employee_archive(request):
    return render_to_response('Management/employee_archive.html', 
                              { 'employee_list': Employee.objects.archive()},
                              context_instance=RequestContext(request)) 
@login_required
def employee_list(request):
    return render_to_response('Management/employee_list.html', 
                              { 'employee_list': Employee.objects.active(),
                               'nhemployee_list': NHEmployee.objects.active()},
                              context_instance=RequestContext(request)) 

@permission_required('Management.add_loan')
def employee_loans(request, employee_id, model):
    return render_to_response('Management/employee_loans.html', 
                              { 'employee': model.objects.get(pk=employee_id)},
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
    l = [EmployeeBase.objects.get(pk=e.id) for e in Project.objects.get(pk=project_id).employees.all()]
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
                y,m = (demand.year, demand.month)
                sp = SalePre(sale = form.instance, date=date.today(),
                             employee_pay = date(m+1==13 and y+1 or y,m+1==13 and 1 or m, 1))
                sp.save()
                next = '/salepre/%s' % sp.id 
            demand.calc_sales_commission()
            for employee in project.employees.all():
                if not employee.work_end:
                    continue
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
    demand = Demand.objects.get(project__id = project_id, year = year, month = month)
    if demand.get_sales().count() == 0:
        return render_to_response('Management/error.html', 
                                  {'error':u'לדרישה שנבחרה אין מכירות'},
                                  context_instance=RequestContext(request))
    filename = settings.MEDIA_ROOT + 'temp/' + datetime.now().strftime('%Y%m%d%H%M%S') + '.pdf'
    
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    
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