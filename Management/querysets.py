from django.db.models import Avg, Max, Min, Count, Sum
from django.db import models
from models import PricelistType

class InvoiceQuerySet(models.query.QuerySet):
    def total_amount_offset(self):
        invoices_amount = self.aggregate(Sum('amount'))['amount__sum'] or 0
        offsets_amount = self.aggregate(Sum('offset__amount'))['offset__amount__sum'] or 0
        return invoices_amount + offsets_amount
    
class PaymentQuerySet(models.query.QuerySet):
    def total_amount(self):
        return self.aggregate(Sum('amount'))['amount__sum'] or 0
    
class DemandDiffQuerySet(models.query.QuerySet):
    def total_amount(self):
        return self.aggregate(Sum('amount'))['amount__sum'] or 0
    
class DemandQuerySet(models.query.QuerySet):
    def total_sales_commission(self):
        return self.aggregate(Sum('sales_commission'))['sales_commission__sum'] or 0
    def total_sale_count(self):
        return self.aggregate(Sum('sale_count'))['sale_count__sum'] or 0
    def noinvoice(self):
        query = self.annotate(invoices_num = Count('invoices'), payments_num = Count('payments'))
        return query.filter(invoices_num = 0, payments_num__gt = 0, force_fully_paid = False)
    def nopayment(self):
        query = self.annotate(invoices_num = Count('invoices'), payments_num = Count('payments'))
        return query.filter(invoices_num__gt = 0, payments_num = 0, force_fully_paid = False)

class SaleQuerySet(models.query.QuerySet):
    def total_price(self):
        return self.aggregate(Sum('price'))['price__sum'] or 0
    def total_price_final(self):
        return self.aggregate(Sum('price_final'))['price_final__sum'] or 0
    
class HouseQuerySet(models.query.QuerySet):
    def sold(self):
        q = models.Q(is_sold = True) | models.Q(sales__salecancel__isnull = True)
        return self.filter(q).annotate(sales_num = Count('sales')).filter(sales_num = 1)
    def signed(self):
        return self.filter(signups__cancel__isnull = False).annotate(signups_num = Count('signups')).filter(signups_num = 1)
    def avalible(self):
        q = models.Q(is_sold = False) & models.Q(sales__salecancel__isnull = True) & models.Q(signups__cancel__isnull = True)
        return self.filter(q).annotate(sales_num = Count('sales'), signups_num = Count('signups')).filter(sales_num = 0, signups_num = 0)

class HouseVersionQuerySet(models.query.QuerySet):
    def company(self):
        return self.filter(type__id = PricelistType.Company)
    def doh0(self):
        return self.filter(type__id = PricelistType.Doh0)

class CityCallersQuerySet(models.query.QuerySet):
    def total_callers_num(self):
        return self.aggregate(Sum('callers_num'))['callers_num__sum'] or 0        

class MediaReferralsQuerySet(models.query.QuerySet):
    def total_referrals_num(self):
        return self.aggregate(Sum('referrals_num'))['referrals_num__sum'] or 0
