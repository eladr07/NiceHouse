from django.db import models
from django.utils.translation import ugettext
from datetime import datetime, date
from django.contrib.auth.models import User
from templatetags.management_extras import *
from django.db.models.signals import pre_save
from decimal import InvalidOperation
from django.db.backends.dummy.base import IntegrityError

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

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
    employee = models.ForeignKey('EmployeeBase', related_name='attachments', editable=False, null=True)
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
        
class ReminderStatusType(models.Model):
    Added, Done, Deleted = 1,2,3
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
        self.statuses.create(type = ReminderStatusType.objects.get(pk = ReminderStatusType.Done)).save()
    def delete(self):
        self.statuses.create(type = ReminderStatusType.objects.get(pk = ReminderStatusType.Deleted)).save()
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
    def archive(self):
        return self.exclude(end_date=None)

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
    
    def is_zilber(self):
        return self.commissions.c_zilber != None
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
                not in (ReminderStatusType.Deleted,ReminderStatusType.Done)]
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
      
class PricelistType(models.Model):
    Company, Doh0 = 1, 2
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
        if s.count() > 1:
            raise IntegrityError('More than 1 active signup for house %s' % self.id)
        return s.count() > 0 and s[0] or None 
    def get_sale(self):
        s = self.sales.filter(salecancel=None)
        if s.count() > 1:
            return s
        elif s.count() == 1:
            return s[0]
        return None
    def save(self, *args, **kw):
        if len(self.num) < 5:#patch to make house ordering work. because it is char field, '2' > '19'
            self.num = self.num.ljust(5, ' ')
        models.Model.save(self, *args, **kw)
    def __unicode__(self):
        return unicode(self.num)
    class Meta:
        unique_together = ('building', 'num')
        ordering = ['num']
        db_table = 'House'

class BuildingType(models.Model):
    Cottage = 3
    name = models.CharField(max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table = 'BuildingType'

class HouseType(models.Model):
    Cottage = 2
    name = models.CharField(max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table = 'HouseType'

class HireType(models.Model):
    SelfEmployed, Salaried, DailySalaried = 1,2,3
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

class RankType(models.Model):
    RegionalSaleManager = 8
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
    include_registration = models.NullBooleanField(ugettext('include_registration'))
    include_guarantee = models.NullBooleanField(ugettext('include_guarantee'))
    settle_date = models.DateField(ugettext('settle_date'), null=True, blank=True)
    allowed_discount = models.FloatField(ugettext('allowed_discount'), default=0)
    is_permit = models.NullBooleanField(ugettext('is_permit'))
    permit_date = models.DateField(ugettext('permit_date'), null=True, blank=True)
    lawyer_fee = models.FloatField(ugettext('lawyer_fee'), default=0)
    register_amount = models.FloatField(ugettext('register_amount'), default=0)
    guarantee_amount = models.FloatField(ugettext('guarantee_amount'), default=0)
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
        return self.type.id == BuildingType.Cottage
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
        permissions = (('building_clients', 'Building Clients'), ('building_clients_pdf', 'Building Clients PDF'))
        
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

class EmployeeBase(Person):
    pid = models.PositiveIntegerField(ugettext('pid'), unique=True)
    birth_date = models.DateField(ugettext('birth_date'))
    home_phone = models.CharField(ugettext('home phone'), max_length=10)
    mate_phone = models.CharField(ugettext('mate phone'), max_length=10, null=True, blank=True)
    family_state = models.PositiveIntegerField(ugettext('family state'), choices = Family_State_Types)
    child_num = models.PositiveIntegerField(ugettext('child num'), null=True, blank=True)
    work_start = models.DateField(ugettext('work start'))
    work_end = models.DateField(ugettext('work end'), null=True, blank=True)
    
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)    
    reminders = models.ManyToManyField('Reminder', null=True, editable=False)
    account = models.OneToOneField('Account', related_name='%(class)s',editable=False, null=True, blank=True)
    employment_terms = models.OneToOneField('EmploymentTerms',editable=False, related_name='%(class)s', null=True, blank=True)
        
    class Meta:
        db_table='EmployeeBase'

class Employee(EmployeeBase):
    rank = models.ForeignKey('RankType', verbose_name=ugettext('rank'))
    projects = models.ManyToManyField('Project', verbose_name=ugettext('projects'), related_name='employees', 
                                      null=True, blank=True, editable=False)
    main_project = models.ForeignKey('Project', verbose_name=ugettext('main_project'), null=True, blank=True)
    objects = EmployeeManager()
    
    def get_open_reminders(self):
        return [r for r in self.reminders.all() if r.statuses.latest().type.id 
                not in (ReminderStatusType.Deleted,ReminderStatusType.Done)]
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

class NHSaleFilter(models.Model):
    His, NotHis, All = 1,2,3
    name = models.CharField(max_length = 20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table = 'NHSaleFilter'

class NHCBase(models.Model):
    min = models.PositiveIntegerField(ugettext('min_commission'), default=0)
    precentage = models.FloatField(ugettext('precentage'))
    filter = models.ForeignKey('NHSaleFilter', verbose_name=ugettext('filter'))
    def calc(self, nhmonth):
        amount = 0
        es = NHEmployeeSalary.objects.get(nhemployee=self.nhemployee, year= nhmonth.year,
                                          month = nhmonth.month)
        scds = []
        if self.filter.id == NHSaleFilter.His or self.filter.id == NHSaleFilter.All:
            for nhss in NHSaleSide.objects.filter(employee1=self.nhemployee):
                x = nhss.employee1_pay * 2.5 * self.precentage / 100
                amount += x
                scds.append(NHSaleCommissionDetail(nhemployeesalary=es, commission='nhcbase',amount=x,
                                                   nhsaleside=nhss, income=nhss.employee1_pay,
                                                   precentage = self.precentage * 2.5))
            for nhss in NHSaleSide.objects.filter(employee2=self.nhemployee):
                x = nhss.employee2_pay * 2.5 * self.precentage / 100
                amount += x
                scds.append(NHSaleCommissionDetail(nhemployeesalary=es, commission='nhcbase',amount=x,
                                                   nhsaleside=nhss, income=nhss.employee2_pay,
                                                   precentage = self.precentage * 2.5))
        if self.filter.id == NHSaleFilter.NotHis or self.filter.id == NHSaleFilter.All:
            for nhe in nhmonth.nhbranch.nhemployees.exclude(id = self.nhemployee.id):
                for nhss in NHSaleSide.objects.filter(employee1=nhe).exclude(employee2=self.nhemployee):
                    x = nhss.employee1_pay * 2.5 * self.precentage / 100
                    amount += x
                    scds.append(NHSaleCommissionDetail(nhemployeesalary=es, commission='nhcbase',amount=x,
                                                       nhsaleside=nhss, income=nhss.employee1_pay,
                                                       precentage = self.precentage * 2.5))
                for nhss in NHSaleSide.objects.filter(employee2=nhe).exclude(employee1=self.nhemployee):
                    x = nhss.employee2_pay * 2.5 * self.precentage / 100
                    amount += x 
                    scds.append(NHSaleCommissionDetail(nhemployeesalary=es, commission='nhcbase',amount=x,
                                                       nhsaleside=nhss, income=nhss.employee2_pay,
                                                       precentage = self.precentage * 2.5))
        if amount >= self.min:
            for scd in scds:
                scd.save()
            return amount
        else:
            NHSaleCommissionDetail.objects.create(nhemployeesalary=es,commission='nhcbase_min', amount=self.min)
            return self.min
    class Meta:
        db_table = 'NHCBase'

class NHCBranchIncome(models.Model):
    filter = models.ForeignKey('NHSaleFilter', verbose_name=ugettext('filter'))
    if_income = models.IntegerField(ugettext('if_branch_income'))
    then_precentage = models.FloatField(ugettext('then_precentage'))
    else_amount = models.IntegerField(ugettext('else_amount'))
    def calc(self, nhmonth):
        amount = 0
        es = NHEmployeeSalary.objects.get(nhemployee=self.nhemployee, year= nhmonth.year,
                                          month = nhmonth.month)
        scds = []
        if self.filter.id == NHSaleFilter.His or self.filter.id == NHSaleFilter.All:
            for nhss in NHSaleSide.objects.filter(employee1=self.nhemployee):
                amount += nhss.employee1_pay
                scds.append(NHSaleCommissionDetail(nhemployeesalary=es,nhsaleside=nhss,
                                                   commission='nhcbranchincome',
                                                   amount=nhss.employee1_pay * 2.5 * self.then_precentage/100,
                                                   precentage = self.then_precentage * 2.5, income=nhss.employee1_pay))
            for nhss in NHSaleSide.objects.filter(employee2=self.nhemployee):
                amount += nhss.employee2_pay
                scds.append(NHSaleCommissionDetail(nhemployeesalary=es,nhsaleside=nhss,
                                                   commission='nhcbranchincome',
                                                   amount=nhss.employee2_pay * 2.5 * self.then_precentage/100,
                                                   precentage = self.then_precentage * 2.5, income=nhss.employee2_pay))
        if self.filter.id == NHSaleFilter.NotHis or self.filter.id == NHSaleFilter.All:
            for nhe in nhmonth.nhbranch.nhemployees.exclude(id = self.nhemployee.id):
                for nhss in NHSaleSide.objects.filter(employee1=nhe).exclude(employee2=self.nhemployee):
                    amount += nhss.employee1_pay
                    scds.append(NHSaleCommissionDetail(nhemployeesalary=es,nhsaleside=nhss,
                                                       commission='nhcbranchincome',
                                                       amount=nhss.employee1_pay * 2.5 * self.then_precentage/100,
                                                       precentage = self.then_precentage * 2.5, income=nhss.employee1_pay))
                for nhss in NHSaleSide.objects.filter(employee2=nhe).exclude(employee1=self.nhemployee):
                    amount += nhss.employee2_pay
                    scds.append(NHSaleCommissionDetail(nhemployeesalary=es,nhsaleside=nhss,
                                                       commission='nhcbranchincome',
                                                       amount=nhss.employee2_pay * 2.5 * self.then_precentage/100,
                                                       precentage = self.then_precentage * 2.5, income=nhss.employee2_pay))
        if amount > self.if_income:
            for scd in scds:
                scd.save()
            return self.then_precentage * amount / 100
        else:
            NHSaleCommissionDetail.objects.create(nhemployeesalary=es, commission='nhcbranchincome_min',
                                                  amount=self.else_amount)
            return self.else_amount
    class Meta:
        db_table = 'NHCBranchIncome'

class NHBranch(models.Model):
    name = models.CharField(ugettext('name'), max_length=30, unique=True)
    manager = models.ForeignKey('NHEmployee', null=True, blank=True,
                                related_name='branch_manager',
                                verbose_name=ugettext('nhbranch_manager'))
    address = models.CharField(ugettext('address'), max_length=40, null=True, blank=True)
    phone = models.CharField(ugettext('phone'), max_length=15, null=True, blank=True)
    mail = models.EmailField(ugettext('mail'), null=True, blank=True)
    fax = models.CharField(ugettext('fax'), max_length=15, null=True, blank=True);
    url = models.URLField(ugettext('url'), null=True, blank=True)
    @property
    def prefix(self):
        return self.name.replace(u'נייס האוס ','') \
               [0]
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table='NHBranch'
        permissions = (('nhbranch_1', 'NHBranch Shoham'),('nhbranch_2', 'NHBranch Modiin'),('nhbranch_3', 'NHBranch Nes Ziona'))
    
class NHEmployee(EmployeeBase):
    nhbranch = models.ForeignKey('NHBranch', verbose_name=ugettext('nhbranch'), related_name='nhemployees')
    nhcbase = models.OneToOneField('NHCBase', editable=False, null=True, related_name='nhemployee')
    nhcbranchincome = models.OneToOneField('NHCBranchIncome', editable=False, null=True, related_name='nhemployee')
    objects = EmployeeManager()
    
    def get_open_reminders(self):
        return [r for r in self.reminders.all() if r.statuses.latest().type.id 
                not in (ReminderStatusType.Deleted,ReminderStatusType.Done)]
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

class NHSaleCommissionDetail(models.Model):
    nhemployeesalary = models.ForeignKey('NHEmployeeSalary')
    nhsaleside = models.ForeignKey('NHSaleSide', null=True)
    commission = models.CharField(max_length=30)
    income = models.IntegerField(null=True)
    precentage = models.FloatField(null=True)
    amount = models.IntegerField()
    class Meta:
        db_table = 'NHSaleCommissionDetail'
        
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
    employee = models.ForeignKey('EmployeeBase', related_name = 'loans', 
                                 verbose_name=ugettext('employee'), null=True)
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
    employee = models.ForeignKey('EmployeeBase', related_name='loan_pays', 
                                 verbose_name=ugettext('employee'), null=True)
    date = models.DateField(ugettext('date'))
    amount = models.FloatField(ugettext('amount'))
    remarks = models.TextField(ugettext('remarks'), blank=True, null=True)
    class Meta:
        db_table = 'LoanPay'

class SaleCommissionDetail(models.Model):
    employee_salary = models.ForeignKey('EmployeeSalary', related_name='commission_details',
                                        null=True)
    commission = models.CharField(max_length=30)
    value = models.FloatField(null=True)
    sale = models.ForeignKey('Sale', null=True, related_name='commission_details')
    class Meta:
        db_table = 'SaleCommissionDetail'
        ordering=['commission','value']

class EmployeeSalaryBaseStatusType(models.Model):
    Approved, SentBookkeeping, SentChecks = 1, 2, 3
    name = models.CharField(max_length=20)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table='EmployeeSalaryBaseStatusType'
        
class EmployeeSalaryBaseStatus(models.Model):
    employeesalarybase = models.ForeignKey('EmployeeSalaryBase', related_name='statuses')
    type = models.ForeignKey('EmployeeSalaryBaseStatusType')
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='EmployeeSalaryBaseStatus'
        ordering = ['date']
        get_latest_by = 'date'

class SalaryExpenses(models.Model):
    income_tax = models.FloatField(ugettext('income_tax'))
    national_insurance = models.FloatField(ugettext('national_insurance'))
    health = models.FloatField(ugettext('health'))
    pension_insurance = models.FloatField(ugettext('pension_insurance'))
    employer_national_insurance = models.FloatField(ugettext('employer_national_insurance'))
    employer_benefit = models.FloatField(ugettext('employer_benefit'))
    compensation_allocation = models.FloatField(ugettext('compensation_allocation'))
    vacation = models.FloatField(ugettext('vacation'))
    convalescence_pay = models.FloatField(ugettext('convalescence_pay'))
    @property
    def bruto(self):
        return self.salary.total_amount + self.income_tax + self.national_insurance + self.health + self.pension_insurance
    @property
    def neto(self):
        return self.salary.total_amount - self.income_tax - self.national_insurance - self.health - self.pension_insurance
    @property
    def bruto_employer_expense(self):
        return self.bruto + self.employer_benefit + self.employer_national_insurance + self.compensation_allocation \
                + self.vacation + self.convalescence_pay
    class Meta:
        db_table = 'SalaryExpenses'
        
class EmployeeSalaryBase(models.Model):
    expenses = models.OneToOneField('SalaryExpenses', related_name='salary', editable=False, null=True)
    month = models.PositiveSmallIntegerField(ugettext('month'), editable=False, choices=((i,i) for i in range(1,13)))
    year = models.PositiveSmallIntegerField(ugettext('year'), editable=False, choices=((i,i) for i in range(datetime.now().year - 10,
                                                                                             datetime.now().year + 10)))
    base = models.FloatField(ugettext('salary_base'), null=True)
    commissions = models.FloatField(ugettext('commissions'), editable=False, null=True)
    safety_net = models.FloatField(ugettext('safety_net'), null=True, blank=True)
    var_pay = models.FloatField(ugettext('var_pay'), null=True, blank=True)
    var_pay_type = models.CharField(ugettext('var_pay_type'), max_length=20, null=True, blank=True)
    refund = models.FloatField(ugettext('refund'), null=True, blank=True)
    refund_type = models.CharField(ugettext('refund_type'), max_length=20, null=True, blank=True)
    deduction = models.FloatField(ugettext('deduction'), null=True, blank=True)
    deduction_type = models.CharField(ugettext('deduction_type'), max_length=20, null=True, blank=True)
    remarks = models.TextField(ugettext('remarks'),null=True, blank=True)
    
    def approve(self):
        self.statuses.create(type = EmployeeSalaryBaseStatusType.objects.get(pk = EmployeeSalaryBaseStatusType.Approved)).save()
    def send_to_checks(self):
        self.statuses.create(type = EmployeeSalaryBaseStatusType.objects.get(pk = EmployeeSalaryBaseStatusType.SentChecks)).save()
    def send_to_bookkeeping(self):
        self.statuses.create(type = EmployeeSalaryBaseStatusType.objects.get(pk = EmployeeSalaryBaseStatusType.SentBookkeeping)).save()
    @property
    def approved_date(self):
        q = self.statuses.filter(type__id = EmployeeSalaryBaseStatusType.Approved)
        return q.count() > 0 and q.latest().date or None
    @property
    def sent_to_bookkeeping_date(self):
        q = self.statuses.filter(type__id = EmployeeSalaryBaseStatusType.SentBookkeeping)
        return q.count() > 0 and q.latest().date or None
    @property
    def sent_to_checks_date(self):
        q = self.statuses.filter(type__id = EmployeeSalaryBaseStatusType.SentChecks)
        return q.count() > 0 and q.latest().date or None
    @property
    def loan_pay(self):
        amount = 0
        for lp in self.get_employee().loan_pays.filter(date__year = self.year, date__month = self.month):
            amount += lp.amount
        return amount
    def get_employee(self):
        if hasattr(self, 'employeesalary'):
            return self.employeesalary.employee
        elif hasattr(self, 'nhemployeesalary'):
            return self.nhemployeesalary.nhemployee
    class Meta:
        db_table = 'EmployeeSalaryBase'

class NHEmployeeSalary(EmployeeSalaryBase):
    nhemployee = models.ForeignKey('NHEmployee', verbose_name=ugettext('nhemployee'), related_name='salaries')
    admin_commission = models.IntegerField(editable=False, null=True)
    @property
    def total_amount(self):
        terms = self.employee.employment_terms
        if not terms.salary_net and terms.hire_type.id == HireType.Salaried:
            return self.expenses and self.expenses.neto or None
        return self.base + self.commissions + self.admin_commission + (self.var_pay or 0) + (self.safety_net or 0) - (self.deduction or 0)
    @property
    def check_amount(self):
        return self.total_amount != None and (self.total_amount - self.loan_pay) or None
    def calculate(self):
        for scd in NHSaleCommissionDetail.objects.filter(nhemployeesalary = self):
            scd.delete()
        self.admin_commission, self.commissions, self.base = 0, 0, 0
        for nhss in NHSaleSide.objects.filter(employee1=self.nhemployee, nhsale__nhmonth__year__exact = self.year,
                                              nhsale__nhmonth__month__exact = self.month):
            self.commissions += nhss.employee1_pay
            NHSaleCommissionDetail.objects.create(nhemployeesalary=self, nhsaleside=nhss,
                                                  commission='base', amount = nhss.employee1_pay,
                                                  precentage = nhss.employee1_commission,
                                                  income = nhss.net_income)
        for nhss in NHSaleSide.objects.filter(employee2=self.nhemployee, nhsale__nhmonth__year__exact = self.year,
                                              nhsale__nhmonth__month__exact = self.month):
            self.commissions += (nhss.employee2_pay or 0)
            NHSaleCommissionDetail.objects.create(nhemployeesalary=self, nhsaleside=nhss,
                                                  commission='base', amount = nhss.employee2_pay or 0,
                                                  precentage = nhss.employee2_commission,
                                                  income = nhss.net_income)
        if self.nhemployee.nhbranch:
            try:
                nhm = NHMonth.objects.get(nhbranch = self.nhemployee.nhbranch, year = self.year,
                                          month = self.month)
            except NHMonth.DoesNotExist:
                return
            self.__calc__(nhm)
        elif self.nhemployee.branch_manager.count() > 0:
            for nhbranch in self.nhemployee.branch_manager.all():
                nhm = NHMonth.objects.get(nhbrnach = nhbranch, year = self.year, month = self.month)
                self.__calc__(nhm)
    def __calc__(self, nhmonth):
        if self.nhemployee.nhcbase:
            self.admin_commission += self.nhemployee.nhcbase.calc(nhmonth)
        if self.nhemployee.nhcbranchincome:
            self.admin_commission += self.nhemployee.nhcbranchincome.calc(nhmonth)
    class Meta:
        db_table='NHEmployeeSalary'
        
class EmployeeSalary(EmployeeSalaryBase):
    employee = models.ForeignKey('Employee', verbose_name=ugettext('employee'), related_name='salaries')
    def __init__(self, *args, **kw):
        super(EmployeeSalary, self).__init__(*args, **kw)
        self.project_commission = {}
    @property
    def sales(self):
        sales = {}
        if self.employee.rank.id != RankType.RegionalSaleManager:
            for s in self.employee.sales.filter(employee_pay__year = self.year, employee_pay__month = self.month):
                if not sales.has_key(s.house.building.project): sales[s.house.building.project]= []
                sales[s.house.building.project].append(s)
            for p in self.employee.projects.all():
                if not sales.has_key(p): sales[p]= []                    
                sales[p].extend(list(Sale.objects.filter(house__building__project = p, employee_pay__month = self.month,
                                                         employee_pay__year = self.year, employee = None)))
        else:
            for p in self.employee.projects.all():
                sales[p] = list(Sale.objects.filter(house__building__project = p,
                                                    employee_pay__month = self.month,
                                                    employee_pay__year = self.year))
        return sales
    @property
    def sales_count(self):
        i=0
        for v in self.sales.values():
            if v:
                i += len(v)
        return i
    @property
    def total_amount(self):
        terms = self.employee.employment_terms
        if not terms.salary_net and terms.hire_type.id == HireType.Salaried:
            return self.expenses and self.expenses.neto or None
        return self.base + self.commissions + (self.var_pay or 0) + (self.safety_net or 0) - (self.deduction or 0)
    @property
    def check_amount(self):
        return self.total_amount != None and (self.total_amount - self.loan_pay) or None
    def project_salary(self):
        res = {}
        if not len(self.project_commission): return res
        ''' TODO: FIX AFTER SALARY EXPENSES ARE FEED '''
        bruto_amount = self.base + self.commissions + (self.var_pay or 0) + (self.safety_net or 0) - (self.deduction or 0)
        if self.employee.main_project:
            for project, commission in self.project_commission.items():
                res[project] = commission + (self.employee.main_project.id == project.id and bruto_amount-self.commissions or 0)
        else:
            base = (bruto_amount-self.commissions) / self.employee.projects.count() 
            for project, commission in self.project_commission.items():
                res[project] = commission + base
        return res 
    def calculate(self):
        #clean any sale commission details associated with this salary
        for scd in SaleCommissionDetail.objects.filter(employee_salary=self):
            scd.delete()
        terms = self.employee.employment_terms
        self.commissions, self.base = 0, terms and terms.salary_base or 0
        for project, sales in self.sales.items():
            q = self.employee.commissions.filter(project__id = project.id)
            if q.count() == 0: continue
            epc = q[0]
            if not epc.is_active(date(self.year, self.month,1)): continue
            if not sales or len(sales) == 0:
                self.project_commission[epc.project] = 0
                continue
            self.project_commission[epc.project] = epc.calc(sales, self)
            self.commissions += self.project_commission[epc.project]
            for s in sales:
                s.employee_paid = True
                s.save() 
    def get_absolute_url(self):
        return '/employeesalaries/%s' % self.id
    class Meta:
        db_table = 'EmployeeSalary'

class EPCommission(models.Model):
    employee = models.ForeignKey('Employee', related_name='commissions')
    project = models.ForeignKey('Project', related_name= 'epcommission')
    start_date = models.DateField(ugettext('start_date'))
    end_date = models.DateField(ugettext('end_date'), null=True, blank=True)
    c_var = models.OneToOneField('CVar', related_name= 'epcommission', null=True, editable=False)
    c_var_precentage = models.OneToOneField('CVarPrecentage', related_name= 'epcommission', null=True, editable=False)
    c_by_price = models.OneToOneField('CByPrice', related_name= 'epcommission', null= True, editable=False)
    b_house_type = models.OneToOneField('BHouseType', related_name= 'epcommission', null=True, editable=False)
    b_discount_save = models.OneToOneField('BDiscountSave', related_name= 'epcommission', null=True, editable=False)
    b_sale_rate = models.OneToOneField('BSaleRate', related_name= 'epcommission', null=True, editable=False)
    def is_active(self, date=date.today()):
        if not self.end_date:
            return True
        if date > self.start_date and date < self.end_date:
            return True
        return False 
    def calc(self, sales, salary):
        dic = {}# key: sale value: commission amount for sale
        for s in sales:
            for scd in s.commission_details.filter(employee_salary=salary):
                scd.delete()
        for c in ['c_var', 'c_by_price', 'b_house_type', 'b_discount_save']:
            if getattr(self,c) == None:
                continue
            amounts = getattr(self,c).calc(sales)
            for s in amounts:
                if amounts[s] == 0:
                    continue
                s.commission_details.create(employee_salary = salary, value = amounts[s], commission = c)
                dic[s] = dic.has_key(s) and dic[s] + amounts[s] or amounts[s]
        for c in ['c_var_precentage']:
            if getattr(self,c) == None:
                continue
            precentages = getattr(self,c).calc(sales)
            for s in precentages:
                if precentages[s] == 0:
                    continue
                amount = precentages[s] * s.employee_price() / 100
                s.commission_details.create(employee_salary = salary, value = amount, commission = c)
                dic[s] = dic.has_key(s) and dic[s] + amount or amount
        total_amount = 0
        for s in dic:
            total_amount = total_amount + dic[s]
        for c in ['b_sale_rate']:
            if getattr(self,c) == None:
                continue
            amount = getattr(self,c).calc(sales)
            if amount == 0:
                continue
            total_amount = total_amount + amount
            scd = SaleCommissionDetail(employee_salary = salary, value = amount, commission = c)
            scd.save()
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
            c = self.get_amount(len(sales)).amount
            for s in sales:
                dic[s] = c
        else:
            i=0
            for s in sales:
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
        if self.is_retro and len(sales) >= self.start_retro:
            c = self.get_precentage(len(sales)).precentage
            for s in sales:
                dic[s] = c
        else:
            i=0
            for s in sales:
                i += 1
                c = self.get_precentage(i).precentage
                dic[s] = c
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
    first_precentage = models.FloatField(ugettext('commission precentage'))
    step = models.FloatField(ugettext('cvf step'))
    last_count = models.PositiveSmallIntegerField(ugettext('cvf last count'), null=True, blank=True)
    last_precentage = models.FloatField(ugettext('commission precentage'), null=True, blank=True)
    def calc(self, sales):
        if len(sales) == 0: return {}
        houses_remaning = len(sales)
        for h in sales[0].house.building.project.houses():
            if h.get_sale() == None and not h.is_sold:
                houses_remaning += 1
        dic = {}
        if self.is_retro and len(sales) > self.first_count:
            precentage = self.first_precentage + self.step * (len(sales) - self.first_count)
            for s in sales:
                if self.last_count and houses_remaning <= self.last_count:
                    dic[s] = self.last_precentage
                else:
                    dic[s] = precentage
                houses_remaning -= 1
        else:
            for s in sales[:self.first_count]:
                dic[s] = self.first_precentage
            if len(sales) <= self.first_count:
                return dic
            i = self.first_count + 1
            for s in sales[self.first_count+1:]:
                if self.last_count and houses_remaning <= self.last_count:
                    dic[s] = self.last_precentage
                else:
                    dic[s] = self.first_precentage + self.step * (i - self.first_count)
                houses_remaning -= 1
                i += 1
        return dic
    class Meta:
        db_table = 'CVarPrecentageFixed'

class CByPrice(models.Model):
    def calc(self, sales):
        dic = {}
        for s in sales:
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
    Cycle = 4
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
        d = Demand.objects.get(project = self.projectcommission.project, year = month.year, month = month.month)
        if d.var_diff: d.var_diff.delete()
        if d.bonus_diff: d.bonus_diff.delete()
        demand = d
        sales = list(d.get_sales().all())
        while demand != None and demand.zilber_cycle_index() != 1:
            demand = demand.get_previous_demand()
            sales.extend(demand.get_sales().filter(commission_include=True))
        base = self.base + self.b_sale_rate * (len(sales) - 1)
        if base > self.b_sale_rate_max:
            base = self.b_sale_rate_max
        for s in sales:
            for c in ['c_zilber_base', 'final']:
                scd = s.commission_details.get_or_create(commission=c)[0]
                scd.value = s.commission_include and base or 0
                scd.save()
            s.price_final = s.project_price()
            s.save()
            if not s.commission_include:
                continue
            if self.base_madad:
                current_madad = d.get_madad() < self.base_madad and self.base_madad or d.get_madad()
                doh0prices = s.house.versions.filter(type__id = PricelistType.Doh0)
                if doh0prices.count() == 0: continue
                memudad = (((current_madad / self.base_madad) - 1) * 0.6 + 1) * doh0prices.latest().price
                scd = s.commission_details.get_or_create(commission='c_zilber_discount')[0]
                scd.value = (s.price - memudad) * self.b_discount
                scd.save()
        prev_adds = 0
        for s in sales:
            if not s.commission_include:
                continue
            q = s.project_commission_details.filter(commission='final')
            last_demand_finish_date = d.get_previous_demand().finish_date
            if q.count() > 0 and last_demand_finish_date:
                pc_base = restore_object(q[0], last_demand_finish_date).value
            else:
                pc_base = s.pc_base
            prev_adds += (base - pc_base) * s.price_final / 100
        if prev_adds:
            d.diffs.create(type=u'משתנה', reason=u'הפרשי קצב מכירות (נספח א)', amount=prev_adds)
        if d.include_zilber_bonus():
            demand, bonus = d, 0
            while demand != None:
                for s in demand.get_sales().filter(commission_include=True):
                    bonus += s.zdb
                if demand.zilber_cycle_index() == 1:
                    break
                demand = demand.get_previous_demand()
            if bonus != 0:
                d.diffs.create(type=u'בונוס', reason=u'בונוס חסכון בהנחה (נספח ב)', amount=bonus)
        d.save()
    class Meta:
        db_table = 'CZilber'

class BDiscountSave(models.Model):
    precentage_bonus = models.PositiveIntegerField(ugettext('precentage_bonus'))
    max_for_bonus = models.FloatField(ugettext('max_bonus'), blank=True, null=True)
    def calc(self, sales):
        dic = {}
        for s in sales:
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
        for s in sales:
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
        for s in sales:
            b = self.bonuses.filter(type = s.house.type)
            dic[s] = b.count() == 1 and b[0].amount or 0
        return dic
    class Meta:
        db_table = 'BHouseType'    
        
class BSaleRate(models.Model):
    def calc(self,sales):
        c = len(sales)
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
    registration_amount = models.PositiveIntegerField(ugettext('registration_amount'), null=True, blank=True)
    include_tax = models.NullBooleanField(ugettext('commission_include_tax'), blank=True, default=True)
    include_lawyer = models.NullBooleanField(ugettext('commission_include_lawyer'), blank=True,
                                             choices = (
                                                        ('','לא משנה'),
                                                        (0, 'לא'),
                                                        (1, 'כן')
                                                        ))
    commission_by_signups = models.BooleanField(ugettext('commission_by_signups'), blank=True)
    max = models.FloatField(ugettext('max_commission'), null=True, blank=True)
    agreement = models.FileField(ugettext('agreement'), upload_to='files', null=True, blank=True)
    remarks = models.TextField(ugettext('commission_remarks'), null=True, blank=True)
    def calc(self, sales, sub=0):
        if sales.count() == 0: return
        demand = sales[0].actual_demand
        if self.commission_by_signups and sub == 0:
            for (m, y) in demand.get_signup_months():
                #get sales that were signed up for specific month, not including future sales.
                subSales = Sale.objects.filter(house__signups__date__year=y,
                                               house__signups__date__month=m,
                                               house__signups__cancel=None,
                                               house__building__project = demand.project,
                                               commission_include=True
                                        ).exclude(contractor_pay__gte = date(demand.month==12 and demand.year+1 or demand.year, 
                                                                             demand.month==12 and 1 or demand.month+1,1))
                self.calc(subSales, 1)
            if demand.bonus_diff: demand.bonus_diff.delete()
            bonus = 0
            for subSales in demand.get_affected_sales().values():
                for s in subSales:
                    if not s.commission_include: continue
                    signup = s.house.get_signup()
                    if not signup: continue
                    #get the finish date when the demand for the month the signup 
                    #were made we use it to find out what was the commission at
                    #that time
                    finish_date = s.actual_demand.finish_date 
                    if not finish_date: continue
                    q = s.project_commission_details.filter(commission='final')
                    if q.count()==0: continue
                    diff = (q[0].value - s.c_final) * s.price_final / 100
                    bonus += int(diff)
            if bonus > 0:
                demand.diffs.create(type=u'בונוס', reason = u'הפרשי עמלה (ניספח א)', amount=bonus)
            return
        if getattr(self, 'c_zilber') != None:
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
                if c in ['c_var_precentage', 'c_var_precentage_fixed'] and self.max and precentages[s] > self.max:
                    precentages[s] = self.max#set base commission to max commission
                dic[s] = dic.has_key(s) and dic[s] + precentages[s] or precentages[s]
                if not details.has_key(s):
                    details[s]={}
                details[s][c] = precentages[s]
        if self.max:
            for s in dic:
                if dic[s] > self.max:
                    dic[s] = self.max
        for s in details:
            for c, v in details[s].items():
                scd = s.commission_details.get_or_create(employee_salary=None, commission=c)[0]
                scd.value = s.commission_include and v or 0
                scd.save()
            scd = s.commission_details.get_or_create(employee_salary=None, commission='final')[0]
            scd.value = s.commission_include and dic[s] or 0
            scd.save()
            s.price_final = s.project_price()
            s.save()

    class Meta:
        db_table = 'ProjectCommission'
  
class Invoice(models.Model):
    num = models.IntegerField(ugettext('invoice_num'), unique=True)
    creation_date = models.DateField(auto_now_add = True)
    date = models.DateField(ugettext('invoice_date'))
    amount = models.IntegerField(ugettext('amount'))
    remarks = models.TextField(ugettext('remarks'), null=True,blank=True)
    def __unicode__(self):
        return u'צק על סך %s ש"ח' % commaise(self.amount)
    class Meta:
        db_table = 'Invoice'
        get_latest_by = 'creation_date'
        ordering = ['creation_date']

class PaymentType(models.Model):
    name = models.CharField(max_length=20)
    def __unicode__(self):
        return unicode(self.name)  
    class Meta:
        db_table = 'PaymentType'

class Payment(models.Model):
    num = models.IntegerField(ugettext('check_num'), unique=True, null=True, blank=True)
    support_num = models.IntegerField(ugettext('support_num'), null=True, blank=True)
    bank = models.CharField(ugettext('bank'), max_length=40)
    branch_num = models.PositiveSmallIntegerField(ugettext('branch_num'))
    payment_type = models.ForeignKey('PaymentType', verbose_name=ugettext('payment_type'))
    payment_date = models.DateField(ugettext('payment_date'))
    creation_date = models.DateField(auto_now_add = True)
    amount = models.IntegerField(ugettext('amount'))
    remarks = models.TextField(ugettext('remarks'), null=True,blank=True)
    def __unicode__(self):
        return u'תשלום על סך %s ש"ח' % commaise(self.amount)
    class Meta:
        db_table = 'Payment'
        get_latest_by = 'creation_date'
        ordering = ['creation_date']

DemandFeed, DemandClosed, DemandSent, DemandFinished = range(1,5)

class DemandStatusType(models.Model):
    name = models.CharField(max_length=20)
    def __unicode__(self):
        return unicode(self.name)  
    class Meta:
        db_table = 'DemandStatusType'

class DemandStatus(models.Model):
    demand = models.ForeignKey('Demand', related_name='statuses')
    date = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey('DemandStatusType')
    def __unicode__(self):
        return u'%s - %s' % (self.type, self.date.strftime('%d/%m/%Y %H:%M'))
    class Meta:
        db_table = 'DemandStatus'
        get_latest_by = 'date'

      
class DemandManager(models.Manager):
    def current(self):
        now = Demand.current_month()
        return self.filter(year = now.year, month = now.month)

class DemandDiff(models.Model):
    demand = models.ForeignKey('Demand', editable=False, related_name='diffs')
    type = models.CharField(ugettext('diff_type'), max_length=30)
    reason = models.CharField(ugettext('diff_reason'), max_length=30, null=True, blank=True)
    amount = models.FloatField(ugettext('amount'))
    def __unicode__(self):
        return u'תוספת מסוג %s על סך %s ש"ח - %s' % (self.type, self.amount, self.reason)
    class Meta:
        db_table = 'DemandDiff'
        unique_together = ('demand','type')

DemandNoInvoice, DemandNoPayment, DemandPaidPlus, DemandPaidMinus, DemandPaid = range(1, 6)
      
class Demand(models.Model):
    project = models.ForeignKey('Project', related_name='demands', verbose_name = ugettext('project'))
    month = models.PositiveSmallIntegerField(ugettext('month'), choices=((i,i) for i in range(1,13)))
    year = models.PositiveSmallIntegerField(ugettext('year'), choices=((i,i) for i in range(datetime.now().year - 10,
                                                                                             datetime.now().year + 10)))
    sale_count = models.PositiveSmallIntegerField(ugettext('sale_count'), default=0)
    remarks = models.TextField(ugettext('remarks'), null=True,blank=True)
    is_finished = models.BooleanField(default=False, editable=False)
    reminders = models.ManyToManyField('Reminder', null=True, editable=False)

    invoices = models.ManyToManyField('Invoice',  related_name = 'demands', 
                                      editable=False, null=True, blank=True)
    payments = models.ManyToManyField('Payment',  related_name = 'demands', 
                                      editable=False, null=True, blank=True)

    objects = DemandManager()
    
    def current_month():
        now = datetime.now()
        if now.day <= 22:
            now = datetime(now.year, now.month == 1 and 12 or now.month - 1, now.day)
        return now
    current_month = Callable(current_month)
    @property
    def fixed_diff(self):
        q = self.diffs.filter(type=u'קבועה')
        return q.count() == 1 and q[0] or None
    @property    
    def var_diff(self):
        q = self.diffs.filter(type=u'משתנה')
        return q.count() == 1 and q[0] or None
    @property    
    def bonus_diff(self):
        q = self.diffs.filter(type=u'בונוס')
        return q.count() == 1 and q[0] or None
    @property   
    def fee_diff(self):
        q = self.diffs.filter(type=u'קיזוז')
        return q.count() == 1 and q[0] or None
    def get_madad(self):
        q = MadadBI.objects.filter(year = self.year, month=self.month)
        return q.count() > 0 and q[0].value or MadadBI.objects.latest().value
    def zilber_cycle_index(self):
        start = self.project.commissions.c_zilber.third_start
        if (start.year == self.year and start.month > self.month) or self.year < start.year:
            return -1
        i = 1
        while start.year != self.year or start.month != self.month:
            start = date(start.month == 12 and start.year + 1 or start.year,
                         start.month == 12 and 1 or start.month + 1, 1)
            i += 1
        return (i % CZilber.Cycle) or CZilber.Cycle
    def get_previous_demand(self):
        try:
            return Demand.objects.get(project = self.project,
                                      year = self.month == 1 and self.year - 1 or self.year,
                                      month = self.month == 1 and 12 or self.month - 1)
        except Demand.DoesNotExist:
            return None
    def get_next_demand(self):
        try:
            return Demand.objects.get(project = self.project,
                                      year = self.month == 12 and self.year + 1 or self.year,
                                      month = self.month == 12 and 1 or self.month + 1)
        except Demand.DoesNotExist:
            return None
    def get_affected_sales(self):
        '''
        get sales from last months, affected by this month's calculation,
        excluding sales from current demand
        '''
        dic = {}
        for m,y in self.get_signup_months():
            dic[(m,y)] = Sale.objects.filter(house__signups__date__year=y,
                                             house__signups__date__month=m,
                                             house__signups__cancel=None,
                                             demand__project__id = self.project.id,
                                             salecancel=None
                        ).exclude(contractor_pay__gte = date(self.year,self.month, 1))
        return dic
    def get_signup_months(self):
        months = {}
        for s in self.get_sales():
            signup = s.house.get_signup()
            if not signup:
                continue
            if not months.has_key((signup.date.month, signup.date.year)):
                months[(signup.date.month, signup.date.year)] = 0
            months[(signup.date.month, signup.date.year)] += 1
        return months
    def include_zilber_bonus(self):
        return self.zilber_cycle_index() == CZilber.Cycle
    def get_absolute_url(self):
        return '/demands/%s' % self.id
    def get_salaries(self):
        s = []
        for e in self.project.employees.all():
            s.append(e.salaries.get(year = self.year, month = self.month))
        return s
    @property
    def was_sent(self):
        return self.statuses.count() == 0 and self.statuses.latest().type.id == DemandSent
    @property
    def finish_date(self):
        f = self.statuses.filter(type__id = DemandFinished)
        return f.count() > 0 and f.latest().date or None
    @property
    def is_fixed(self):
        return self.sales.exclude(salehousemod=None, salepricemod=None,
                                  salepre=None, salereject=None).count() > 0
    @property
    def diff_invoice(self):
        if self.invoices.count() == 0: return self.get_total_amount()
        return self.invoices.latest().amount - self.get_total_amount()
    @property
    def diff_invoice_payment(self):
        if self.invoices.count() == 0 and self.payments.count() == 0: return 0
        if self.invoices.count() == 0:
            return self.payments.latest().amount
        if self.payments.count() == 0:
            return self.invoices.latest().amount
        return self.payments.latest().amount - self.invoices.latest().amount
    def get_open_reminders(self):
        return [r for r in self.reminders.all() if r.statuses.latest().type.id 
                not in (ReminderStatusType.Deleted,ReminderStatusType.Done)]
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
            amount = amount + (s.price_final or 0) 
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
        diffs = 0
        for d in self.diffs.all():
            diffs += d.amount
        return self.get_sales_commission() + diffs
    def get_deleted_sales(self):
        return [s for s in self.sales.filter(is_deleted=True)]
    def diff(self):
        pay = 0
        for p in self.payments.all():
            pay += pay.amount
        if self.invoices.count() > 0:
            return self.invoices.latest().amount - pay
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
        return u'דרישה לתשלום לפרוייקט %s בגיו חודש %s' % (self.project, '%s-%s' % (self.month, self.year))
    class Meta:
        db_table='Demand'
        ordering = ['project','year','month']
        get_latest_by = 'month'
        unique_together = ('project', 'month', 'year')
        permissions = (('list_demand', 'Can list demands'),('demand_pdf', 'Demand PDF'), ('demands_pdf', 'Demands PDF'),
                       ('demand_season', 'Demand Season'), ('demand_followup', 'Demand Followup'), 
                       ('demand_remarks', 'Demand Remarks'), ('demand_sale_count', 'Demand Sale Count'),
                       ('demand_invoices', 'Demand Invoices'), ('demand_payments', 'Demand Payments'),
                       ('season_income', 'Season Income'))

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
    clients_address = models.TextField(ugettext('clients_address'), null=True)
    clients_phone = models.TextField(ugettext('phone'))
    sale_date = models.DateField(ugettext('predicted_sale_date'))
    price = models.IntegerField(ugettext('signup_price'))
    price_include_lawyer = models.BooleanField(ugettext('include_lawyer'), choices = Boolean)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    cancel = models.OneToOneField('SignupCancel', related_name = 'signup', null=True, editable=False)
    def get_absolute_url(self):
        return '/signups/%s' % self.id
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
        verbose_name = ugettext('tax')
                
#Building Input
class MadadBI(models.Model):
    year = models.PositiveSmallIntegerField(ugettext('year'))
    month = models.PositiveSmallIntegerField(ugettext('year'))
    publish_date = models.DateField(ugettext('publish_date'))
    value = models.FloatField(ugettext('value'))
    def diff(self):
        q = MadadBI.objects.filter(year = self.month == 1 and self.year - 1 or self.year,
                                   month = self.month == 1 and 12 or self.month - 1)
        return q.count() == 1 and self.value - q[0].value or 0
    class Meta:
        db_table = 'MadadBI'
        get_latest_by = 'publish_date'
        ordering = ['-publish_date']
        unique_together = ('year', 'month')

#Consumer Prices
class MadadCP(models.Model):
    year = models.PositiveSmallIntegerField(ugettext('year'))
    month = models.PositiveSmallIntegerField(ugettext('year'))
    publish_date = models.DateField(ugettext('publish_date'))
    value = models.FloatField(ugettext('value'))
    def diff(self):
        q = MadadCP.objects.filter(year = self.month == 1 and self.year - 1 or self.year,
                                   month = self.month == 1 and 12 or self.month - 1)
        return q.count() == 1 and (self.value - q[0].value) / (q[0].value / 100) or 0
    class Meta:
        db_table = 'MadadCP'
        get_latest_by = 'publish_date'
        ordering = ['-publish_date']
        unique_together = ('year', 'month')

class NHPay(models.Model):
    nhsaleside = models.ForeignKey('NHSaleSide', editable=False, related_name='pays')
    employee = models.ForeignKey('EmployeeBase', editable=False, related_name='nhpays', 
                                 null=True)
    lawyer = models.ForeignKey('Lawyer', editable=False, related_name='nhpays', 
                               null=True)
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    amount = models.FloatField(ugettext('amount'))
    class Meta:
        db_table='NHPay'

class Lawyer(Person):
    def get_absolute_url(self):
        return '/lawyers/%s' % self.id
    class Meta:
        db_table='Lawyer'

class SaleType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    def __unicode__(self):
        return unicode(self.name)
    class Meta:
        db_table='SaleType'

class NHSaleSide(models.Model):
    nhsale = models.ForeignKey('NHSale', editable=False)
    sale_type = models.ForeignKey('SaleType', verbose_name=ugettext('action_type'))
    name1 = models.CharField(ugettext('name'), max_length=20)
    name2 = models.CharField(ugettext('name'), max_length=20, null=True, blank=True)
    phone1 = models.CharField(ugettext('phone'), max_length=20)
    phone2 = models.CharField(ugettext('phone'), max_length=20, null=True, blank=True)
    address = models.CharField(ugettext('address'), max_length=40)
    employee1 = models.ForeignKey('NHEmployee', verbose_name=ugettext('advisor'), related_name='nhsaleside1s')
    employee1_commission = models.FloatField(ugettext('commission_precent'))
    employee2 = models.ForeignKey('NHEmployee', verbose_name=ugettext('advisor'), related_name='nhsaleside2s', 
                                null=True, blank=True)
    employee2_commission = models.FloatField(ugettext('commission_precent'), 
                                            null=True, blank=True)
    director = models.ForeignKey('EmployeeBase', verbose_name=ugettext('director'), related_name='nhsaleside_director', 
                                null=True, blank=True)    
    director_commission = models.FloatField(ugettext('commission_precent'), 
                                            null=True, blank=True)
    signing_advisor = models.ForeignKey('NHEmployee', verbose_name=ugettext('signing_advisor'), related_name='nhsaleside_signer')
    lawyer1 = models.ForeignKey('Lawyer', verbose_name=ugettext('lawyer'), related_name='nhsaleside1s', 
                                null=True, blank=True)
    lawyer2 = models.ForeignKey('Lawyer', verbose_name=ugettext('lawyer'), related_name='nhsaleside2s', 
                                null=True, blank=True)
    signed_commission = models.FloatField(ugettext('signed_commission'))
    actual_commission = models.FloatField(ugettext('actual_commission'), blank=True)
    income = models.IntegerField(ugettext('return_worth'), blank=True)
    voucher_num = models.IntegerField(ugettext('voucher_num'))
    voucher_date = models.DateField(ugettext('voucher_date'))
    temp_receipt_num = models.IntegerField(ugettext('temp_receipt_num'))
    employee_remarks = models.TextField(ugettext('employee_remarks'), null=True, blank=True)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    invoices = models.ManyToManyField('Invoice', null=True, editable=False)
    payments = models.ManyToManyField('Payment', null=True, editable=False)
    def __init__(self, *args, **kw):
        models.Model.__init__(self, *args, **kw)
        self.include_tax = True
    @property
    def employee1_pay(self):
        if self.employee1_commission == None or self.employee1 == None:
            return None
        amount = self.net_income * self.employee1_commission / 100
        terms = self.employee1.employment_terms
        if not terms: return amount
        nhmonth = self.nhsale.nhmonth
        tax = Tax.objects.filter(date__lte=date(nhmonth.year, nhmonth.month,1)).latest().value / 100 + 1
        if not self.include_tax and terms.hire_type.id == HireType.SelfEmployed:
            amount = amount / tax
        return amount
    @property
    def employee2_pay(self):
        if self.employee2_commission == None or self.employee2 == None:
            return None
        amount = self.net_income * self.employee2_commission / 100
        terms = self.employee2.employment_terms
        if not terms: return amount
        nhmonth = self.nhsale.nhmonth
        tax = Tax.objects.filter(date__lte=date(nhmonth.year, nhmonth.month,1)).latest().value / 100 + 1
        if not self.include_tax and terms.hire_type.id == HireType.SelfEmployed:
            amount = amount / tax
        return amount
    @property
    def director_pay(self):
        if self.director_commission == None or self.director == None:
            return None
        amount =  self.net_income * self.director_commission / 100
        terms = self.director.employment_terms
        if not terms: return amount
        nhmonth = self.nhsale.nhmonth
        tax = Tax.objects.filter(date__lte=date(nhmonth.year, nhmonth.month,1)).latest().value / 100 + 1
        if not self.include_tax and terms.hire_type.id == HireType.SelfEmployed:
            amount = amount / tax
        return amount
    @property
    def lawyers_pay(self):
        amount = 0
        if self.lawyer1:
            for nhp in self.lawyer1.nhpays.all(nhsaleside = self):
                amount += nhp.amount
        if self.lawyer2:
            for nhp in self.lawyer2.nhpays.all(nhsaleside = self):
                amount += nhp.amount
        return amount             
    @property
    def net_income(self):
        return self.income - self.lawyers_pay
    @property
    def all_employee_commission_precentage(self):
        return (self.employee1_commission or 0) + (self.employee2_commission or 0) + (self.director_commission or 0)
    @property
    def all_employee_commission(self):
        return (self.employee1_pay or 0) + (self.employee2_pay or 0) + (self.director_pay or 0)
    def is_employee_related(self, employee):
        return self.employee1 == employee or self.employee2 == employee or self.director == employee
    def get_employee_pay(self, employee):
        if self.employee1 == employee:
            return self.employee1_pay or 0
        if self.employee2 == employee:
            return self.employee2_pay or 0
        if self.director == employee:
            return self.director_pay or 0
        return 0
    def save(self,*args, **kw):
        if not self.income and self.actual_commission:
            self.income = self.nhsale.price * self.actual_commission / 100
        elif self.income and not self.actual_commission:
            self.actual_commission = self.income / self.nhsale.price * 100
        models.Model.save(self, *args, **kw)
        e1, ec1, e2, ec2, d, dc = (self.employee1, self.employee1_commission,
                                   self.employee2, self.employee2_commission,
                                   self.director, self.director_commission)
        y, m = self.nhsale.nhmonth.year,self.nhsale.nhmonth.month 
        if e1 and ec1:
            q = e1.nhpays.filter(nhsaleside = self)
            nhp = q.count() == 1 and q[0] or NHPay(employee=e1, nhsaleside = self, year = y, month = m)
            nhp.amount = self.employee1_pay
            nhp.save()
        if e2 and ec2:
            q = e2.nhpays.filter(nhsaleside = self)
            nhp = q.count() == 1 and q[0] or NHPay(employee=e2, nhsaleside = self, year = y, month = m)
            nhp.amount = self.employee2_pay
            nhp.save()
        if d and dc:
            q = d.nhpays.filter(nhsaleside = self)
            nhp = q.count() == 1 and q[0] or NHPay(employee=d, nhsaleside = self, year = y, month = m)
            nhp.amount = self.director_pay
            nhp.save()
    class Meta:
        db_table = 'NHSaleSide'

class NHMonth(models.Model):
    nhbranch = models.ForeignKey('NHBranch', verbose_name=ugettext('nhbranch'))
    month = models.PositiveSmallIntegerField(ugettext('month'), 
                                             choices=((i,i) for i in range(1,13)))
    year = models.PositiveSmallIntegerField(ugettext('year'), 
                                            choices=((i,i) for i in range(datetime.now().year - 10,
                                                                          datetime.now().year + 10)))
    is_closed = models.BooleanField(editable=False, default=False)
    def __init__(self, *args, **kw):
        models.Model.__init__(self, *args, **kw)
        self.include_tax = True
    @property
    def avg_signed_commission(self):
        count, total = 0, 0
        for nhs in self.nhsales.all():
            for nhss in nhs.nhsaleside_set.all():
                count += 1
                total += nhss.signed_commission
        return count > 0 and total / count or 0
    @property 
    def avg_actual_commission(self):
        count, total = 0, 0
        for nhs in self.nhsales.all():
            for nhss in nhs.nhsaleside_set.all():
                count += 1
                total += nhss.signed_commission
        return count > 0 and total / count or 0
    @property
    def total_income(self):
        amount = 0
        for nhs in self.nhsales.all():
            for nhss in nhs.nhsaleside_set.all():
                amount += nhss.income
        if not self.include_tax:
            t = Tax.objects.filter(date__lte=date(self.year, self.month,1)).latest().value / 100 + 1
            amount = amount / t
        return amount
    @property
    def total_lawyer_pay(self):
        amount = 0
        for nhs in self.nhsales.all():
            for nhss in nhs.nhsaleside_set.all():
                amount += nhss.lawyers_pay
        return amount
    @property
    def total_net_income(self):
        amount = 0
        for nhs in self.nhsales.all():
            for nhss in nhs.nhsaleside_set.all():
                amount += nhss.net_income
        if not self.include_tax:
            t = Tax.objects.filter(date__lte=date(self.year, self.month,1)).latest().value / 100 + 1
            amount = amount / t
        return amount
    @property
    def total_commission(self):
        amount = 0
        for nhs in self.nhsales.all():
            for nhss in nhs.nhsaleside_set.all():
                amount += nhss.all_employee_commission
        return amount
    def close(self):
        self.is_closed = True
    def tax(self):
        return Tax.objects.filter(date__lte = date(self.year, self.month, 1)).latest().value
    class Meta:
        db_table = 'NHMonth'
        ordering = ['-year', '-month']
        permissions = (('nhmonth_season', 'NHMonth Season'),)

class NHSale(models.Model):
    nhmonth = models.ForeignKey('NHMonth', editable=False, related_name='nhsales')
    
    num = models.IntegerField(ugettext('sale_num'))
    address = models.CharField(ugettext('address'), max_length=50)
    hood = models.CharField(ugettext('hood'), max_length=50)
    rooms = models.PositiveSmallIntegerField(ugettext('rooms'))
    floor = models.PositiveSmallIntegerField(ugettext('floor'))
    type = models.ForeignKey('HouseType', verbose_name = ugettext('house_type'))
    
    sale_date = models.DateField(ugettext('sale_date'))
    price = models.FloatField(ugettext('price'))
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    def verbose_id(self):
        return self.nhmonth.nhbranch.prefix + '-' + str(self.id)
    def get_absolute_url(self):
        return '/nhsale/%s' % self.id
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
        d.fee_diff.delete()
        d.diffs.create(type=u'קיזוז', reason = u"ביטול מכירה מס' %s" % self.sale.id, amount = self.fee * -1)
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
    include_registration = models.NullBooleanField(ugettext('include_registration'), blank=True,
                                                   choices = (
                                                              ('','לא משנה'),
                                                              (0, 'לא'),
                                                              (1, 'כן')
                                                              ))
    price_include_lawyer = models.BooleanField(ugettext('price_include_lawyer'), choices = Boolean)
    price_no_lawyer = models.IntegerField(ugettext('sale_price_no_lawyer'))
    clients = models.TextField(ugettext('clients'))
    clients_phone = models.CharField(ugettext('phone'), max_length = 10)
    price_final = models.IntegerField(editable=False, null=True)
    employee_pay = models.DateField(ugettext('employee_paid'), editable=False)
    contractor_pay = models.DateField(ugettext('contractor_paid'), editable=False)
    remarks = models.TextField(ugettext('remarks'), null=True, blank=True)
    contract_num = models.CharField(ugettext('so_contact_num'), max_length=10, null=True, blank=True)    
    include_tax = models.BooleanField(ugettext('include_tax'), choices=Boolean, default=1)
    discount = models.FloatField(ugettext('given_discount'), null=True, blank=True)
    allowed_discount = models.FloatField(ugettext('allowed_discount'), null=True, blank=True)
    commission_include = models.BooleanField(ugettext('commission include'), default=True, blank=True)
    def __init__(self, *args, **kw):
        models.Model.__init__(self, *args, **kw)
        self.restore = True
    @property
    def actual_demand(self):
        return Demand.objects.get(month=self.contractor_pay.month, year=self.contractor_pay.year,
                                  project=self.demand.project)
    @property
    def project_commission_details(self):
        return self.commission_details.filter(employee_salary=None)
    @property
    def pc_base(self):
        for c in ['c_var_precentage', 'c_var_precentage_fixed', 'c_zilber_base']:
            q = self.project_commission_details.filter(commission=c)
            if q.count() == 0:
                continue
            finish_date = self.actual_demand.finish_date
            return self.restore and finish_date and restore_object(q[0], finish_date).value or q[0].value
        return 0
    @property
    def zdb(self):
        q = self.project_commission_details.filter(commission='c_zilber_discount')
        if q.count() == 0: return 0
        finish_date = self.actual_demand.finish_date
        return self.restore and finish_date and restore_object(q[0], finish_date).value or q[0].value
    @property
    def pb_dsp(self):
        q = self.project_commission_details.filter(commission='b_discount_save_precentage')
        if q.count() == 0: return 0
        finish_date = self.actual_demand.finish_date
        return self.restore and finish_date and restore_object(q[0], finish_date).value or q[0].value
    @property
    def c_final(self):
        q = self.project_commission_details.filter(commission='final')
        if q.count() == 0: return 0
        finish_date = self.actual_demand.finish_date
        return self.restore and finish_date and restore_object(q[0], finish_date).value or q[0].value
    @property
    def pc_base_worth(self):
        return self.pc_base * self.price_final / 100
    @property
    def pb_dsp_worth(self):
        return self.pb_dsp * self.price_final / 100
    @property
    def c_final_worth(self):
        return (self.c_final or 0) * (self.price_final or 0) / 100
    def project_price(self):
        c = self.house.building.project.commissions
        if c.include_lawyer == None:
            price = self.price
        elif c.include_lawyer == True:
            price = self.price_include_lawyer and self.price or self.price * LAWYER_TAX
        elif c.include_lawyer == False:
            price = self.price_no_lawyer
        TAX = Tax.objects.filter(date__lte=date(self.contractor_pay.year, self.contractor_pay.month,1)).latest().value / 100 + 1
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
        TAX = Tax.objects.filter(date__lte=date(self.employee_pay.year, self.employee_pay.month,1)).latest().value / 100 + 1        
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
        if self.price_final == None:
            self.price_final = self.project_price()
        models.Model.save(self, args, kw)
    @property
    def is_fixed(self):
        for attr in ['salehousemod', 'salepricemod', 'salepre', 'salereject']:
            if getattr(self, attr):
                return True
    @property
    def is_ep_ok(self):
        return self.employee_pay.year == self.demand.year and self.employee_pay.month == self.demand.month 
    @property
    def is_cp_ok(self):
        return self.contractor_pay.year == self.demand.year and self.contractor_pay.month == self.demand.month 
    def __unicode__(self):
        return u'בניין %s דירה %s ל%s' % (self.house.building.num, self.house.num, self.clients)
    def get_absolute_url(self):
        return '/sale/%s' % self.id
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

class ChangeLogManager(models.Manager):
    def object_changelog(obj):
        return self.filter(object_type = obj.__class__.name,
                           object_id = obj.id)

class ChangeLog(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length = 30)
    object_id = models.IntegerField()
    attribute = models.CharField(max_length = 30)
    verbose_name = models.CharField(max_length = 30)
    old_value = models.CharField(max_length = 30, null=True)
    new_value = models.CharField(max_length = 30, null=True)
    
    objects = ChangeLogManager()
    
    class Meta:
        db_table = 'ChangeLog'
        ordering = ['date']
        get_latest_by = 'date'

tracked_models = [BDiscountSave, BDiscountSavePrecentage, BHouseType, BSaleRate,
                  CAmount, CByPrice, CPrecentage, CPriceAmount, CVar,
                  CVarPrecentage, CVarPrecentageFixed, CZilber, EmploymentTerms,
                  ProjectCommission, SaleCommissionDetail, EmployeeSalaryBase, NHEmployeeSalary]

def restore_object(instance, date):
    model = instance.__class__
    id = getattr(instance, 'id', None)
    if not model in tracked_models or not id:
        raise TypeError()
    for l in ChangeLog.objects.filter(object_type = model.__name__,
                                      object_id = id,
                                      date__gt = date):
        try:
            if isinstance(getattr(instance, l.attribute), float):
                val = float(l.old_value)
            elif isinstance(getattr(instance, l.attribute), int):
                val = int(l.old_value)
            else:
                val = l.attribute
            setattr(instance, l.attribute, val)
        except:
            pass
    return instance

def track_changes(sender, **kwargs):
    instance = kwargs['instance']
    model = instance.__class__
    id = getattr(instance, 'id', None)
    if not model in tracked_models or not id:
        return
    old_obj = model.objects.get(pk=id)
    for field in model._meta.fields:
        if getattr(old_obj, field.name) == getattr(instance, field.name):
            continue
        cl = ChangeLog(object_type = model.__name__,
                       object_id = id,
                       attribute = field.name,
                       verbose_name = field.verbose_name,
                       old_value = getattr(old_obj, field.name),
                       new_value = getattr(instance, field.name))
        cl.save()

pre_save.connect(track_changes)
