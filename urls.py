from django.conf.urls.defaults import *
from Management.models import *
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

    (r'^$', 'Management.views.index'),
    (r'^locate_house$', 'Management.views.locate_house'),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/password_change/$', 'django.contrib.auth.views.password_change'),
    
    (r'^contacts/$', 'Management.views.contact_list'),
    (r'^contact/add$', 'Management.views.limited_create_object',
         {'form_class' : Management.forms.ContactForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'add_contact',
          'post_save_redirect' : '.'}),
    (r'^contact/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.ContactForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_contact',
          'post_save_redirect' : '%(id)s'}),
    (r'^contact/(?P<id>\d+)/del$', 'Management.views.contact_delete'),
    (r'^projects/$', 'Management.views.project_list'),
    (r'^projects/archive$', 'Management.views.project_archive'),
    (r'^projects/(?P<obj_id>\d+)/addreminder$', 'Management.views.obj_add_reminder',
     {'model':Project}),
    (r'^projects/\d+/reminder/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.ReminderForm,
      'template_name' : 'Management/object_edit.html',
      'permission':'change_reminder',
      'post_save_redirect' : '../reminders'}),
    (r'^projects/(?P<obj_id>\d+)/reminders$', 'Management.views.obj_reminders',
     {'model':Project}),
    (r'^projects/(?P<obj_id>\d+)/attachment/add$', 'Management.views.obj_add_attachment',
     {'model':Project}),
    (r'^projects/(?P<obj_id>\d+)/attachments$', 'Management.views.obj_attachments',
     {'model':Project}),
    (r'^projects/(?P<project_id>\d+)/addcontact$', 'Management.views.project_contact'),
    (r'^projects/(?P<project_id>\d+)/contact/(?P<id>\d+)/remove$', 'Management.views.project_removecontact'),
    (r'^projects/(?P<project_id>\d+)/contact/(?P<id>\d+)/delete$', 'Management.views.project_deletecontact'),
    (r'^projects/(?P<project_id>\d+)/demandcontact$', 'Management.views.project_contact', {'demand':True}),
    (r'^projects/(?P<project_id>\d+)/paymentcontact$', 'Management.views.project_contact', {'payment':True}),
    (r'^projects/\d+/contacts/(?P<id>\d+)/del$', 'Management.views.contact_delete'),
    (r'^projects/(?P<id>\d+)/$', 'Management.views.project_edit'),
    (r'^projects/(?P<project_id>\d+)/commissions$', 'Management.views.projectcommission_edit'),
    (r'^projects/add/$', 'Management.views.project_add'),
    (r'^projects/end/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.ProjectEndForm,
      'template_name' : 'Management/object_edit.html',
      'permission':'change_project',
      'post_save_redirect' : '%(id)s'}),
    (r'^projects/(?P<project_id>\d+)/buildings$', 'Management.views.project_buildings'),
    (r'^projects/(?P<project_id>\d+)/buildings/add$', 'Management.views.building_add'),
    (r'^buildings/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.BuildingForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_building',
          'post_save_redirect' : '%(id)s'}),
    (r'^buildings/(?P<building_id>\d+)/addparking$', 'Management.views.building_addparking'),
    (r'^buildings/(?P<building_id>\d+)/addstorage$', 'Management.views.building_addstorage'),
    (r'^buildings/(?P<object_id>\d+)/pricelist/type(?P<type_id>\d+)$', 'Management.views.building_pricelist'),
    (r'^buildings/(?P<building_id>\d+)/addhouse/type(?P<type_id>\d+)$', 'Management.views.building_addhouse'),
    (r'^buildings/\d+/house/(?P<id>\d+)/type(?P<type_id>\d+)$', 'Management.views.house_edit'),
    (r'^buildings/(?P<building_id>\d+)/del$', 'Management.views.building_delete'),
    (r'^projects/(?P<project_id>\d+)/cvp/$', 'Management.views.project_cvp'),
    (r'^projects/(?P<project_id>\d+)/cvpf/$', 'Management.views.project_cvpf'),
    (r'^projects/(?P<project_id>\d+)/cz/$', 'Management.views.project_cz'),
    (r'^projects/(?P<project_id>\d+)/bdsp/$', 'Management.views.project_bdsp'),
    (r'^projects/(?P<project_id>\d+)/cvp/del$', 'Management.views.project_commission_del', {'attribute':'c_var_precentage'}),
    (r'^projects/(?P<project_id>\d+)/cvpf/del$', 'Management.views.project_commission_del', {'attribute':'c_var_precentage_fixed'}),
    (r'^projects/(?P<project_id>\d+)/cz/del$', 'Management.views.project_commission_del', {'attribute':'c_zilber'}),
    (r'^projects/(?P<project_id>\d+)/bdsp/del$', 'Management.views.project_commission_del', {'attribute':'b_discount_save_precentage'}),

    (r'^projects/(?P<id>\d+)/addinvoice$', 'Management.views.project_invoice_add'),
    (r'^projects/(?P<id>\d+)/addpayment$', 'Management.views.project_payment_add'),
    
    (r'^projects/(?P<project_id>\d+)/demands/unpaid$', 'Management.views.project_demands', 
     {'func':'demands_unpaid', 'template_name' : 'Management/project_demands_unpaid.html'}),
    (r'^projects/(?P<project_id>\d+)/demands/noinvoice$', 'Management.views.project_demands', 
     {'func':'demands_noinvoice', 'template_name' : 'Management/project_demands_noinvoice.html'}),
    (r'^projects/(?P<project_id>\d+)/demands/nopayment$', 'Management.views.project_demands', 
     {'func':'demands_nopayment', 'template_name' : 'Management/project_demands_nopayment.html'}),
    (r'^projects/(?P<project_id>\d+)/demands/mispaid$', 'Management.views.project_demands', 
     {'func':'demands_mispaid', 'template_name' : 'Management/project_demands_mispaid.html'}),
    (r'^demandsall$', 'Management.views.demands_all'),
    
    (r'^buildings/add$', 'Management.views.building_add'),
     
    (r'^parkings/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.ParkingForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_parking',
          'post_save_redirect' : '%(id)s'}),
    (r'^storages/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.StorageForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_storage',
          'post_save_redirect' : '%(id)s'}),
        
    (r'^employees/(?P<obj_id>\d+)/attachment/add$', 'Management.views.obj_add_attachment',
     {'model':Employee}),
    (r'^employees/(?P<obj_id>\d+)/attachments$', 'Management.views.obj_attachments',
     {'model':Employee}),
    (r'^employees/(?P<obj_id>\d+)/addreminder$', 'Management.views.obj_add_reminder',
     {'model':Employee}),
    (r'^employees/\d+/reminder/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.ReminderForm,
      'template_name' : 'Management/reminder_edit.html',
      'permission': 'change_reminder',
      'post_save_redirect' : '../reminders'}),
    (r'^employees/(?P<obj_id>\d+)/reminders$', 'Management.views.obj_reminders',
     {'model': Employee}),
    (r'^employees/(?P<employee_id>\d+)/loans$', 'Management.views.employee_loans',
     {'model':Employee}),
    (r'^employees/(?P<employee_id>\d+)/addloan$', 'Management.views.employee_addloan'),
    (r'^employees/(?P<employee_id>\d+)/loanpay$', 'Management.views.employee_loanpay'),
    (r'^employees/(?P<employee_id>\d+)/cv/project/(?P<project_id>\d+)$', 'Management.views.employee_cv'),
    (r'^employees/(?P<employee_id>\d+)/cvp/project/(?P<project_id>\d+)$', 'Management.views.employee_cvp'),
    (r'^employees/(?P<employee_id>\d+)/cbp/project/(?P<project_id>\d+)$', 'Management.views.employee_cbp'),
    (r'^employees/(?P<employee_id>\d+)/bsr/project/(?P<project_id>\d+)$', 'Management.views.employee_bsr'),
    (r'^employees/(?P<employee_id>\d+)/bht/project/(?P<project_id>\d+)$', 'Management.views.employee_bht'),
    (r'^employees/(?P<employee_id>\d+)/bds/project/(?P<project_id>\d+)$', 'Management.views.employee_bds'),
    (r'^employees/(?P<employee_id>\d+)/cv/project/(?P<project_id>\d+)/del$', 'Management.views.employee_commission_del', {'attribute':'c_var'}),
    (r'^employees/(?P<employee_id>\d+)/cvp/project/(?P<project_id>\d+)/del$', 'Management.views.employee_commission_del', {'attribute':'c_var_precentage'}),
    (r'^employees/(?P<employee_id>\d+)/cbp/project/(?P<project_id>\d+)/del$', 'Management.views.employee_commission_del', {'attribute':'c_by_price'}),
    (r'^employees/(?P<employee_id>\d+)/bsr/project/(?P<project_id>\d+)/del$', 'Management.views.employee_commission_del', {'attribute':'b_sale_rate'}),
    (r'^employees/(?P<employee_id>\d+)/bht/project/(?P<project_id>\d+)/del$', 'Management.views.employee_commission_del', {'attribute':'b_house_type'}),
    (r'^employees/(?P<employee_id>\d+)/bds/project/(?P<project_id>\d+)/del$', 'Management.views.employee_commission_del', {'attribute':'b_discount_save'}),
    (r'^employees/$', 'Management.views.employee_list'),
    (r'^employees/pdf$', 'Management.views.employee_list_pdf'),
    (r'^employees/archive$', 'Management.views.employee_archive'),
    (r'^employees/add/$', 'Management.views.limited_create_object',
     {'form_class' : Management.forms.EmployeeForm,
      'permission':'add_employee',
      'post_save_redirect' : '/employees/%(id)s'}),
    (r'^employees/(?P<object_id>\d+)/$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.EmployeeForm,
      'permission':'change_employee',
      'post_save_redirect' : '/employees/%(id)s'}),
    (r'^employees/end/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.EmployeeEndForm,
      'template_name' : 'Management/object_edit.html',
      'permission':'change_employee',
      'post_save_redirect' : '%(id)s'}),
    (r'^employees/(?P<id>\d+)/employmentterms$', 'Management.views.employee_employmentterms',
     {'model':EmployeeBase}),
    (r'^employees/(?P<id>\d+)/account$', 'Management.views.employee_account',
     {'model':EmployeeBase}),
 
     (r'^nhemployees/(?P<obj_id>\d+)/attachment/add$', 'Management.views.obj_add_attachment',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<obj_id>\d+)/attachments$', 'Management.views.obj_attachments',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<obj_id>\d+)/addreminder$', 'Management.views.obj_add_reminder',
     {'model':EmployeeBase}),
    (r'^nhemployees/\d+/reminder/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.ReminderForm,
      'template_name' : 'Management/reminder_edit.html',
      'permission': 'change_reminder',
      'post_save_redirect' : '../reminders'}),
    (r'^nhemployees/(?P<obj_id>\d+)/reminders$', 'Management.views.obj_reminders',
     {'model': EmployeeBase}),
    (r'^nhemployees/(?P<employee_id>\d+)/loans$', 'Management.views.employee_loans',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<employee_id>\d+)/addloan$', 'Management.views.nhemployee_addloan'),
    (r'^nhemployees/(?P<employee_id>\d+)/loanpay$', 'Management.views.nhemployee_loanpay'),
    (r'^nhemployees/$', 'Management.views.employee_list'),
    (r'^nhemployees/archive$', 'Management.views.employee_archive'),
    (r'^nhemployees/add/$', 'Management.views.limited_create_object',
     {'form_class' : Management.forms.NHEmployeeForm,
      'permission':'add_employee',
      'post_save_redirect' : '/nhemployees/%(id)s'}),
    (r'^nhemployees/(?P<object_id>\d+)/$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.NHEmployeeForm,
      'permission':'change_employee',
      'post_save_redirect' : '/nhemployees/%(id)s'}),
    (r'^nhemployees/end/(?P<id>\d+)/$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.EmployeeEndForm,
      'template_name' : 'Management/object_edit.html',
      'permission':'change_employee',
      'post_save_redirect' : '%(id)s'}),
    (r'^nhemployees/(?P<id>\d+)/employmentterms$', 'Management.views.employee_employmentterms',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<id>\d+)/account$', 'Management.views.employee_account',
     {'model':EmployeeBase}),
    (r'^nhemployees/(?P<employee_id>\d+)/nhcb$', 'Management.views.nhemployee_nhcb'),
    (r'^nhemployees/(?P<employee_id>\d+)/nhcbi$', 'Management.views.nhemployee_nhcbi'),
    (r'^nhemployees/(?P<employee_id>\d+)/nhcb/del$', 'Management.views.nhemployee_commission_del',
     {'attr':'nhcbase'}),
    (r'^nhemployees/(?P<employee_id>\d+)/nhcbi/del$', 'Management.views.nhemployee_commission_del',
     {'attr':'nhcbranchincome'}),
  
    (r'^reminder/(?P<id>\d+)/del$', 'Management.views.reminder_del'),
    (r'^reminder/(?P<id>\d+)/do$', 'Management.views.reminder_do'),
    (r'^attachments$', 'Management.views.attachment_list'),
    (r'^attachment/add$', 'Management.views.attachment_add'),
    (r'^attachment/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.AttachmentForm,
      'template_name' : 'Management/object_edit.html',
      'permission':'change_attachment',
      'post_save_redirect' : '%(id)s'}),
    (r'^attachment/(?P<id>\d+)/del$', 'Management.views.attachment_delete'),
    (r'^tasks/$', 'Management.views.task_list'),
    (r'^task/add$', 'Management.views.task_add'),
    (r'^task/(?P<id>\d+)/del$', 'Management.views.task_del'),
    (r'^task/(?P<id>\d+)/do$', 'Management.views.task_do'),
    (r'^links/$', 'Management.views.limited_object_list',
         {'queryset': Link.objects.all()}),
    (r'^link/add$', 'Management.views.limited_create_object',
         {'model' : Management.models.Link,
          'template_name' : 'Management/object_edit.html',
          'permission':'add_link',
          'post_save_redirect' : '%(id)s'}),
    (r'^link/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'model' : Management.models.Link,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_link',
          'post_save_redirect' : '%(id)s'}),
    (r'^link/(?P<id>\d+)/del$', 'Management.views.link_del'),
    (r'^cars/$', 'Management.views.limited_object_list',
         {'queryset': Car.objects.all()}),
    (r'^car/add$', 'Management.views.limited_create_object',
         {'model' : Management.models.Car,
          'template_name' : 'Management/object_edit.html',
          'permission':'add_car',
          'post_save_redirect' : '%(id)s'}),
    (r'^car/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'model' : Management.models.Car,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_car',
          'post_save_redirect' : '%(id)s'}),
    (r'^car/(?P<id>\d+)/del$', 'Management.views.car_del'),
    
    (r'^nhbranch/add$', 'Management.views.limited_create_object',
         {'model' : Management.models.NHBranch,
          'template_name' : 'Management/nhbranch_edit.html',
          'permission':'add_nhbranch',
          'post_save_redirect' : '%(id)s'}),
    (r'^nhbranch/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'model' : Management.models.NHBranch,
          'template_name' : 'Management/nhbranch_edit.html',
          'permission':'change_nhbranch',
          'post_save_redirect' : '%(id)s'}),
    (r'^nhbranch/(?P<nhbranch_id>\d+)/sales$', 'Management.views.nhmonth_sales'),
    (r'^nhbranch/(?P<nhbranch_id>\d+)/sales/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.nhmonth_sales'),
    (r'^nhmonth/(?P<id>\d+)/close$', 'Management.views.nhmonth_close'),
    
    (r'^projects/(?P<project_id>\d+)/signups/$', 'Management.views.signup_list'),
    (r'^projects/(?P<project_id>\d+)/signups/add$', 'Management.views.signup_edit'),
    (r'^signups/(?P<id>\d+)/cancel$', 'Management.views.signup_cancel'),
    (r'^signups/(?P<id>\d+)$', 'Management.views.signup_edit'),
    
    (r'^sale$', 'Management.views.sale_add'),
    (r'^sale/(?P<id>\d+)$', 'Management.views.sale_edit'),
    (r'^sale/(?P<sale_id>\d+)/commission$', 'Management.views.salecommissiondetail_edit'),
    
    (r'^demands/(?P<id>\d+)/zero$', 'Management.views.demand_zero'),
    (r'^demands/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.DemandForm,
          'template_name' : 'Management/demand_edit.html',
          'permission':'change_demand',
          'post_save_redirect' : '%(id)s'}),
    (r'^demands/(?P<obj_id>\d+)/reminders$', 'Management.views.obj_reminders',
     {'model': Demand}),
    (r'^demands/(?P<obj_id>\d+)/addreminder$', 'Management.views.obj_add_reminder',
     {'model':Demand}),
    (r'^demands/\d+/reminder/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
     {'form_class' : Management.forms.ReminderForm,
      'template_name' : 'Management/object_edit.html',
      'permission':'change_reminder',
      'post_save_redirect' : '../reminders'}),
    (r'^demands/(?P<id>\d+)/close$', 'Management.views.demand_close'),
    (r'^demands/(?P<id>\d+)/sales$', 'Management.views.demand_sales'),
    
    (r'^demands/$', 'Management.views.demand_list'),
    (r'^demands/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.demand_list'),
    (r'^demands/(?P<id>\d+)/calc$', 'Management.views.demand_calc'),
    (r'^demandsold$', 'Management.views.demand_old_list'),
    (r'^demandsold/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.demand_old_list'),
    (r'^demandseason$', 'Management.views.demand_season_list'),
    (r'^demandseason/(?P<project_id>\d+)/(?P<from_year>\d+)/(?P<from_month>\d+)/(?P<to_year>\d+)/(?P<to_month>\d+)$', 'Management.views.demand_season_list'),
    (r'^demands/closeall$', 'Management.views.demand_closeall'),
    (r'^demands/sendall$', 'Management.views.demands_send'),
    (r'^demands/(?P<demand_id>\d+)/sale/add$', 'Management.views.sale_add'),
    (r'^demands/\d+/sale/(?P<id>\d+)/del$', 'Management.views.demand_sale_del'),
    (r'^demands/\d+/sale/(?P<id>\d+)/reject$', 'Management.views.demand_sale_reject'),
    
    (r'^demands/(?P<id>\d+)/invoice/add$', 'Management.views.demand_invoice_add'),

    (r'^demands/(?P<id>\d+)/payment/add$', 'Management.views.demand_payment_add'),
    
    (r'^demands/(?P<id>\d+)/close$', 'Management.views.demand_close'),
    (r'^demands/(?P<object_id>\d+)/remarks$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.DemandRemarksForm,
          'template_name' : 'Management/demand_remarks_edit.html',
          'permission':'add_demand',
          'post_save_redirect' : 'remarks'}),
          
    (r'^demandinvoices/$', 'Management.views.demand_invoice_list'),
    (r'^demandinvoices/(?P<project_id>\d+)/(?P<from_year>\d+)/(?P<from_month>\d+)/(?P<to_year>\d+)/(?P<to_month>\d+)$', 'Management.views.demand_invoice_list'),
    (r'^demandpayments/$', 'Management.views.demand_payment_list'),

    (r'^employeesalaries/$', 'Management.views.employee_salary_list'),
    (r'^employeesalaries/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.employee_salary_list'),
    (r'^employeesalaries/(?P<year>\d+)/(?P<month>\d+)/pdf$', 'Management.views.employee_salary_pdf'),
    (r'^employeesalaries/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'model' : Management.models.EmployeeSalary,
          'template_name' : 'Management/employee_salary_edit.html',
          'permission':'change_employeesalary',
          'post_save_redirect' : '%(id)s'}),
    (r'^employeesalaries/(?P<id>\d+)/calc$', 'Management.views.employee_salary_calc',
     {'model':EmployeeSalary}),
    (r'^employeesalaries/(?P<id>\d+)/details$', 'Management.views.employee_salary_details'),
    (r'^employeesalaries/(?P<id>\d+)/checkdetails$', 'Management.views.employee_salary_check_details',
     {'model':EmployeeSalary}),
    (r'^employeesalaries/(?P<id>\d+)/totaldetails$', 'Management.views.employee_salary_total_details',
     {'model':EmployeeSalary}),
    (r'^employeesalaries/(?P<id>\d+)/approve$', 'Management.views.employee_salary_approve'),
    (r'^employee/(?P<id>\d+)/sales/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.employee_sales'),
    
    (r'^employee/remarks/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.employee_remarks'),
    (r'^employee/refund/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.employee_refund'),
    
    (r'^nhemployeesalaries/$', 'Management.views.nhemployee_salary_list'),
    (r'^nhemployeesalaries/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.nhemployee_salary_list'),
    (r'^nhemployeesalaries/(?P<nhbranch_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/pdf$', 'Management.views.nhemployee_salary_pdf'),
    (r'^nhemployeesalaries/(?P<nhbranch_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/send$', 'Management.views.nhemployee_salary_send'),
    (r'^nhemployeesalaries/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'model' : Management.models.NHEmployeeSalary,
          'template_name' : 'Management/nhemployee_salary_edit.html',
          'permission':'change_nhemployeesalary',
          'post_save_redirect' : '%(id)s'}),
    (r'^nhemployeesalaries/(?P<id>\d+)/calc$', 'Management.views.employee_salary_calc',
     {'model':NHEmployeeSalary}),
    (r'^nhemployeesalaries/(?P<id>\d+)/details$', 'Management.views.nhemployee_salary_details'),
    (r'^nhemployeesalaries/(?P<id>\d+)/checkdetails$', 'Management.views.employee_salary_check_details',
     {'model':NHEmployeeSalary}),
    (r'^nhemployeesalaries/(?P<id>\d+)/totaldetails$', 'Management.views.employee_salary_total_details',
     {'model':NHEmployeeSalary}),
    (r'^nhemployeesalaries/(?P<id>\d+)/approve$', 'Management.views.employee_salary_approve'),
    (r'^nhemployee/(?P<id>\d+)/sales/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.nhemployee_sales'),
    
    (r'^nhemployee/remarks/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.nhemployee_remarks'),
    (r'^nhemployee/refund/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.nhemployee_refund'),
        
    (r'^payments/add$', 'Management.views.payment_add'),
    (r'^payments/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.PaymentForm,
          'template_name' : 'Management/payment_edit.html',
          'permission':'change_payment',
          'post_save_redirect' : '%(id)s'}),
    (r'^payments/(?P<id>\d+)/del$', 'Management.views.payment_del'),
    
    (r'^invoices/add$', 'Management.views.invoice_add'),      
    (r'^invoices/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.InvoiceForm,
          'template_name' : 'Management/invoice_edit.html',
          'permission':'change_invoice',
          'post_save_redirect' : '%(id)s'}),
    (r'^invoices/(?P<id>\d+)/del$', 'Management.views.invoice_del'),    
    
    (r'^checks(/(?P<year>\d{4})/(?P<month>\d{2}))?$', 'Management.views.check_list'),
    (r'^checks/add$', 'Management.views.check_add'),
    (r'^checks/(?P<id>\d+)$', 'Management.views.check_edit'),
    (r'^checks/(?P<id>\d+)/del$', 'Management.views.check_del'),
    
    (r'^advancepayments$', 'Management.views.limited_object_list',
         {'queryset': AdvancePayment.objects.filter(is_paid=None)}),
    (r'^advancepayments/add$', 'Management.views.limited_create_object',
         {'form_class' : Management.forms.AdvancePaymentForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'add_advancepayment',
          'post_save_redirect' : '%(id)s'}),
    (r'^advancepayments/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.AdvancePaymentForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_advancepayment',          
          'post_save_redirect' : '%(id)s'}),
    (r'^advancepayments/(?P<id>\d+)/toloan$', 'Management.views.advance_payment_toloan'),
    (r'^advancepayments/(?P<id>\d+)/del$', 'Management.views.advance_payment_del'),
    
    (r'^loans$', 'Management.views.limited_object_list',
         {'queryset': Loan.objects.all()}),
    (r'^loans/add$', 'Management.views.limited_create_object',
         {'form_class' : Management.forms.LoanForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'add_loan',          
          'post_save_redirect' : '%(id)s'}),
    (r'^loans/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.LoanForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_loan',          
          'post_save_redirect' : '%(id)s'}),
    (r'^loans/(?P<id>\d+)/del$', 'Management.views.loan_del'),
    
    (r'^employeechecks(/(?P<year>\d{4})/(?P<month>\d{2}))?$', 'Management.views.employeecheck_list'),
    (r'^employeechecks/add$', 'Management.views.limited_create_object',
         {'form_class' : Management.forms.EmployeeCheckForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'add_employeecheck',
          'post_save_redirect' : '%(id)s'}),
    (r'^employeechecks/(?P<id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.EmployeeCheckForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_employeecheck',          
          'post_save_redirect' : '%(id)s'}),
    (r'^employeechecks/(?P<id>\d+)/del$', 'Management.views.employeecheck_del'),
    
    (r'^reports/$', 'django.views.generic.simple.direct_to_template',
     {'template': 'Management/reports.html',
      'extra_context': {'form':Management.forms.DemandReportForm,
                        'form2':Management.forms.DemandReportForm(prefix='2')}}),
    (r'^reports/project_month/(?P<project_id>\d+)/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.report_project_month'),
    (r'^reports/projects_month/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.report_projects_month'),
    (r'^reports/project_season/(?P<project_id>\d+)/(?P<from_year>\d+)/(?P<from_month>\d+)/(?P<to_year>\d+)/(?P<to_month>\d+)$', 'Management.views.report_project_season'),
    
    (r'^madad/$', 'Management.views.madad_list'),
    (r'^madad/add$', 'Management.views.limited_create_object',
         {'model' : Management.models.Madad,
          'template_name' : 'Management/object_edit.html',
          'permission':'add_madad',          
          'post_save_redirect' : '%(id)s'}),
    (r'^madad/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'model' : Management.models.Madad,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_madad',          
          'post_save_redirect' : '%(id)s'}),
    (r'^madad/(?P<id>\d+)/del$', 'Management.views.madad_del'),
    
    (r'^tax/$', 'Management.views.tax_list'),
    (r'^tax/add$', 'Management.views.limited_create_object',
         {'model' : Management.models.Tax,
          'template_name' : 'Management/object_edit.html',
          'permission':'add_tax',          
          'post_save_redirect' : '%(id)s'}),
    (r'^tax/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'model' : Management.models.Tax,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_tax',          
          'post_save_redirect' : '%(id)s'}),
    (r'^tax/(?P<id>\d+)/del$', 'Management.views.tax_del'),
    
    (r'^salepricemod/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.SalePriceModForm,
          'template_name' : 'Management/sale_mod_edit.html',
          'permission':'change_salepricemod',          
          'post_save_redirect' : '%(id)s'}),
    (r'^salehousemod/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.SaleHouseModForm,
          'template_name' : 'Management/sale_mod_edit.html',
          'permission':'change_salehousemod',          
          'post_save_redirect' : '%(id)s'}),
    (r'^salepre/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.SalePreForm,
          'template_name' : 'Management/sale_mod_edit.html',
          'permission':'change_salepre',          
          'post_save_redirect' : '%(id)s'}),
    (r'^salereject/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.SaleRejectForm,
          'template_name' : 'Management/sale_mod_edit.html',
          'permission':'change_salereject',          
          'post_save_redirect' : '%(id)s'}),
    (r'^salecancel/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'model' : Management.models.SaleCancel,
          'template_name' : 'Management/sale_mod_edit.html',
          'permission':'change_salecancel',          
          'post_save_redirect' : '%(id)s'}),
          
    (r'^nhbranch/(?P<branch_id>\d+)/nhsale/add$', 'Management.views.nhsale_add'),
    (r'^nhsale/(?P<object_id>\d+)/$', 'Management.views.nhsale_edit'),
    (r'^nhsale/(?P<object_id>\d+)/edit$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.NHSaleForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_nhsale',          
          'post_save_redirect' : '../%(id)s'}),
    (r'^nhsaleside/(?P<object_id>\d+)$', 'Management.views.limited_update_object',
         {'form_class' : Management.forms.NHSaleSideForm,
          'template_name' : 'Management/object_edit.html',
          'permission':'change_nhsaleside',          
          'post_save_redirect' : '%(id)s'}),
    (r'^nhsaleside/(?P<object_id>\d+)/payment/add$', 'Management.views.nhsaleside_payment_add'),
    (r'^nhsaleside/(?P<object_id>\d+)/invoice/add$', 'Management.views.nhsaleside_invoice_add'),
    
    (r'^xml/buildings/(?P<project_id>\d+)$', 'Management.views.json_buildings'),
    (r'^xml/employees/(?P<project_id>\d+)$', 'Management.views.json_employees'),
    (r'^xml/houses/(?P<building_id>\d+)$', 'Management.views.json_houses'),
    (r'^xml/house/(?P<house_id>\d+)$', 'Management.views.json_house'),
    (r'^json/links$', 'Management.views.json_links'),
    (r'^invoice_details/(?P<project>\d+)/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.invoice_details'),
    (r'^payment_details/(?P<project>\d+)/(?P<year>\d+)/(?P<month>\d+)$', 'Management.views.payment_details'),
    (r'^house_details/(?P<id>\d+)$', 'Management.views.house_details'),
    (r'^signup_details/(?P<house_id>\d+)$', 'Management.views.signup_details'),
    (r'^project_sales/(?P<id>\d+)$', 'Management.views.project_sales'),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT,
         'show_indexes': True}),
)
