from django.conf.urls.defaults import *
from Management.models import *
from django.template import RequestContext
import Management.forms
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^NiceHouse/', include('NiceHouse.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT,
         'show_indexes': True}),)

urlpatterns += patterns('Management.views',
    (r'^$', 'index'),
    (r'^locate_house$', 'locate_house'),
    
    (r'^contacts/$', 'limited_object_list',
     {'queryset' : Contact.objects.all(), 'template_name' : 'Management/contact_list.html', 'context_processors':[RequestContext]}),
    (r'^contact/add$', 'limited_create_object',
     {'form_class' : Management.forms.ContactForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '.'}),
    (r'^contact/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.ContactForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^contact/(?P<id>\d+)/del$', 'contact_delete'),
    (r'^projects/$', 'project_list'),
    (r'^projects/archive$', 'limited_object_list',
     {'queryset':Project.objects.archive(), 'template_name':'Management/project_archive.html', 'context_processors':[RequestContext]}),
    (r'^projects/(?P<obj_id>\d+)/addreminder$', 'obj_add_reminder',
     {'model':Project}),
    (r'^projects/(?P<obj_id>\d+)/reminders$', 'obj_reminders',
     {'model':Project}),
    (r'^projects/(?P<obj_id>\d+)/attachment/add$', 'obj_add_attachment',
     {'model':Project}),
    (r'^projects/(?P<obj_id>\d+)/attachments$', 'obj_attachments',
     {'model':Project}),
    (r'^projects/(?P<project_id>\d+)/addcontact$', 'project_contact'),
    (r'^projects/(?P<project_id>\d+)/contact/(?P<id>\d+)/remove$', 'project_removecontact'),
    (r'^projects/(?P<project_id>\d+)/contact/(?P<id>\d+)/delete$', 'project_deletecontact'),
    (r'^projects/(?P<project_id>\d+)/demandcontact$', 'project_contact', {'demand':True}),
    (r'^projects/(?P<project_id>\d+)/paymentcontact$', 'project_contact', {'payment':True}),
    (r'^projects/\d+/contacts/(?P<id>\d+)/del$', 'contact_delete'),
    (r'^projects/(?P<id>\d+)/$', 'project_edit'),
    (r'^projectcommission/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.ProjectCommissionForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^projects/add/$', 'project_add'),
    (r'^projects/end/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.ProjectEndForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^projects/(?P<project_id>\d+)/buildings$', 'project_buildings'),
    (r'^projects/(?P<project_id>\d+)/buildings/add$', 'building_add'),
    (r'^buildings/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.BuildingForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^buildings/(?P<object_id>\d+)/clients/$', 'building_clients'),
    (r'^buildings/(?P<object_id>\d+)/clients/pdf$', 'building_clients_pdf'),
    (r'^buildings/(?P<building_id>\d+)/addparking$', 'building_addparking'),
    (r'^buildings/(?P<building_id>\d+)/addstorage$', 'building_addstorage'),
    (r'^buildings/(?P<object_id>\d+)/pricelist/type(?P<type_id>\d+)$', 'building_pricelist'),
    (r'^buildings/(?P<object_id>\d+)/pricelist/type(?P<type_id>\d+)/pdf$', 'building_pricelist_pdf'),
    (r'^buildings/(?P<building_id>\d+)/addhouse/type(?P<type_id>\d+)$', 'building_addhouse'),
    (r'^buildings/\d+/house/(?P<id>\d+)/type(?P<type_id>\d+)$', 'house_edit'),
    (r'^buildings/(?P<building_id>\d+)/del$', 'building_delete'),
    (r'^projects/(?P<project_id>\d+)/(?P<commission>\w+)/$', 'project_commission_add'),
    (r'^projects/(?P<project_id>\d+)/(?P<commission>\w+)/del$', 'project_commission_del'),

    (r'^projects/(?P<id>\d+)/addinvoice$', 'project_invoice_add'),
    (r'^projects/(?P<id>\d+)/addpayment$', 'project_payment_add'),
    
    (r'^projects/(?P<project_id>\d+)/demands/unpaid$', 'project_demands', 
     {'func':'demands_unpaid', 'template_name' : 'Management/project_demands_unpaid.html'}),
    (r'^projects/(?P<project_id>\d+)/demands/noinvoice$', 'project_demands', 
     {'func':'demands_noinvoice', 'template_name' : 'Management/project_demands_noinvoice.html'}),
    (r'^projects/(?P<project_id>\d+)/demands/nopayment$', 'project_demands', 
     {'func':'demands_nopayment', 'template_name' : 'Management/project_demands_nopayment.html'}),
    (r'^projects/(?P<project_id>\d+)/demands/mispaid$', 'project_demands', 
     {'func':'demands_mispaid', 'template_name' : 'Management/project_demands_mispaid.html'}),
    (r'^demandsall$', 'demands_all'),
    
    (r'^projectsprofit$', 'projects_profit'),
    
    (r'^buildings/add$', 'building_add'),
     
    (r'^parkings/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.ParkingForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^storages/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.StorageForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
        
    (r'^employees/(?P<obj_id>\d+)/attachment/add$', 'obj_add_attachment',
     {'model':Employee}),
    (r'^employees/(?P<obj_id>\d+)/attachments$', 'obj_attachments',
     {'model':Employee}),
    (r'^employees/(?P<obj_id>\d+)/addreminder$', 'obj_add_reminder',
     {'model':Employee}),
    (r'^employees/(?P<obj_id>\d+)/reminders$', 'obj_reminders',
     {'model': Employee}),
    (r'^employees/(?P<object_id>\d+)/loans$', 'limited_object_detail',
     {'queryset':Employee.objects.all(), 'template_name':'Management/employee_loans.html', 'template_object_name':'employee',
      'context_processors':[RequestContext]}),
    (r'^employees/(?P<employee_id>\d+)/addloan$', 'employee_addloan'),
    (r'^employees/(?P<employee_id>\d+)/loanpay$', 'employee_loanpay'),
    (r'^employees/(?P<employee_id>\d+)/(?P<commission>\w+)/project/(?P<project_id>\d+)$', 'employee_commission_add'),
    (r'^employees/(?P<employee_id>\d+)/(?P<commission>\w+)/project/(?P<project_id>\d+)/del$', 'employee_commission_del'),    
    (r'^employees/(?P<employee_id>\d+)/addproject$', 'employee_project_add'),
    (r'^employees/(?P<employee_id>\d+)/removeproject/(?P<project_id>\d+)$', 'employee_project_remove'),
    (r'^employees/$', 'limited_object_list',
     {'template_name':'Management/employee_list.html', 'queryset':Employee.objects.active(), 'template_object_name':'employee',
      'extra_context':{'nhemployee_list':NHEmployee.objects.active()}, 'context_processors':[RequestContext]}),
    (r'^employees/pdf$', 'employee_list_pdf'),
    (r'^employees/archive$', 'limited_object_list',
     {'queryset':Employee.objects.archive(), 'template_name':'Management/employee_archive.html', 'template_object_name':'employee',
      'extra_context':{'nhemployee_list':NHEmployee.objects.archive()}, 'context_processors':[RequestContext]}),
    (r'^employees/add/$', 'limited_create_object',
     {'form_class' : Management.forms.EmployeeForm, 'post_save_redirect' : '/employees/%(id)s'}),
    (r'^employees/(?P<object_id>\d+)/$', 'limited_update_object',
     {'form_class' : Management.forms.EmployeeForm, 'post_save_redirect' : '/employees/%(id)s'}),
    (r'^employees/end/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.EmployeeEndForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^employees/(?P<id>\d+)/employmentterms$', 'employee_employmentterms',
     {'model':EmployeeBase}),
    (r'^employees/(?P<id>\d+)/account$', 'employee_account',
     {'model':EmployeeBase}),
     
     (r'^epcommission/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : EPCommission, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),

     (r'^nhemployees/(?P<obj_id>\d+)/attachment/add$', 'obj_add_attachment',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<obj_id>\d+)/attachments$', 'obj_attachments',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<obj_id>\d+)/addreminder$', 'obj_add_reminder',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<obj_id>\d+)/reminders$', 'obj_reminders',
     {'model': EmployeeBase}),
    (r'^nhemployees/(?P<object_id>\d+)/loans$', 'limited_object_detail',
     {'queryset':NHEmployee.objects.all(), 'template_name':'Management/employee_loans.html', 'template_object_name':'employee',
      'context_processors':[RequestContext]}),
    (r'^nhemployees/(?P<employee_id>\d+)/addloan$', 'nhemployee_addloan'),
    (r'^nhemployees/(?P<employee_id>\d+)/loanpay$', 'nhemployee_loanpay'),
    (r'^nhemployees/add/$', 'limited_create_object',
     {'form_class' : Management.forms.NHEmployeeForm, 'post_save_redirect' : '/nhemployees/%(id)s'}),
    (r'^nhemployees/(?P<object_id>\d+)/$', 'limited_update_object',
     {'form_class' : Management.forms.NHEmployeeForm, 'post_save_redirect' : '/nhemployees/%(id)s'}),
    (r'^nhemployees/end/(?P<id>\d+)/$', 'limited_update_object',
     {'form_class' : Management.forms.EmployeeEndForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^nhemployees/(?P<id>\d+)/employmentterms$', 'employee_employmentterms',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<id>\d+)/account$', 'employee_account',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<employee_id>\d+)/nhcb$', 'nhemployee_nhcb'),
    (r'^nhemployees/(?P<employee_id>\d+)/nhcbi$', 'nhemployee_nhcbi'),
    (r'^nhemployees/(?P<employee_id>\d+)/nhcb/del$', 'nhemployee_commission_del',
     {'attr':'nhcbase'}),
    (r'^nhemployees/(?P<employee_id>\d+)/nhcbi/del$', 'nhemployee_commission_del',
     {'attr':'nhcbranchincome'}),
     
    (r'^reminder/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.ReminderForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^reminder/(?P<id>\d+)/del$', 'reminder_del'),
    (r'^reminder/(?P<id>\d+)/do$', 'reminder_do'),
    (r'^attachments$', 'limited_object_list',
     {'queryset':Attachment.objects.all(), 'template_name':'Management/attachment_list.html', 'context_processors':[RequestContext]}),
    (r'^attachment/add$', 'attachment_add'),
    (r'^attachment/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.AttachmentForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^attachment/(?P<id>\d+)/del$', 'attachment_delete'),
    (r'^tasks/$', 'task_list'),
    (r'^task/add$', 'task_add'),
    (r'^task/(?P<object_id>\d+)/del$', 'limited_delete_object',
     {'model':Task, 'post_delete_redirect':'/tasks'}),
    (r'^task/(?P<id>\d+)/do$', 'task_do'),
    (r'^links/$', 'limited_object_list',
     {'queryset': Link.objects.all()}),
    (r'^link/add$', 'limited_create_object',
     {'model' : Management.models.Link, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^link/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.Link, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^link/(?P<object_id>\d+)/del$', 'limited_delete_object',
     {'model':Link, 'post_delete_redirect':'/links'}),
    (r'^cars/$', 'limited_object_list',
     {'queryset': Car.objects.all()}),
    (r'^car/add$', 'limited_create_object',
     {'model' : Management.models.Car, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^car/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.Car, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^car/(?P<object_id>\d+)/del$', 'limited_delete_object',
     {'model':Car, 'post_delete_redirect':'/cars'}),
    
    (r'^nhbranch/add$', 'limited_create_object',
     {'model' : Management.models.NHBranch, 'template_name' : 'Management/nhbranch_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^nhbranch/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.NHBranch, 'template_name' : 'Management/nhbranch_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^nhbranch/(?P<nhbranch_id>\d+)/sales/$', 'nhmonth_sales'),
    (r'^nhmonth/(?P<id>\d+)/close$', 'nhmonth_close'),
    (r'^nhseasonincome/$', 'nh_season_income'),
    
    (r'^seasonincome/$', 'season_income'),
    
    (r'^projects/(?P<project_id>\d+)/signups/$', 'signup_list'),
    (r'^projects/(?P<project_id>\d+)/signups/add$', 'signup_edit'),
    (r'^signups/(?P<id>\d+)/cancel$', 'signup_cancel'),
    (r'^signups/(?P<id>\d+)$', 'signup_edit'),
    
    (r'^sale$', 'sale_add'),
    (r'^sale/(?P<id>\d+)$', 'sale_edit'),
    (r'^sale/(?P<sale_id>\d+)/commission$', 'salecommissiondetail_edit'),
    
    (r'^demands/(?P<id>\d+)/zero$', 'demand_zero'),
    (r'^demands/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.DemandForm, 'template_name' : 'Management/demand_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^demands/(?P<obj_id>\d+)/reminders$', 'obj_reminders',
     {'model': Demand}),
    (r'^demands/(?P<obj_id>\d+)/addreminder$', 'obj_add_reminder',
     {'model':Demand}),
    (r'^demands/(?P<id>\d+)/close$', 'demand_close'),
    (r'^demandsales/$', 'demand_sale_list'),
    
    (r'^demands/$', 'demand_list'),
    (r'^demands/(?P<id>\d+)/calc$', 'demand_calc'),
    (r'^demandsold/$', 'demand_old_list'),
    (r'^demandseason/$', 'demand_season_list'),
    (r'^demandfollowup/$', 'demand_followup_list'),
    (r'^demands/closeall$', 'demand_closeall'),
    (r'^demands/sendall$', 'demands_send'),
    (r'^demands/(?P<demand_id>\d+)/sale/add$', 'sale_add'),
    (r'^demands/\d+/sale/(?P<id>\d+)/del$', 'demand_sale_del'),
    (r'^demands/\d+/sale/(?P<id>\d+)/reject$', 'demand_sale_reject'),
    (r'^demands/(?P<id>\d+)/invoice/add$', 'demand_invoice_add'),
    (r'^demands/(?P<id>\d+)/payment/add$', 'demand_payment_add'),
    (r'^demands/(?P<id>\d+)/close$', 'demand_close'),
    (r'^demands/(?P<object_id>\d+)/remarks$', 'limited_update_object',
     {'form_class' : Management.forms.DemandRemarksForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : 'remarks',
      'permission':'Management.demand_remarks'}),
    (r'^demands/(?P<object_id>\d+)/salecount$', 'limited_update_object',
     {'form_class' : Management.forms.DemandSaleCountForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : 'salecount',
      'permission':'Management.demand_sale_count'}),
    (r'^demands/(?P<object_id>\d+)/adddiff$', 'demand_adddiff'),
    (r'^demands/(?P<object_id>\d+)/adddiffadjust$', 'demand_adddiff_adjust'),
    (r'^demanddiff/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.DemandDiff, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^demanddiff/(?P<object_id>\d+)/del$', 'demanddiff_del'),
          
    (r'^demandinvoices/$', 'demand_invoice_list'),
    (r'^demandpayments/$', 'demand_payment_list'),

    (r'^salaryexpenses/$', 'salary_expenses_list'),
    (r'^salaryexpenses/(?P<id>)\d+/approve$', 'salary_expenses_approve'),
    (r'^salaryexpenses/add$', 'limited_create_object',
     {'model' : Management.models.SalaryExpenses, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^salaryexpenses/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.SalaryExpenses, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
     (r'^salary/(?P<salary_id>\d+)/expenses$', 'employee_salary_expenses'),
     
    (r'^employeesalaries/$', 'employee_salary_list'),
    (r'^employeesalaryseason/$', 'employeesalary_season_list'),
    (r'^employeesalaries/(?P<year>\d+)/(?P<month>\d+)/pdf$', 'employee_salary_pdf'),
    (r'^employeesalaries/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.EmployeeSalary, 'template_name' : 'Management/employee_salary_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^employeesalaries/(?P<id>\d+)/calc$', 'employee_salary_calc',
     {'model':EmployeeSalary}),
    (r'^employeesalaries/(?P<object_id>\d+)/details$', 'limited_object_detail',
     {'queryset':EmployeeSalary.objects.all(),
      'template_name':'Management/employee_commission_details.html',
      'template_object_name':'salary',
      'context_processors':[RequestContext]}),
    (r'^employeesalaries/(?P<object_id>\d+)/checkdetails$', 'limited_object_detail',
     {'queryset':EmployeeSalary.objects.all(),
      'template_name':'Management/employee_salary_check_details.html',
      'template_object_name':'salary',
      'context_processors':[RequestContext]}),
    (r'^employeesalaries/(?P<object_id>\d+)/totaldetails$', 'limited_object_detail',
     {'queryset':EmployeeSalary.objects.all(), 'template_name':'Management/employee_salary_total_details.html', 
      'template_object_name':'salary', 'context_processors':[RequestContext]}),
    (r'^employeesalaries/(?P<id>\d+)/approve$', 'employee_salary_approve'),
    (r'^employee/(?P<id>\d+)/sales/(?P<year>\d+)/(?P<month>\d+)$', 'employee_sales'),
    
    (r'^employee/remarks/(?P<year>\d+)/(?P<month>\d+)$', 'employee_remarks'),
    (r'^employee/refund/(?P<year>\d+)/(?P<month>\d+)$', 'employee_refund'),
    
    (r'^nhemployeesalaries/$', 'nhemployee_salary_list'),
    (r'^nhemployeesalaries/(?P<nhbranch_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/pdf$', 'nhemployee_salary_pdf'),
    (r'^nhemployeesalaries/(?P<nhbranch_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/send$', 'nhemployee_salary_send'),
    (r'^nhemployeesalaries/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.NHEmployeeSalary, 'template_name' : 'Management/nhemployee_salary_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^nhemployeesalaries/(?P<id>\d+)/calc$', 'employee_salary_calc',
     {'model':NHEmployeeSalary}),
    (r'^nhemployeesalaries/(?P<object_id>\d+)/details$', 'limited_object_detail',
     {'queryset':NHEmployeeSalary.objects.all(), 'template_name':'Management/nhemployee_commission_details.html',
      'template_object_name':'salary', 'context_processors':[RequestContext]}),
    (r'^nhemployeesalaries/(?P<object_id>\d+)/checkdetails$', 'limited_object_detail',
     {'queryset':NHEmployeeSalary.objects.all(), 'template_name':'Management/employee_salary_check_details.html.html',
      'template_object_name':'salary', 'context_processors':[RequestContext]}),
    (r'^nhemployeesalaries/(?P<object_id>\d+)/totaldetails$', 'limited_object_detail',
     {'queryset':NHEmployeeSalary.objects.all(), 'template_name':'Management/employee_salary_total_details.html',
      'template_object_name':'salary', 'context_processors':[RequestContext]}),
    (r'^nhemployeesalaries/(?P<id>\d+)/approve$', 'employee_salary_approve'),
    (r'^nhemployee/(?P<id>\d+)/sales/(?P<year>\d+)/(?P<month>\d+)$', 'nhemployee_sales'),
    
    (r'^nhemployee/remarks/(?P<year>\d+)/(?P<month>\d+)$', 'nhemployee_remarks'),
    (r'^nhemployee/refund/(?P<year>\d+)/(?P<month>\d+)$', 'nhemployee_refund'),
        
    (r'^payments/add$', 'payment_add'),
    (r'^payments/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.PaymentForm, 'template_name' : 'Management/payment_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^payments/(?P<id>\d+)/del$', 'payment_del'),
    
    (r'^invoices/add$', 'invoice_add'),      
    (r'^invoices/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.InvoiceForm, 'template_name' : 'Management/invoice_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^invoices/(?P<id>\d+)/del$', 'invoice_del'),    
    
    (r'^checks(/(?P<year>\d{4})/(?P<month>\d{2}))?$', 'check_list'),
    (r'^checks/add$', 'check_add'),
    (r'^checks/(?P<id>\d+)$', 'check_edit'),
    (r'^checks/(?P<id>\d+)/del$', 'limited_delete_object',
     {'model':Check, 'post_delete_redirect':'/checks'}),
        
    (r'^advancepayments$', 'limited_object_list',
     {'queryset': AdvancePayment.objects.filter(is_paid=None)}),
    (r'^advancepayments/add$', 'limited_create_object',
     {'form_class' : Management.forms.AdvancePaymentForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^advancepayments/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.AdvancePaymentForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^advancepayments/(?P<id>\d+)/toloan$', 'advance_payment_toloan'),
    (r'^advancepayments/(?P<id>\d+)/del$', 'limited_delete_object',
     {'model':AdvancePayment, 'post_delete_redirect':'/advancepayments'}),
    
    (r'^loans/$', 'limited_object_list',
     {'queryset': Loan.objects.all()}),
    (r'^loans/add$', 'limited_create_object',
     {'form_class' : Management.forms.LoanForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^loans/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.LoanForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^loans/(?P<id>\d+)/del$', 'limited_delete_object',
     {'model':Loan, 'post_delete_redirect':'/loans'}),
    
    (r'^lawyers/$', 'limited_object_list',
     {'queryset': Lawyer.objects.all()}),
    (r'^lawyers/add$', 'limited_create_object',
     {'model' : Lawyer, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^lawyers/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Lawyer, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^lawyers/(?P<id>\d+)/del$', 'limited_delete_object',
     {'model':Lawyer, 'post_delete_redirect':'/lawyers'}),
    
    (r'^employeechecks(/(?P<year>\d{4})/(?P<month>\d{2}))?$', 'employeecheck_list'),
    (r'^employeechecks/add$', 'limited_create_object',
     {'form_class' : Management.forms.EmployeeCheckForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^employeechecks/(?P<id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.EmployeeCheckForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^employeechecks/(?P<id>\d+)/del$', 'limited_delete_object',
     {'model':EmployeeCheck, 'post_delete_redirect':'/employeechecks'}),
    
    (r'^reports/$', 'limited_direct_to_template',
     {'template': 'Management/reports.html',
      'extra_context': {'form':Management.forms.DemandReportForm, 'form2':Management.forms.DemandReportForm(prefix='2')}}),
    (r'^reports/project_month/(?P<project_id>\d+)/(?P<year>\d+)/(?P<month>\d+)$', 'report_project_month'),
    (r'^reports/projects_month/(?P<year>\d+)/(?P<month>\d+)$', 'report_projects_month'),
    (r'^reports/project_season/(?P<project_id>\d+)/(?P<from_year>\d+)/(?P<from_month>\d+)/(?P<to_year>\d+)/(?P<to_month>\d+)$', 'report_project_season'),
    (r'^reports/employeesalary_season/(?P<employee_id>\d+)/(?P<from_year>\d+)/(?P<from_month>\d+)/(?P<to_year>\d+)/(?P<to_month>\d+)$', 'report_employeesalary_season'),
    
    (r'^madadbi/$', 'limited_object_list',
     {'queryset':MadadBI.objects.all(), 'template_name':'Management/madadbi_list.html', 'context_processors':[RequestContext]}),
    (r'^madadbi/add$', 'limited_create_object',
     {'form_class' : Management.forms.MadadBIForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^madadbi/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.MadadBIForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^madadbi/(?P<id>\d+)/del$', 'limited_delete_object',
     {'model':MadadBI, 'post_delete_redirect':'/madadbi'}),
    
    (r'^madadcp/$', 'limited_object_list',
     {'queryset':MadadCP.objects.all(), 'template_name':'Management/madadcp_list.html', 'context_processors':[RequestContext]}),
    (r'^madadcp/add$', 'limited_create_object',
     {'form_class' : Management.forms.MadadCPForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^madadcp/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.MadadCPForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^madadcp/(?P<id>\d+)/del$', 'limited_delete_object',
     {'model':MadadCP, 'post_delete_redirect':'/madadcp'}),
    
    (r'^tax/$', 'limited_object_list',
     {'queryset':Tax.objects.all(), 'template_name':'Management/tax_list.html', 'context_processors':[RequestContext]}),
    (r'^tax/add$', 'limited_create_object',
     {'model' : Management.models.Tax, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^tax/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.Tax, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^tax/(?P<id>\d+)/del$', 'limited_delete_object',
     {'model':Tax, 'post_delete_redirect':'/tax'}),
    
    (r'^salepricemod/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.SalePriceModForm, 'template_name' : 'Management/sale_mod_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^salehousemod/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.SaleHouseModForm, 'template_name' : 'Management/sale_mod_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^salepre/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.SalePreForm, 'template_name' : 'Management/sale_mod_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^salereject/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.SaleRejectForm, 'template_name' : 'Management/sale_mod_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^salecancel/(?P<object_id>\d+)$', 'limited_update_object',
     {'model' : Management.models.SaleCancel, 'template_name' : 'Management/sale_mod_edit.html', 'post_save_redirect' : '%(id)s'}),
      
    (r'^nhbranch/(?P<branch_id>\d+)/nhsale/add$', 'nhsale_add'),
    (r'^nhsale/(?P<object_id>\d+)/$', 'nhsale_edit'),
    (r'^nhsale/(?P<object_id>\d+)/edit$', 'limited_update_object',
     {'form_class' : Management.forms.NHSaleForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '../%(id)s'}),
    (r'^nhsaleside/(?P<object_id>\d+)$', 'limited_update_object',
     {'form_class' : Management.forms.NHSaleSideForm, 'template_name' : 'Management/object_edit.html', 'post_save_redirect' : '%(id)s'}),
    (r'^nhsaleside/(?P<object_id>\d+)/payment/add$', 'nhsaleside_payment_add'),
    (r'^nhsaleside/(?P<object_id>\d+)/invoice/add$', 'nhsaleside_invoice_add'),
    
    (r'^xml/buildings/(?P<project_id>\d+)$', 'json_buildings'),
    (r'^xml/employees/(?P<project_id>\d+)$', 'json_employees'),
    (r'^xml/houses/(?P<building_id>\d+)$', 'json_houses'),
    (r'^xml/house/(?P<house_id>\d+)$', 'json_house'),
    (r'^json/links$', 'json_links'),
    (r'^demand_details/(?P<project>\d+)/(?P<year>\d+)/(?P<month>\d+)$', 'demand_details'),
    (r'^invoice_details/(?P<project>\d+)/(?P<year>\d+)/(?P<month>\d+)$', 'invoice_details'),
    (r'^payment_details/(?P<project>\d+)/(?P<year>\d+)/(?P<month>\d+)$', 'payment_details'),
    (r'^house_details/(?P<id>\d+)$', 'house_details'),
    (r'^signup_details/(?P<house_id>\d+)$', 'signup_details'),
    (r'^demand_sales/(?P<project_id>\d+)/(?P<year>\d+)/(?P<month>\d+)$', 'demand_sales'),
)
