from django.db import models
from django.utils.translation import ugettext
from datetime import datetime, date
from django.contrib.auth.models import User
from templatetags.management_extras import *

Salary_Types = (
                (0, u'ברוטו'),
                (1, u'נטו')
                )
Family_State_Types = (
                      (1, u'רווק'),
                      (2, u'נשוי'),
                      (3, u'גרוש')
                      )
Boolean = (
           (0, u'לא'),
           (1, u'כן')
           )

class Tag(models.Model):
    name = models.CharField(unique = True, max_length=20)
    is_deleted = models.BooleanField(editable=False, default=False)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table = 'Tag'
        ordering = ['name']

class AttachmentType(models.Model):
    name = models.CharField(max_length=10, unique=True)
    def __unicode__(self):
        return unicode(self.name)            
    class Meta:
        db_table = 'AttachmentType'
        
class Attachment(models.Model):
    add_time = models.DateTimeField(auto_now_add=True, editable=False)
    user_added = models.ForeignKey(User, related_name = 'attachments', editable=False, verbose_name=ugettext('user'))
    tags = models.ManyToManyField('Tag', related_name = 'attachments',null=True, blank=True, verbose_name = ugettext('tags'))
    file = models.FileField(ugettext('filename'), upload_to='files')

    type = models.ForeignKey('AttachmentType', verbose_name = ugettext('attachment_type'))
    sr_name = models.CharField(ugettext('sr_name'), max_length=20)
    is_private = models.BooleanField(ugettext('is_private'), blank=True)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    
    project = models.ForeignKey('Project', related_name='attachments', editable=False, null=True)
    employee = models.ForeignKey('Employee', related_name='attachments', editable=False, null=True)
    car = models.ForeignKey('Car', related_name='attachments', editable=False, null=True)
    
    class Meta:
        db_table = 'Attachment'

class Car(models.Model):
    number = models.IntegerField(ugettext('car_num'), unique = True)
    owner = models.CharField(ugettext('car_owner'), max_length = 20)
    insurance_expire_date = models.DateField(ugettext('insurance_expire_date'))
    insurance_man = models.CharField(ugettext('insurance_man'), max_length = 20)
    insurance_phone = models.CharField(ugettext('insurance_phone'), max_length = 10)
    tow_company = models.CharField(ugettext('tow_company'), max_length = 20)
    tow_phone = models.CharField(ugettext('tow_phone'), max_length = 10)
    compulsory_insurance_cost = models.IntegerField(ugettext('compulsory_insurance_cost'))
    comprehensive_insurance_cost = models.IntegerField(ugettext('comprehensive_insurance_cost'))    
    class Meta:
        db_table = 'Car'

class Task(models.Model):
    sender = models.ForeignKey(User, related_name='task_requests', editable=False)
    user = models.ForeignKey(User, related_name='tasks', verbose_name=ugettext('user'))
    content = models.TextField(ugettext('content'))
    time = models.DateTimeField(auto_now_add=True, editable=False)
    is_done = models.BooleanField(default=False, editable=False)
    time_done = models.DateTimeField(null = True, editable=False)
    is_deleted = models.BooleanField(default=False, editable=False)
    
    def do(self):
        self.is_done = True
        self.time_done = datetime.now()
        self.save()
    def delete(self):
        self.is_deleted = True
        self.save()
    class Meta:
        ordering = ['is_done', '-time']
        db_table = 'Task'
        
ReminderStatusAdded, ReminderStatusDone, ReminderStatusDeleted = range(1,4)
class ReminderStatusType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table='ReminderStatusType'
        
class ReminderStatus(models.Model):
    reminder = models.ForeignKey('Reminder', related_name='statuses')
    type = models.ForeignKey('ReminderStatusType')
    time = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return unicode(self.type) + ' - ' + unicode(self.time)
    class Meta:
        db_table='ReminderStatus'
        ordering = ['-time']
        get_latest_by = 'time'
        
class Reminder(models.Model):
    content = models.TextField(ugettext('content'))
    def do(self):
        self.statuses.create(type = ReminderStatusType.objects.get(pk = ReminderStatusDone)).save()
    def delete(self):
        self.statuses.create(type = ReminderStatusType.objects.get(pk = ReminderStatusDeleted)).save()
    class Meta:
        db_table = 'Reminder'
    
class Link(models.Model):
    name = models.CharField(ugettext('name'), max_length=30)
    url = models.URLField(ugettext('url'))
    class Meta:
        db_table = 'Link'
        ordering = ['name']

class ProjectDetails(models.Model):
    architect = models.CharField(ugettext('architect'), max_length=30)
    houses_num = models.PositiveSmallIntegerField(ugettext('houses_num'))
    buildings_num = models.PositiveSmallIntegerField(ugettext('buildings_num'))
    bank = models.CharField(ugettext('accompanied_bank'), max_length=20)
    url = models.URLField(ugettext('url'), null=True, blank=True)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)  
    building_types = models.ManyToManyField('BuildingType', verbose_name=ugettext('building_types'))
    class Meta:
        db_table = 'ProjectDetails'

class ProjectManager(models.Manager):
    def active(self):
        return self.filter(end_date=None, is_marketing=True)

class Project(models.Model):
    details = models.OneToOneField('ProjectDetails', editable=False, null=True)
    initiator = models.CharField(ugettext('initiator'), max_length=30)
    name = models.CharField(ugettext('project name'), max_length=30)
    city = models.CharField(ugettext('city'), max_length=30)
    hood = models.CharField(ugettext('hood'), max_length=30)
    office_address = models.CharField(ugettext('office address'), max_length=30)
    phone = models.CharField(ugettext('project phone'), max_length=15)
    cell_phone = models.CharField(ugettext('project cell phone'), max_length=15)
    fax = models.CharField(ugettext('project fax'), max_length=15);
    mail = models.EmailField(ugettext('mail'), null=True, blank=True)
    is_marketing = models.BooleanField(ugettext('is_marketing'), choices=Boolean)
    start_date = models.DateField(ugettext('startdate'))
    end_date = models.DateField(ugettext('enddate'), null=True, blank=True)
    remarks = models.TextField(ugettext('special_data'), null=True, blank=True)
    demand_contact = models.ForeignKey('Contact', editable=False, related_name='projects_demand', blank=True, null=True)
    payment_contact = models.ForeignKey('Contact', editable=False, related_name='projects_payment', blank=True, null=True)
    contacts = models.ManyToManyField('Contact', related_name='projects', null=True, editable=False)
    reminders = models.ManyToManyField('Reminder', null=True, editable=False)

    objects = ProjectManager()
    
    def demands_unpaid(self):
        return [d for d in self.demands.all() 
                if d.statuses.count()>0 
                and d.payments.count()==0 
                and d.invoices.count()==0
                and d.get_total_amount()>0]
    def demands_noinvoice(self):
        return [d for d in self.demands.all() 
                if d.statuses.count()>0 
                and d.payments.count()>0 
                and d.invoices.count()==0
                and d.get_total_amount()>0]
    def demands_nopayment(self):
        return [d for d in self.demands.all() 
                if d.statuses.count()>0 
                and d.payments.count()==0 
                and d.invoices.count()>0
                and d.get_total_amount()>0]
    def demands_mispaid(self):
        return [d for d in self.demands.all() 
                if d.statuses.count()>0 
                and d.diff()
                and d.get_total_amount()>0]
    def current_demand(self):
        try:
            return Demand.objects.current().get(project = self)
        except Demand.DoesNotExist:
            return None
    def get_open_reminders(self):
        return [r for r in self.reminders.all() if r.statuses.latest().type.id 
                not in (ReminderStatusDeleted,ReminderStatusDone)]
    def sales(self, year = datetime.now().year, month = datetime.now().month):
        return Sale.objects.filter(house__building__project = self,
                                   contractor_pay__month = month,
                                   contractor_pay__year = year)
    def signups(self, year = datetime.now().year, month = datetime.now().month):
        return Signup.objects.filter(house__building__project = self, date__year = year, date__month= month)
    def end(self):
        self.end_date = datetime.now()
    def __unicode__(self):
        return u"%s - %s" % (self.initiator, self.name)
    def houses(self):
        houses = []
        for building in self.non_deleted_buildings():
            houses.extend(building.houses.filter(is_deleted=False))
        return houses
    def non_deleted_buildings(self):
        return self.buildings.filter(is_deleted= False)
    def save(self, *args, **kw):
        models.Model.save(self, *args, **kw)
        if ProjectCommission.objects.filter(project = self).count()==0 :
            ProjectCommission(project = self).save()
    @property
    def is_active(self):
        return self.is_marketing and not self.end_date
    def get_absolute_url(self):
        return '/projects/%s' % self.id
    class Meta:
        verbose_name = ugettext('project')
        verbose_name_plural = ugettext('projects')
        db_table = 'Project'
        ordering = ['initiator','name']

class ParkingType(models.Model):
    name = models.CharField(ugettext('name'), max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table='ParkingType'

PricelistTypeCompany = 1        
class PricelistType(models.Model):
    name = models.CharField(ugettext('name'), max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table='PricelistType'

class Parking(models.Model):
    building = models.ForeignKey('Building', verbose_name=ugettext('building'), related_name='parkings')
    house = models.ForeignKey('House', null=True, blank=True, related_name='parkings', verbose_name=ugettext('house'))
    num = models.PositiveSmallIntegerField(ugettext('parking_num'))
    type = models.ForeignKey('ParkingType', verbose_name=ugettext('parking_type'))
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    def __unicode__(self):
        return u'מס\' %s - %s' % (self.num, self.type)
    class Meta:
        db_table='Parking'
        unique_together = ('building', 'num')
        ordering = ['num']
        
class Storage(models.Model):
    building = models.ForeignKey('Building', verbose_name=ugettext('building'), related_name='storages')
    house = models.ForeignKey('House', null=True, blank=True, related_name='storages', verbose_name=ugettext('house'))
    num = models.PositiveSmallIntegerField(ugettext('storage_num'))
    size = models.FloatField(ugettext('size'), null=True, blank=True)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    def __unicode__(self):
        return self.size and u'מס\' %s - %s מ"ר' % (self.num, self.size) or u'מס\' %s' % self.num 
    class Meta:
        db_table='Storage'
        unique_together = ('building', 'num')
        ordering = ['num']
    
class House(models.Model):
    building = models.ForeignKey('Building', related_name='houses',verbose_name = ugettext('building'), editable=False)
    type = models.ForeignKey('HouseType', verbose_name=ugettext('asset_type'))
    num = models.CharField(ugettext('house_num'), max_length=5)
    floor = models.PositiveSmallIntegerField(ugettext('floor'))
    rooms = models.FloatField(ugettext('rooms'))
    net_size = models.FloatField(ugettext('net_size'))
    garden_size = models.FloatField(ugettext('garden_size'), null=True, blank=True)
    remarks = models.CharField(ugettext('remarks'), max_length = 200, null=True, blank=True)
    
    bruto_size = models.FloatField(ugettext('bruto_size'), null=True, blank=True)
    load_precentage = models.FloatField(ugettext('load_precentage'), null=True, blank=True)
    parking_size = models.FloatField(ugettext('parking_size'), null=True, blank=True)
    
    is_sold = models.BooleanField(ugettext('is_sold'), default= False)
    is_deleted = models.BooleanField(default= False, editable= False)
    def pricelist_types(self):
        types = []
        for v in self.versions.all():
            if types.count(v.type) == 0:
                types.append(v.type)
        return types
    def get_cottage_num(self):
        return self.num[:-1]
    def get_signup(self):
        s = self.signups.filter(cancel=None)
        return s.count() == 1 and s[0] or None 
    def get_sale(self):
        s = self.sales.filter(salecancel=None)
        if s.count() > 1:
            return s
        elif s.count() == 1:
            return s[0]
        return None
    def __unicode__(self):
        return unicode(self.num)
    class Meta:
        unique_together = ('building', 'num')
        ordering = ['num']
        db_table = 'House'

BuildingTypeCottage = 3
class BuildingType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table = 'BuildingType'

HouseTypeCottage = 2
class HouseType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table = 'HouseType'

class HireType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table = 'HireType'
        
class HouseVersion(models.Model):
    house = models.ForeignKey('House', related_name = 'versions', editable=False)
    type = models.ForeignKey('PricelistType', verbose_name = ugettext('pricelist_type'), editable=False)
    date = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField(ugettext('price'))    
    class Meta:
        get_latest_by = 'date'
        ordering = ['-date']
        db_table = 'HouseVersion'

RankRegionalSaleManager = 8
class RankType(models.Model):
    name = models.CharField(ugettext('rank'), max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table = 'RankType'
        ordering = ['name']
        
class ParkingCost(models.Model):
    pricelist = models.ForeignKey('Pricelist', related_name='parking_costs')
    type = models.ForeignKey('ParkingType', verbose_name = ugettext('parking_type'))
    cost = models.FloatField(ugettext('cost'))
    class Meta:
        db_table='ParkingCost'
        unique_together = ('pricelist','type')

class Pricelist(models.Model):
    include_tax = models.NullBooleanField(ugettext('include_tax'))
    include_lawyer = models.NullBooleanField(ugettext('include_lawyer'))
    include_parking = models.NullBooleanField(ugettext('include_parking'))
    include_storage = models.NullBooleanField(ugettext('include_storage'))
    settle_date = models.DateField(ugettext('settle_date'), null=True, blank=True)
    allowed_discount = models.FloatField(ugettext('allowed_discount'), default=0)
    is_permit = models.NullBooleanField(ugettext('is_permit'))
    permit_date = models.DateField(ugettext('permit_date'), null=True, blank=True)
    lawyer_fee = models.FloatField(ugettext('lawyer_fee'), default=0)
    register_expense = models.FloatField(ugettext('register_expense'), default=0)
    storage_cost = models.FloatField(ugettext('storage_cost'), null=True, blank=True)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    class Meta:
        db_table = 'Pricelist'

class Building(models.Model):
    pricelist = models.OneToOneField('Pricelist', editable=False, related_name='building')
    project = models.ForeignKey('Project', related_name = 'buildings', verbose_name=ugettext('project'))
    num = models.CharField(ugettext('building_num'), max_length = 4)
    name = models.CharField(ugettext('name'), max_length=10, null=True, blank=True)
    type = models.ForeignKey('BuildingType', verbose_name=ugettext('building_types'))
    floors = models.PositiveSmallIntegerField(ugettext('floors'))
    house_count = models.PositiveSmallIntegerField(ugettext('houses_num'))
    stage = models.CharField(ugettext('stage'), max_length = 1, null=True, blank=True)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    is_deleted = models.BooleanField(default= False, editable= False)
    def sold_houses(self):
        return [h for h in self.houses.filter(is_deleted=False) if h.get_sale() != None or h.is_sold]
    def signed_houses(self):
        return [h for h in self.houses.filter(is_deleted=False) if h.get_signup() != None]
    def avalible_houses(self):
        return [h for h in self.houses.filter(is_deleted=False) if h.get_signup() == None and h.get_sale() == None and not h.is_sold]
    def is_cottage(self):
        return self.type.id == BuildingTypeCottage
    def pricelist_types(self):
        types = []
        for h in self.houses.filter(is_deleted=False):
            for t in h.pricelist_types():
                if types.count(t) == 0:
                    types.append(t)
        return types
    def save(self, *args, **kw):
        try:
            pl = self.pricelist
        except Pricelist.DoesNotExist:
            pl = Pricelist()
            pl.save()
            self.pricelist = pl
        models.Model.save(self, *args, **kw)
    def __unicode__(self):
        return self.num
    class Meta:
        unique_together = ('project', 'num')
        db_table = 'Building'
        
class Person(models.Model):
    first_name = models.CharField(ugettext('first_name'), max_length=20)
    last_name = models.CharField(ugettext('last_name'), max_length=20)
    phone = models.CharField(ugettext('phone'), max_length=10, null=True, blank=True)
    cell_phone = models.CharField(ugettext('cell_phone'), max_length=10, null=True, blank=True)
    mail = models.EmailField(ugettext('mail'), null=True, blank=True)
    address = models.CharField(ugettext('address'), max_length=40, null=True, blank=True)
    role = models.CharField(ugettext('role'), max_length= 20, null=True, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)
    class Meta:
        abstract = True
        verbose_name = ugettext('person')
        verbose_name_plural = ugettext('persons')
        
class Contact(Person):
    fax = models.CharField(ugettext('fax'), max_length=10, null=True, blank=True);
    company = models.CharField(ugettext('company'), max_length=20, null=True, blank=True)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    class Meta:
        db_table = 'Contact'
        unique_together = ('first_name','last_name')

class EmploymentTerms(models.Model):
    salary_base = models.PositiveIntegerField(ugettext('salary base'))
    salary_net = models.BooleanField(ugettext('salary net'), choices= Salary_Types)
    safety = models.PositiveIntegerField(ugettext('safety'))
    hire_type = models.ForeignKey('HireType', verbose_name=ugettext('hire_type'))
    include_tax = models.BooleanField(ugettext('commission_include_tax'), blank=True)
    include_lawyer = models.BooleanField(ugettext('commission_include_lawyer'), blank=True)
    class Meta:
        db_table='EmploymentTerms'

class EmployeeManager(models.Manager):
    def active(self):
        return self.filter(work_end = None)
    def archive(self):
        return self.exclude(work_end = None)

class Employee(Person):
    pid = models.PositiveIntegerField(ugettext('pid'), unique=True)
    rank = models.ForeignKey('RankType', verbose_name=ugettext('rank'))
    birth_date = models.DateField(ugettext('birth_date'))
    home_phone = models.CharField(ugettext('home phone'), max_length=10)
    mate_phone = models.CharField(ugettext('mate phone'), max_length=10, null=True, blank=True)
    family_state = models.PositiveIntegerField(ugettext('family state'), choices = Family_State_Types)
    child_num = models.PositiveIntegerField(ugettext('child num'), null=True, blank=True)
    
    projects = models.ManyToManyField('Project', verbose_name=ugettext('projects'), related_name='employees', 
                                      null=True, blank=True)
    work_start = models.DateField(ugettext('work start'))
    work_end = models.DateField(ugettext('work end'), null=True, blank=True)
    
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    reminders = models.ManyToManyField('Reminder', null=True, editable=False)
    account = models.OneToOneField('Account', related_name='employee',editable=False, null=True, blank=True)
    employment_terms = models.OneToOneField('EmploymentTerms',editable=False, related_name='employee', null=True, blank=True)
    
    objects = EmployeeManager()
    
    def get_open_reminders(self):
        return [r for r in self.reminders.all() if r.statuses.latest().type.id 
                not in (ReminderStatusDeleted,ReminderStatusDone)]
    def end(self):
        self.work_end = datetime.now()
    def save(self, *args, **kw):
        models.Model.save(self, *args, **kw)
        for p in self.projects.all():
            if self.commissions.filter(project = p).count() == 0:
                EPCommission(employee = self, project = p).save()
    def loan_left(self):
        n = 0
        for loan in self.loans.all():
            n += loan.amount
        for pay in self.loan_pays.all():
            n -= pay.amount
        return n
    def loans_and_pays(self):
        l = [l for l in self.loans.all()]
        l.extend([p for p in self.loan_pays.all()])
        l.sort(lambda x,y: cmp(x.date, y.date))
        left = 0
        for o in l:
            if isinstance(o, Loan):
                left += o.amount
            elif isinstance(o, LoanPay):
                left -= o.amount
            o.left = left
        return l
    def get_absolute_url(self):
        return '/employees/%s' % self.id
    class Meta:
        verbose_name = ugettext('employee')
        verbose_name_plural = ugettext('employees')
        db_table = 'Employee'
        ordering = ['rank','-work_start']

class NHBranch(models.Model):
    name = models.CharField(ugettext('name'), max_length=30, unique=True)
    manager = models.ForeignKey('NHEmployee', null=True, blank=True,
                                related_name='branch_manager',
                                verbose_name=ugettext('nhbranch_manager'))
    mail = models.EmailField(ugettext('mail'), null=True, blank=True)
    phone = models.CharField(ugettext('phone'), max_length=20, null=True, blank=True)
    url = models.URLField(ugettext('url'), null=True, blank=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table='NHBranch'
    
class NHEmployee(Person):
    pid = models.PositiveIntegerField(ugettext('pid'), unique=True)
    birth_date = models.DateField(ugettext('birth_date'))
    home_phone = models.CharField(ugettext('home phone'), max_length=10)
    mate_phone = models.CharField(ugettext('mate phone'), max_length=10, null=True, blank=True)
    family_state = models.PositiveIntegerField(ugettext('family state'), choices = Family_State_Types)
    child_num = models.PositiveIntegerField(ugettext('child num'), null=True, blank=True)
    
    nhbranch = models.ForeignKey('NHBranch', verbose_name=ugettext('nhbranch'), related_name='nhemployees')
    
    work_start = models.DateField(ugettext('work start'))
    work_end = models.DateField(ugettext('work end'), null=True, blank=True)
    
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    reminders = models.ManyToManyField('Reminder', null=True, editable=False)
    account = models.OneToOneField('Account', related_name='nhemployee',editable=False, null=True, blank=True)
    employment_terms = models.OneToOneField('EmploymentTerms',editable=False, related_name='nhemployee', null=True, blank=True)
    
    objects = EmployeeManager()
    
    def get_open_reminders(self):
        return [r for r in self.reminders.all() if r.statuses.latest().type.id 
                not in (ReminderStatusDeleted,ReminderStatusDone)]
    def end(self):
        self.work_end = datetime.now()
    def loan_left(self):
        n = 0
        for loan in self.loans.all():
            n += loan.amount
        for pay in self.loan_pays.all():
            n -= pay.amount
        return n
    def loans_and_pays(self):
        l = [l for l in self.loans.all()]
        l.extend([p for p in self.loan_pays.all()])
        l.sort(lambda x,y: cmp(x.date, y.date))
        left = 0
        for o in l:
            if isinstance(o, Loan):
                left += o.amount
            elif isinstance(o, LoanPay):
                left -= o.amount
            o.left = left
        return l
    def get_absolute_url(self):
        return '/nhemployees/%s' % self.id
    class Meta:
        db_table = 'NHEmployee'
        ordering = ['nhbranch','-work_start']
        
class AdvancePayment(models.Model):
    employee = models.ForeignKey('Employee', related_name = 'advance_payments', verbose_name=ugettext('employee'))
    amount = models.IntegerField(ugettext('amount'))
    date = models.DateField(ugettext('date'))
    date_paid = models.DateField(editable=False, null=True)
    is_paid = models.NullBooleanField(editable=False)
    def pay(self):
        self.is_paid = True
        self.date_paid = datetime.now()
        self.save()
    def to_loan(self):
        self.is_paid=False
        self.save()
    class Meta:
        db_table='AdvancePayment'
        get_latest_by = 'date'
        ordering = ['-date']
        
class Loan(models.Model):
    employee = models.ForeignKey('Employee', related_name = 'loans', verbose_name=ugettext('employee'),
                                 null=True)
    nhemployee = models.ForeignKey('NHEmployee', related_name = 'loans', verbose_name=ugettext('nhemployee'),
                                   null=True)
    amount = models.IntegerField(ugettext('amount'))
    date = models.DateField(ugettext('date'), default=date.today())
    pay_num = models.PositiveSmallIntegerField(ugettext('pay_num'))
    remarks = models.TextField(ugettext('remarks'), blank=True, null=True)
    def save(self, *args, **kw):
        if not self.id:
            'link the loan to the current employee salary'
            salary = self.employee.salaries.current()[0]
            self.date = datetime(salary.year, salary.month, 1)
        models.Model.save(self, *args, **kw)
    class Meta:
        db_table = 'Loan'

class LoanPay(models.Model):
    employee = models.ForeignKey('Employee', related_name='loan_pays', editable=False,
                                 null=True)
    nhemployee = models.ForeignKey('NHEmployee', related_name = 'loan_pays', verbose_name=ugettext('nhemployee'),
                                   null=True)
    date = models.DateField(ugettext('date'), auto_now_add=True)
    amount = models.FloatField(ugettext('amount'))
    remarks = models.TextField(ugettext('remarks'), blank=True, null=True)
    class Meta:
        db_table = 'LoanPay'

class EmployeeSalaryManager(models.Manager):
    def current(self):
        n = datetime.now()
        if n.day <= 22:
            n = datetime(n.year, n.month == 1 and 12 or n.month - 1, n.day)
        return self.filter(year = n.year, month = n.month)

class EmployeeSalary(models.Model):
    employee = models.ForeignKey('Employee', verbose_name=ugettext('employee'), related_name='salaries')
    month = models.PositiveSmallIntegerField(ugettext('month'), editable=False, choices=((i,i) for i in range(1,13)))
    year = models.PositiveSmallIntegerField(ugettext('year'), editable=False, choices=((i,i) for i in range(datetime.now().year - 10,
                                                                                             datetime.now().year + 10)))
    base = models.IntegerField(ugettext('salary_base'))
    commissions = models.IntegerField(ugettext('commissions'), editable=False)
    safety_net = models.PositiveSmallIntegerField(ugettext('safety_net'), null=True, blank=True)
    var_pay = models.SmallIntegerField(ugettext('var_pay'), null=True, blank=True)
    var_pay_type = models.CharField(ugettext('var_pay_type'), max_length=20, null=True, blank=True)
    refund = models.SmallIntegerField(ugettext('refund'), null=True, blank=True)
    refund_type = models.CharField(ugettext('refund_type'), max_length=20, null=True, blank=True)
    deduction = models.SmallIntegerField(ugettext('deduction'), null=True, blank=True)
    deduction_type = models.CharField(ugettext('deduction_type'), max_length=20, null=True, blank=True)
    approved = models.BooleanField(ugettext('approved'), editable=False)
    remarks = models.TextField(ugettext('remarks'),null=True, blank=True)
    
    objects = EmployeeSalaryManager()
    
    @property
    def sales(self):
        sales = {}
        if self.employee.rank.id != RankRegionalSaleManager:
            sales['direct'] = self.employee.sales.filter(employee_pay__year = self.year, employee_pay__month = self.month)
            for p in self.employee.projects.all():
                all = Sale.objects.filter(house__building__project = p,
                                          employee_pay__month = self.month,
                                          employee_pay__year = self.year)
                if all:
                    sales[p] = all.filter(employee = None)
        else:
            for p in self.employee.projects.all():
                sales[p] = Sale.objects.filter(house__building__project = p,
                                               employee_pay__month = self.month,
                                               employee_pay__year = self.year)
        return sales
    @property
    def sales_count(self):
        i=0
        for v in self.sales.values():
            if v:
                i+=v.count()
        return i
    @property
    def loan_pay(self):
        amount = 0
        for lp in self.employee.loan_pays.filter(date__year = self.year, date__month = self.month):
            amount += lp.amount
        return amount
    @property
    def total_amount(self):
        return self.base + self.commissions + (self.var_pay or 0) + (self.safety_net or 0) - (self.deduction or 0)
    def check_amount(self):
        return self.total_amount - self.loan_pay
    @property
    def bruto_amount(self):
        if not self.employee.employment_terms or self.employee.employment_terms.salary_net:
            return None
        return self.total_amount
    def calculate(self):
        amount = 0
        for epc in self.employee.commissions.all():
            total_sales = self.sales
            for k in total_sales:
                if total_sales[k] == None:
                    continue
                sales = total_sales[k].filter(house__building__project = epc.project)
                if sales.count() == 0:
                    continue
                amount += epc.calc(sales)
                for s in sales.all():
                    s.employee_paid = True
                    s.save()
        self.commissions = amount
    class Meta:
        db_table='EmployeeSalary'
        unique_together = ('employee','year','month')
    
class EPCommission(models.Model):
    employee = models.ForeignKey('Employee', related_name='commissions')
    project = models.ForeignKey('Project', related_name= 'epcommission')
    c_var = models.OneToOneField('CVar', related_name= 'epcommission', null=True)
    c_var_precentage = models.OneToOneField('CVarPrecentage', related_name= 'epcommission', null=True)
    c_by_price = models.OneToOneField('CByPrice', related_name= 'epcommission', null= True)
    b_house_type = models.OneToOneField('BHouseType', related_name= 'epcommission', null=True)
    b_discount_save = models.OneToOneField('BDiscountSave', related_name= 'epcommission', null=True)
    b_sale_rate = models.OneToOneField('BSaleRate', related_name= 'epcommission', null=True)
    def calc(self, sales):
        dic = {}# key: sale value: commission amount for sale
        for c in ['c_var', 'c_by_price', 'b_house_type', 'b_discount_save']:
            if getattr(self,c) == None:
                continue
            amounts = getattr(self,c).calc(sales)
            for s in amounts:
                dic[s] = dic.has_key(s) and dic[s] + amounts[s] or amounts[s]
        for c in ['c_var_precentage']:
            if getattr(self,c) == None:
                continue
            precentages = getattr(self,c).calc(sales)
            for s in precentages:
                dic[s] = dic.has_key(s) and dic[s] + precentages[s] * s.employee_price() / 100 or precentages[s] * s.employee_price() / 100
        total_amount = 0
        for s in dic:
            total_amount = total_amount + dic[s]
        for c in ['b_sale_rate']:
            if getattr(self,c) == None:
                continue
            amount = getattr(self,c).calc(sales)
            total_amount = total_amount + amount
        return total_amount
    class Meta:
        db_table = 'EPCommission'

class CAmount(models.Model):
    c_var = models.ForeignKey('CVar', related_name='amounts', editable=False)
    amount = models.PositiveIntegerField(ugettext('commission amount'))
    index = models.PositiveSmallIntegerField(editable=False)

    def save(self, *args, **kw):
        if not self.id:
            try:
                latest = self.c_var.amounts.latest()
                self.index = latest.index + 1
            except:
                self.index = 1
        models.Model.save(self, *args, **kw)

    class Meta:
        ordering = ['index']
        get_latest_by = 'index'
        unique_together = ('index','c_var')
        db_table = 'ECAmount'
        
class CPrecentage(models.Model):
    c_var_precentage = models.ForeignKey('CVarPrecentage', related_name='precentages', editable=False)
    precentage = models.FloatField(ugettext('commission precentage'))
    index = models.PositiveSmallIntegerField(editable=False)
    
    def save(self, *args, **kw):
        if not self.id:
            try:
                latest = self.c_var_precentage.precentages.latest()
                self.index = latest.index + 1
            except:
                self.index = 1
        models.Model.save(self, *args, **kw)
    
    class Meta:
        ordering = ['index']
        get_latest_by = 'index'
        unique_together = ('index','c_var_precentage')
        db_table = 'CPrecentage'

class CPriceAmount(models.Model):
    c_by_price = models.ForeignKey('CByPrice', related_name='price_amounts', editable=False)
    price = models.PositiveIntegerField(ugettext('price'))
    amount = models.PositiveIntegerField(ugettext('commission amount'))
    
    class Meta:
        ordering = ['price']
        unique_together = ('price','c_by_price')
        db_table = 'CPriceAmount'
    
class HouseTypeBonus(models.Model):
    bonus = models.ForeignKey('BHouseType', related_name ='bonuses')
    type = models.ForeignKey('HouseType', verbose_name=ugettext('house_type'))
    amount = models.PositiveIntegerField(ugettext('amount'))
    class Meta:
        db_table = 'HouseTypeBonus'
        unique_together = ('bonus','type')
        
class SaleRateBonus(models.Model):
    b_sale_rate = models.ForeignKey('BSaleRate', related_name='bonuses')
    house_count = models.PositiveSmallIntegerField(ugettext('house count'))
    amount = models.PositiveIntegerField(ugettext('commission amount'))
    class Meta:
        ordering = ['house_count']
        db_table = 'SaleRateBonus'
    
class CVar(models.Model):
    is_retro = models.BooleanField(ugettext('retroactive'))
    def calc(self,sales):
        dic = {}
        i = 0
        if self.is_retro:
            c = self.get_amount(sales.count()).amount
            for s in sales.all():
                dic[s] = c
        else:
            i=0
            for s in sales.all():
                i += 1
                dic[s] = self.get_amount(i).amount
        return dic
    def get_amount(self, index):
        amount = self.amounts.filter(index = index)
        if amount.count() == 1:
            return amount[0]
        else:
            for a in self.amounts.all():
                amount = a
                if a.index > index:
                    break
        return amount
            
    class Meta:
        db_table = 'CVar'
        
class CVarPrecentage(models.Model):
    is_retro = models.BooleanField(ugettext('retroactive'))
    start_retro = models.PositiveSmallIntegerField(ugettext('retroactive_start'),null=True, blank=True, default=1)
    def calc(self, sales):
        dic={}
        i=0
        if self.is_retro and sales.count() >= self.start_retro:
            c = self.get_precentage(sales.count()).precentage
            for s in sales.all():
                dic[s] = c
        else:
            i=0
            for s in sales.all():
                i += 1
                dic[s] = self.get_precentage(i).precentage
        return dic            
    def get_precentage(self, index):
        precentage = self.precentages.filter(index = index)
        if precentage.count() == 1:
            return precentage[0]
        else:
            for p in self.precentages.all():
                precentage = p
                if p.index > index:
                    break
        return precentage
    class Meta:
        db_table = 'CVarPrecentage'
 
class CVarPrecentageFixed(models.Model):
    is_retro = models.BooleanField(ugettext('retroactive'))
    first_count = models.PositiveSmallIntegerField(ugettext('cvf first count'))
    first_precentage = models.FloatField(ugettext('precentage'))
    step = models.FloatField(ugettext('cvf step'))
    last_count = models.PositiveSmallIntegerField(ugettext('cvf last count'), null=True, blank=True)
    last_precentage = models.FloatField(ugettext('precentage'), null=True, blank=True)
    def calc(self, sales):
        dic = {}
        if self.is_retro and sales.count() > self.first_count:
            precentage = self.first_precentage + self.step * (sales.count() - self.first_count)
            for s in sales.all():
                dic[s] = precentage
        else:
            for s in sales.all()[:self.first_count]:
                dic[s] = self.first_precentage
            if sales.all().count() <= self.first_count:
                return dic
            i = self.first_count + 1
            for s in sales.all()[self.first_count+1:]:
                dic[s] = self.first_precentage + self.step * (i - self.first_count)
                i += 1
        return dic
    class Meta:
        db_table = 'CVarPrecentageFixed'

class CByPrice(models.Model):
    def calc(self, sales):
        dic = {}
        for s in sales.all():
            dic[s] = self.get_amount(s.price)
        return dic
    def get_amount(self, price):
        amount = 0
        for pa in self.price_amounts.reverse():
            if price >= pa.price:
                break
            amount = pa.amount
        return amount
    class Meta:
        db_table = 'CByPrice'
   
class CZilber(models.Model):
    base = models.FloatField(ugettext('commission_base'))
    b_discount = models.FloatField(ugettext('b_discount'))
    b_sale_rate = models.FloatField(ugettext('b_sale_rate'))
    b_sale_rate_max = models.FloatField(ugettext('max_commission'))
    base_madad = models.FloatField(ugettext('madad_base'))
    third_start = models.DateField(ugettext('third_start'))
    def calc(self, month):
        '''
        month is datetime
        '''
        prev_sales = {}
        p = self.projectcommission.project
        d = p.demands.get(year = month.year, month = month.month)
        qs = self.third_start
        while qs < month:
            t = date(qs.month == 12 and qs.year + 1 or qs.year, 
                     (qs.month + 4) % 12 or 12, 1)
            if t > month:
                break
            qs = t
        start = qs#the start of the current third.
        #gather all sales from start of third
        while qs < month:
            prev_sales[qs] = p.sales(qs.year, qs.month)
            qs = date(qs.month == 12 and qs.year + 1 or qs.year, 
                      (qs.month + 1) % 12 or 12, 1)
        sales = p.sales(month.year, month.month)
        #calculate comulative sale count for third
        third_sale_count = sales.count()
        for m in prev_sales:
            third_sale_count += prev_sales[m] and prev_sales[m].count() or 0
        #each sale (over the first) applies sale rate bonus
        base = self.base + self.b_sale_rate * (third_sale_count - 1)
        if base > self.b_sale_rate_max:
            base = self.b_sale_rate_max
        for s in sales:
            #check if in last month of the third
            if (start.month + 4) % 12 == month.month - 1: 
                discount_bonus = 0
                if Madad.objects.count() > 0 and self.base_madad:
                    memudad = (Madad.objects.latest().value / self.base_madad * 0.6 + 1) * s.company_price
                    discount_bonus += (s.price_final - mumdad) * b_discount
                    d.bonus = discount_bonus
                    d.bonus_type = u'חסכון בהנחה'
            s.pc_base = base
            s.c_final = base
            s.price_final = s.project_price()
            s.save()
        prev_adds = 0
        for m in prev_sales:
            if not prev_sales[m]:
                continue
            for s in prev_sales[m].all():
                prev_adds += (base - s.pc_base) * s.price_final / 100
        d.var_pay = prev_adds
        d.var_pay_type = u'תוספת בגין %s עד %s' % (start.strftime('%d/%m/%Y'), 
                                                   date(month.month == 1 and month.year-1 or month.year, 
                                                        month.month == 1 and 12 or month.month, 
                                                        1).strftime('%d/%m/%Y'))
        d.save()
    class Meta:
        db_table = 'CZilber'

class BDiscountSave(models.Model):
    precentage_bonus = models.PositiveIntegerField(ugettext('precentage_bonus'))
    max_for_bonus = models.FloatField(ugettext('max_bonus'), blank=True, null=True)
    def calc(self, sales):
        dic = {}
        for s in sales.all():
            if s.allowed_discount and s.discount:
                saved = s.allowed_discount - s.discount
            else:
                saved = 0
            if saved < 0:
                saved = 0
            if self.max_for_bonus and saved > self.max_for_bonus:
                saved = self.max_for_bonus
            dic[s] = saved * self.precentage_bonus
        return dic
    class Meta:
        db_table = 'BDiscountSave'
        
class BDiscountSavePrecentage(models.Model):
    precentage_bonus = models.FloatField(ugettext('precentage_bonus'))
    max_for_bonus = models.FloatField(ugettext('max_bonus'), blank=True, null=True)
    def calc(self, sales):
        dic = {}
        for s in sales.all():
            if s.allowed_discount and s.discount:
                saved = s.allowed_discount - s.discount
            else:
                saved = 0
            if saved < 0:
                saved = 0
            if self.max_for_bonus and saved > self.max_for_bonus:
                saved = self.max_for_bonus
            dic[s] = saved * self.precentage_bonus
        return dic
    class Meta:
        db_table = 'BDiscountSavePrecentage'

class BHouseType(models.Model):
    def calc(self, sales):
        dic={}
        for s in sales.all():
            b = self.bonuses.filter(type = s.house.type)
            dic[s] = b.count() == 1 and b[0].amount or 0
        return dic
    class Meta:
        db_table = 'BHouseType'    
        
class BSaleRate(models.Model):
    def calc(self,sales):
        c = sales.count()
        for b in self.bonuses.reverse():
            if c >= b.house_count:
                return b.amount
        return 0
    class Meta:
        db_table = 'BSaleRate'
    
class ProjectCommission(models.Model):
    project = models.OneToOneField('Project', related_name= 'commissions', editable=False)
    c_var_precentage = models.OneToOneField('CVarPrecentage', related_name= 'projectcommission', null=True, editable=False)
    c_var_precentage_fixed = models.OneToOneField('CVarPrecentageFixed', related_name= 'projectcommission', null=True, editable=False)
    c_zilber = models.OneToOneField('CZilber', related_name='projectcommission', null=True, editable=False)
    b_discount_save_precentage = models.OneToOneField('BDiscountSavePrecentage', related_name= 'projectcommission', null=True, editable=False)
   
    add_amount = models.PositiveIntegerField(ugettext('add_amount'), null=True, blank=True)
    add_type = models.CharField(ugettext('add_type'), max_length = 20, null=True, blank=True)
    include_tax = models.NullBooleanField(ugettext('commission_include_tax'), blank=True)
    include_lawyer = models.NullBooleanField(ugettext('commission_include_lawyer'), blank=True,
                                         choices = (
                                                    ('','לא משנה'),
                                                    (0, 'לא'),
                                                    (1, 'כן')
                                                    ))
    max = models.FloatField(ugettext('max_commission'), null=True, blank=True)
    agreement = models.FileField(ugettext('agreement'), upload_to='files', null=True, blank=True)
    remarks = models.TextField(ugettext('commission_remarks'), null=True, blank=True)
    def calc(self, sales):
        '''
        sales should be a QuerySet. returns sales with commission fields
        '''
        if getattr(self, 'c_zilber') != None:
            demand = sales[0].demand
            month = date(demand.year, demand.month, 1)
            getattr(self, 'c_zilber').calc(month)
            return
        dic={}
        details={}
        for c in ['c_var_precentage','c_var_precentage_fixed','b_discount_save_precentage']:
            if getattr(self,c) == None:
                continue
            precentages = getattr(self,c).calc(sales)
            for s in precentages:
                dic[s] = dic.has_key(s) and dic[s] + precentages[s] or precentages[s]
                if c == 'b_discount_save_precentage':
                    attr = 'pb_dsp'
                elif c == 'c_var_precentage' or c == 'c_var_precentage_fixed':
                    attr = 'pc_base'
                    if self.max and precentages[s] > self.max:
                        precentages[s] = self.max#set base commission to max commission
                if not details.has_key(s):
                    details[s]={}
                details[s][attr] = precentages[s]
        if self.max:
            for s in dic:
                if dic[s] > self.max:
                    dic[s] = self.max
        for s in details:
            for a, v in details[s].items():
                setattr(s, a, v)#updates commission values to sale instance
            s.price_final = s.project_price()
            s.c_final = dic[s]
            s.save()
        return [s for s in dic]

    class Meta:
        db_table = 'ProjectCommission'
  
class Invoice(models.Model):
    num = models.IntegerField(ugettext('invoice_num'), unique=True)
    creation_date = models.DateField(auto_now_add = True)
    date = models.DateField(ugettext('invoice_date'))
    amount = models.IntegerField(ugettext('amount'))
    remarks = models.TextField(ugettext('remarks'), null=True,blank=True)
    def __unicode__(self):
        return u'צק על סך %s ש"ת' % commaise(self.amount)
    class Meta:
        db_table = 'Invoice'
        get_latest_by = 'creation_date'

class PaymentType(models.Model):
    name = models.CharField(max_length=20)
    def __unicode__(self):
        return unicode(self.name)  
    class Meta:
        db_table = 'PaymentType'

class Payment(models.Model):
    num = models.IntegerField(ugettext('check_num'), unique=True, null=True, blank=True)
    support_num = models.IntegerField(ugettext('support_num'), null=True, blank=True)
    payment_type = models.ForeignKey('PaymentType', verbose_name=ugettext('payment_type'))
    payment_date = models.DateField(ugettext('payment_date'))
    creation_date = models.DateField(auto_now_add = True)
    amount = models.IntegerField(ugettext('amount'))
    remarks = models.TextField(ugettext('remarks'), null=True,blank=True)
    def __unicode__(self):
        return u'חשבונית על סך %s ש"ח' % commaise(self.amount)
    class Meta:
        db_table = 'Payment'
        get_latest_by = 'creation_date'

DemandFeed, DemandClosed, DemandSent, DemandFinished = range(1,5)

class DemandStatusType(models.Model):
    name = models.CharField(max_length=20)
    def __unicode__(self):
        return unicode(self.name)  
    class Meta:
        db_table = 'DemandStatusType'

class DemandStatus(models.Model):
    demand = models.ForeignKey('Demand', related_name='statuses')
    date = models.DateTimeField(default=datetime.now())
    type = models.ForeignKey('DemandStatusType')
    def __unicode__(self):
        return u'%s - %s' % (self.type, self.date.strftime('%d/%m/%Y %H:%M'))
    class Meta:
        db_table = 'DemandStatus'
        get_latest_by = 'date'

def demand_month():
    now = datetime.now()
    if now.day <= 22:
        now = datetime(now.year, now.month == 1 and 12 or now.month - 1, now.day)
    return now
      
class DemandManager(models.Manager):
    def current(self):
        now = demand_month()
        return self.filter(year = now.year, month = now.month)

DemandNoInvoice, DemandNoPayment, DemandPaidPlus, DemandPaidMinus, DemandPaid = range(1, 6)
      
class Demand(models.Model):
    project = models.ForeignKey('Project', related_name='demands', verbose_name = ugettext('project'))
    month = models.PositiveSmallIntegerField(ugettext('month'), choices=((i,i) for i in range(1,13)))
    year = models.PositiveSmallIntegerField(ugettext('year'), choices=((i,i) for i in range(datetime.now().year - 10,
                                                                                             datetime.now().year + 10)))
    fixed_pay = models.IntegerField(ugettext('fixed_pay'),blank=True, null=True)
    fixed_pay_type = models.CharField(ugettext('fixed_pay_type'), max_length=20, null=True, blank=True)
    var_pay = models.IntegerField(ugettext('var_pay'), null=True, blank=True)
    var_pay_type = models.CharField(ugettext('var_pay_type'), max_length=50, null=True, blank=True)
    bonus = models.IntegerField(ugettext('bonus'),blank=True, null=True)
    bonus_type = models.CharField(ugettext('bonus_type'), max_length=20, null=True, blank=True)
    fee = models.IntegerField(ugettext('fee'),blank=True, null=True)
    fee_type = models.CharField(ugettext('fee_type'), max_length=20, null=True, blank=True)
    remarks = models.TextField(ugettext('remarks'), null=True,blank=True)
    is_finished = models.BooleanField(default=False, editable=False)
    reminders = models.ManyToManyField('Reminder', null=True, editable=False)

    invoices = models.ManyToManyField('Invoice',  related_name = 'demands', 
                                      editable=False, null=True, blank=True)
    payments = models.ManyToManyField('Payment',  related_name = 'demands', 
                                      editable=False, null=True, blank=True)

    objects = DemandManager()
    
    def get_absolute_url(self):
        return '/demands/%s' % self.id
    def get_salaries(self):
        s = []
        for e in self.project.employees.all():
            s.append(e.salaries.get(year = self.year, month = self.month))
        return s
    @property
    def was_sent(self):
        if self.statuses.count() == 0:
            return False
        return self.statuses.latest().type.id == DemandSent
    @property
    def is_fixed(self):
        return self.sales.exclude(salehousemod=None, salepricemod=None,
                                  salepre=None, salereject=None).count() > 0
    def get_open_reminders(self):
        return [r for r in self.reminders.all() if r.statuses.latest().type.id 
                not in (ReminderStatusDeleted,ReminderStatusDone)]
    def get_pricemodsales(self):
        return self.sales.exclude(salepricemod=None)
    def get_housemodsales(self):
        return self.sales.exclude(salehousemod=None)
    def get_presales(self):
        return self.sales.exclude(salepre=None)
    def get_rejectedsales(self):
        return self.sales.exclude(salereject=None)
    def get_sales(self):
        return Sale.objects.filter(salecancel=None,
                                   contractor_pay__year = self.year,
                                   contractor_pay__month = self.month,
                                   house__building__project = self.project)
    def get_sales_amount(self):
        amount = 0
        for s in self.get_sales():
            amount = amount + s.price
        return amount
    def get_final_sales_amount(self):
        amount = 0
        for s in self.get_sales():
            amount = amount + s.price_final
        return amount
    def get_total_final_prices(self):
        amount = 0
        for s in self.get_sales():
            amount = amount + s.price_final
        return amount
    def calc_sales_commission(self):
        if self.get_sales().count() == 0:
            return
        c = self.project.commissions
        c.calc(self.get_sales())
    def get_sales_commission(self):
        i=0
        for s in self.get_sales():
            i += s.c_final_worth
        return i
    def get_total_amount(self):
        return self.get_sales_commission() + (self.fixed_pay or 0) + (self.var_pay or 0) + (self.bonus or 0) - (self.fee or 0)
    def get_deleted_sales(self):
        return [s for s in self.sales.filter(is_deleted=True)]
    def diff(self):
        if self.invoices.count() > 0 and self.payments.count() > 0:
            return self.invoices.latest().amount - self.payments.latest().amount
        else:
            return None
    def state(self):
        if self.invoices.count()==0:
            return DemandNoInvoice
        if self.payments.count()==0:
            return DemandNoPayment
        diff = self.diff()
        if diff > 0:
            return DemandPaidPlus
        if diff < 0:
            return DemandPaidMinus
        return DemandPaid
    def feed(self):
        self.statuses.create(type= DemandStatusType.objects.get(pk=DemandFeed)).save()
    def send(self):
        self.statuses.create(type= DemandStatusType.objects.get(pk=DemandSent)).save()
    def close(self):
        self.statuses.create(type= DemandStatusType.objects.get(pk=DemandClosed)).save()
    def finish(self):
        self.statuses.create(type= DemandStatusType.objects.get(pk=DemandFinished)).save()
        self.is_finished = True
        self.save()
    def __unicode__(self):
        return u'דרישה לתשלום לפרוייקט %s בגיו חודש %s' % (self.project, '%s-%s' % (self.month, self.month))
    class Meta:
        db_table='Demand'
        ordering = ['project']
        get_latest_by = 'month'
        unique_together = ('project', 'month', 'year')
        permissions = (("list_demand", "Can list demands"),("report_project_month", "Report project month"),
                       ("report_projects_month", "Report projects month"),)

class SignupCancel(models.Model):
    date = models.DateField(ugettext('cancel_date'))
    was_signed = models.BooleanField(ugettext('was_signed_cancel_form'), choices = Boolean)
    was_fee = models.BooleanField(ugettext('was_fee'), choices = Boolean)
    reason = models.TextField(ugettext('cancel_reason'), null=True, blank=True)
    class Meta:
        db_table='SignupCancel'
        
class Signup(models.Model):
    house = models.ForeignKey('House', related_name = 'signups', verbose_name=ugettext('house'))
    date = models.DateField(ugettext('signup_date'))
    clients = models.TextField(ugettext('clients'))
    clients_address = models.TextField(ugettext('clients_address'))
    clients_phone = models.TextField(ugettext('phone'))
    sale_date = models.DateField(ugettext('predicted_sale_date'))
    price = models.IntegerField(ugettext('signup_price'))
    include_lawyer = models.BooleanField(ugettext('include_lawyer'), choices = Boolean)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    cancel = models.OneToOneField('SignupCancel', related_name = 'signup', null=True, editable=False)
       
    class Meta:
        ordering = ['-date']
        db_table = 'Signup'
        verbose_name = ugettext('signup')
        get_latest_by = 'date'

LAWYER_TAX = 1.015

class Tax(models.Model):
    date = models.DateField(ugettext('date'))
    value = models.FloatField(ugettext('value'))
    class Meta:
        db_table = 'Tax'
        get_latest_by = 'date'
        ordering = ['-date']    

class Madad(models.Model):
    date = models.DateField(ugettext('date'))
    value = models.FloatField(ugettext('value'))
    class Meta:
        db_table = 'Madad'
        get_latest_by = 'date'
        ordering = ['-date']

class NHPay(models.Model):
    nhsale = models.ForeignKey('NHSale', editable=False, related_name='pays')
    employee = models.ForeignKey('NHEmployee', editable=False, related_name='nhpays', null=True)
    lawyer = models.ForeignKey('Lawyer', editable=False, related_name='nhpays', null=True)
    amount = models.FloatField(ugettext('amount'))
    class Meta:
        db_table='NHPay'

class Lawyer(Person):
    class Meta:
        db_table='Lawyer'

class NHSaleSide(models.Model):
    name1 = models.CharField(ugettext('name'), max_length=20, null=True, blank=True)
    name2 = models.CharField(ugettext('name'), max_length=20, null=True, blank=True)
    phone1 = models.CharField(ugettext('phone'), max_length=20, null=True, blank=True)
    phone2 = models.CharField(ugettext('phone'), max_length=20, null=True, blank=True)
    employee1 = models.ForeignKey('NHEmployee', verbose_name=ugettext('advisor'), related_name='nhsaleside1s')
    employee2 = models.ForeignKey('NHEmployee', verbose_name=ugettext('advisor'), related_name='nhsaleside2s', 
                                null=True, blank=True)
    director = models.ForeignKey('NHEmployee', verbose_name=ugettext('director'), related_name='nhsaleside_director', 
                                null=True, blank=True)
    lawyer1 = models.ForeignKey('Lawyer', verbose_name=ugettext('lawyer'), related_name='nhsaleside1s', 
                                null=True, blank=True)
    lawyer2 = models.ForeignKey('Lawyer', verbose_name=ugettext('lawyer'), related_name='nhsaleside2s', 
                                null=True, blank=True)
    signed_commission = models.FloatField(ugettext('signed_commission'))
    actual_commission = models.FloatField(ugettext('actual_commission'))
    voucher_num = models.IntegerField(ugettext('voucher_num'))
    voucher_date = models.DateField(ugettext('voucher_date'))
    temp_receipt_num = models.IntegerField(ugettext('temp_receipt_num'))
    invoices = models.ManyToManyField('Invoice', null=True, editable=False)
    payments = models.ManyToManyField('Payment', null=True, editable=False)
    remarks = models.TextField(ugettext('remarks'))
    class Meta:
        db_table = 'NHSaleSide'

class NHSale(models.Model):
    nhbranch = models.ForeignKey('NHBranch', verbose_name=ugettext('nhbranch'))
    side1 = models.ForeignKey('NHSaleSide', related_name='nhsaleside1s')
    side2 = models.ForeignKey('NHSaleSide', related_name='nhsaleside2s')
    
    address = models.CharField(ugettext('address'), max_length=50)
    hood = models.CharField(ugettext('hood'), max_length=50)
    rooms = models.PositiveSmallIntegerField(ugettext('rooms'))
    floor = models.PositiveSmallIntegerField(ugettext('floor'))
    type = models.ForeignKey('HouseType', verbose_name = ugettext('house_type'))
    
    price = models.FloatField(ugettext('price'))
    remarks = models.TextField(ugettext('remarks'))
        
    class Meta:
        db_table='NHSale'

class SaleMod(models.Model):
    sale = models.OneToOneField('Sale', unique=True, editable=False, related_name='%(class)s')
    date = models.DateField(ugettext('date'))
    remarks = models.TextField(ugettext('remarks'), null=True)
    def get_absolute_url(self):
        return '/%s/%s' % (self.__class__.__name__.lower(), self.id)
    class Meta:
        abstract = True

class SalePriceMod(SaleMod):
    old_price = models.IntegerField()
    @property
    def current_price(self):
        return self.sale.price
    class Meta:
        db_table = 'SalePriceMod'

class SaleHouseMod(SaleMod):
    old_house = models.ForeignKey('House')
    @property
    def old_building(self):
        return self.old_house.building
    @property
    def current_building(self):
        return self.current_house.building
    @property
    def current_house(self):
        return self.sale.house
    class Meta:
        db_table = 'SaleHouseMod'

class SalePre(SaleMod):
    employee_pay = models.DateField(ugettext('employee_pay'), null=True)
    def save(self, *args, **kw):
        SaleMod.save(self, *args, **kw)
        self.sale.employee_pay = self.employee_pay
        self.sale.save()
    class Meta:
        db_table = 'SalePre'

class SaleReject(SaleMod):
    to_month = models.DateField(ugettext('reject_month'), null=True)
    employee_pay = models.DateField(ugettext('employee_pay'), null=True)
    def save(self, *args, **kw):
        SaleMod.save(self, args, kw)
        self.sale.employee_pay = self.employee_pay
        self.sale.contractor_pay = self.to_month
        self.sale.save()
    class Meta:
        db_table = 'SaleReject'
        
class SaleCancel(SaleMod):
    fee = models.PositiveIntegerField(ugettext('fee'))
    def save(self, *args, **kw):
        models.Model.save(self, *args, **kw)
        d = self.sale.demand
        d.fee = self.fee
        d.fee_type = u"ביטול מכירה מס' %s" % self.sale.id
        d.save()
    class Meta:
        db_table = 'SaleCancel'
        
class Sale(models.Model):
    demand = models.ForeignKey('Demand', related_name='sales', editable=False)
    house = models.ForeignKey('House', related_name = 'sales', verbose_name=ugettext('house'))
    employee = models.ForeignKey('Employee', related_name = 'sales', verbose_name=ugettext('employee'),
                                 null=True, blank=True)
    sale_date = models.DateField(ugettext('sale_date'))
    price = models.IntegerField(ugettext('sale_price'))
    company_price = models.IntegerField(ugettext('company_price'), null=True, blank=True)
    price_include_lawyer = models.BooleanField(ugettext('price_include_lawyer'), choices = Boolean)
    price_no_lawyer = models.IntegerField(ugettext('sale_price_no_lawyer'))
    clients = models.TextField(ugettext('clients'))
    clients_phone = models.CharField(ugettext('phone'), max_length = 10)
    pc_base = models.FloatField(editable=False, null=True)
    pb_dsp = models.FloatField(editable=False, null=True)
    c_final = models.FloatField(editable=False, null=True)
    price_final = models.IntegerField(editable=False, null=True)
    employee_pay = models.DateField(ugettext('employee_paid'), editable=False)
    contractor_pay = models.DateField(ugettext('contractor_paid'), editable=False)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    contract_num = models.CharField(ugettext('so_contact_num'), max_length=10, null=True, blank=True)    
    include_tax = models.BooleanField(ugettext('include_tax'), choices=Boolean, default=1)
    discount = models.FloatField(ugettext('given_discount'), null=True, blank=True)
    allowed_discount = models.FloatField(ugettext('allowed_discount'), null=True, blank=True)
    @property
    def pc_base_worth(self):
        return self.pc_base * self.price_final / 100
    @property
    def pb_dsp_worth(self):
        return self.pb_dsp * self.price_final / 100
    @property
    def c_final_worth(self):
        return self.c_final * self.price_final / 100
    def project_price(self):
        c = self.house.building.project.commissions
        if c.include_lawyer == None:
            price = self.price
        elif c.include_lawyer == True:
            price = self.price_include_lawyer and self.price or self.price * LAWYER_TAX
        elif c.include_lawyer == False:
            price = self.price_no_lawyer
        TAX = Tax.objects.filter(date__month__lte=self.demand.month,
                                 date__year__lte=self.demand.year).latest().value / 100 + 1
        if c.include_tax:
            price = self.include_tax and price or price * TAX
        else:
            price = self.include_tax and price / TAX or price
        return price
    def employee_price(self):
        et = self.employee.employment_terms
        if et.include_lawyer:
            price = self.price_include_lawyer and self.price or self.price * LAWYER_TAX
        else:
            price = self.price_no_lawyer
        TAX = Tax.objects.filter(date__month__lte=self.demand.month,
                                 date__year__lte=self.demand.year).latest().value / 100 + 1
        if et.include_tax:
            price = self.include_tax and price or price * TAX
        else:
            price = self.include_tax and price / TAX or price
        return price
    def save(self, *args, **kw):
        d = date(self.demand.year, self.demand.month, 1)
        if not self.employee_pay:
            self.employee_pay = d
        if not self.contractor_pay:
            self.contractor_pay = d
        models.Model.save(self, args, kw)
    @property
    def is_fixed(self):
        return self.salehousemod or self.salepricemod or self.salepre or self.salereject
    @property
    def is_ep_ok(self):
        return self.employee_pay.year == self.demand.year and self.employee_pay.month == self.demand.month 
    @property
    def is_cp_ok(self):
        return self.contractor_pay.year == self.demand.year and self.contractor_pay.month == self.demand.month 
    def __unicode__(self):
        return u'בניין %s דירה %s ל%s' % (self.house.building.num, self.house.num, self.clients)
    class Meta:
        ordering = ['sale_date']
        db_table = 'Sale'
        
class Account(models.Model):
    num = models.IntegerField(ugettext('account_num'), unique=True)
    bank = models.CharField(ugettext('bank'), max_length=20)
    branch = models.CharField(ugettext('branch'), max_length=20)
    branch_num = models.SmallIntegerField(ugettext('branch_num'))
    payee = models.CharField(ugettext('payee'), max_length=20)
    class Meta:
        db_table='Account'
        
class CheckBase(models.Model):
    num = models.IntegerField(ugettext('check_num'), unique=True)
    issue_date = models.DateField(ugettext('issue_date'))
    amount = models.IntegerField(ugettext('amount'))
    pay_date = models.DateField(ugettext('payment_date'))
    remarks = models.TextField(ugettext('remarks'))
    class Meta:
        abstract=True

class EmployeeCheck(CheckBase):
    employee = models.ForeignKey('Employee', related_name='checks', verbose_name=ugettext('employee'))
    class Meta:
        db_table = 'EmployeeCheck'

class Check(CheckBase):
    supplier = models.CharField(ugettext('supplier'), max_length=20)
    account = models.ForeignKey('Account', null=True, editable=False)
    invoice_num = models.IntegerField(ugettext('invoice_num'), null=True, blank=True)
    expense_type = models.ForeignKey('ExpenseType', verbose_name=ugettext('expense_type'), blank=True)
    class Meta:
        db_table = 'Check'

class ExpenseType(models.Model):
    name = models.CharField(ugettext('expense_type'), max_length=20, unique=True)
    class Meta:
        db_table = 'ExpenseType'