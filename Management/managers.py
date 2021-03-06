# coding: utf-8

import common
from django.db import models
from querysets import *
from datetime import date

def nhemployee_sort(nhemployee1, nhemployee2):
    query1 = nhemployee1.nhbranchemployee_set.all()
    query2 = nhemployee2.nhbranchemployee_set.all()
    if query1.count() == 0 and query2.count() == 0:
        return 0
    elif query1.count() == 0:
        return 1
    elif query2.count() == 0:
        return -1
    return cmp(query1.latest().nhbranch.id, query2.latest().nhbranch.id)

class SeasonManager(models.Manager):
    def range(self, from_year, from_month, to_year, to_month):
        return self.get_query_set().range(from_year, from_month, to_year, to_month)
    def get_query_set(self):
        return SeasonQuerySet(self.model)

class EmployeeSalaryBaseManager(SeasonManager):
    def nondeleted(self):
        return self.get_query_set().nondeleted()
    def get_query_set(self):
        return EmployeeSalaryBaseQuerySet(self.model)
    
class InvoiceManager(models.Manager):
    use_for_related_fields = True
    
    def total_amount_offset(self):
        return self.get_query_set().total_amount_offset()
    def get_query_set(self):
        return InvoiceQuerySet(self.model)

class PaymentManager(models.Manager):
    use_for_related_fields = True
    
    def total_amount(self):
        return self.get_query_set().total_amount()
    def get_query_set(self):
        return PaymentQuerySet(self.model)

class DemandManager(SeasonManager):
    use_for_related_fields = True
    
    def get_or_create(self, **kwargs):
        demand, created = super(DemandManager, self).get_or_create(**kwargs)
        commissions = demand.project.commissions
        if created and commissions.add_amount:
            demand.diffs.create(type=u'קבועה', amount = commissions.add_amount, reason = commissions.add_type)
        return demand, created
            
    def noinvoice(self):
        return self.get_query_set().noinvoice()
    def nopayment(self):
        return self.get_query_set().nopayment()
    def current(self):
        now = common.current_month()
        return self.filter(year = now.year, month = now.month)
    
    def get_query_set(self):
        return DemandQuerySet(self.model)

class DemandDiffManager(models.Manager):
    use_for_related_fields = True
    
    def total_amount(self):
        return self.get_query_set().total_amount()
    def get_query_set(self):
        return DemandDiffQuerySet(self.model)

class SaleManager(models.Manager):
    use_for_related_fields = True
    
    def contractor_pay_range(self, from_year, from_month, to_year, to_month):
        return self.get_query_set().contractor_pay_range(from_year, from_month, to_year, to_month)
    def get_query_set(self):
        return SaleQuerySet(self.model)
    
class HouseManager(models.Manager):
    use_for_related_fields = True
    
    def sold(self):
        return self.get_query_set().sold()
    def signed(self):
        return self.get_query_set().signed()
    def avalible(self):
        return self.get_query_set().avalible()
    def get_query_set(self):
        return HouseQuerySet(self.model)

class HouseVersionManager(models.Manager):
    use_for_related_fields = True
    
    def company(self):
        return self.get_query_set().company()
    def doh0(self):
        return self.get_query_set().doh0()
    def get_query_set(self):
        return HouseVersionQuerySet(self.model)

class CityCallersManager(models.Manager):
    use_for_related_fields = True
    
    def total_callers_num(self):
        return self.get_query_set().total_callers_num()

class MediaReferralsManager(models.Manager):
    use_for_related_fields = True
    
    def total_referrals_num(self):
        return self.get_query_set().total_referrals_num()
    def get_query_set(self):
        return MediaReferralsQuerySet(self.model)

class DivisionTypeManager(models.Manager):
    def nh_divisions(self):
        return self.filter(pk__in = (2,3,4))
    
class ProjectManager(models.Manager):
    def active(self):
        return self.filter(end_date=None, is_marketing=True)
    def archive(self):
        return self.exclude(end_date=None)

class EmployeeManager(models.Manager):
    def active(self):
        return self.filter(work_end = None)
    def archive(self):
        return self.exclude(work_end = None)
    
class NHBranchEmployeeManager(models.Manager):
    def month(self, year, month):
        start_date = date(year, month, 1)
        end_date = date(month == 12 and year + 1 or year, month == 12 and 1 or month + 1, 1)
        q = models.Q(start_date__lt = start_date) & (models.Q(end_date__isnull = True) | models.Q(end_date__gte = end_date))
        return self.filter(q)

class NHEmployeeManager(models.Manager):
    def active(self):
        query = self.filter(work_end = None)
        nhemployees = list(query)
        nhemployees.sort(nhemployee_sort)
        return nhemployees
    def archive(self):
        query = self.exclude(work_end = None)
        nhemployees = list(query)
        nhemployees.sort(nhemployee_sort)
        return nhemployees