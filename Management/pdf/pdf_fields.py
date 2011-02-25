import Management.models as models

from reportlab.platypus import Paragraph
from pyfribidi import log2vis
from styles import *
from Management.templatetags.management_extras import commaise

class TableField(object):
    def __init__(self, title='', width= -1, is_summarized=False, is_commaised=False):
        self.name = self.__class__.__name__
        self.title = title
        self.width = width
        self.is_summarized = is_summarized
        self.is_commaised = is_commaised
    def format(self, item):
        raise NotImplementedError
    def get_height(self, item):
        return 25
        
class ProjectNameAndCityField(TableField):
    def __init__(self):
        return super(ProjectNameAndCityField, self).__init__(log2vis(u'הפרוייקט\nשם'),
                                                             130)
    def format(self, item):
        return log2vis(item.project.name_and_city)
    
    class Meta:
        models = (models.Demand, models.Sale)

class ProjectInitiatorField(TableField):
    def __init__(self):
        return super(ProjectInitiatorField, self).__init__(log2vis(u'היזם\nשם'),
                                                             150)
    def format(self, item):
        return log2vis(item.project.initiator)
    
    class Meta:
        models = (models.Demand, models.Sale)

class MonthField(TableField):
    def __init__(self):
        return super(ProjectInitiatorField, self).__init__(log2vis(u'חודש'), None)
    def format(self, item):
        return '%s/%s' % (item.month, item.year)
    
    class Meta:
        models = (models.Demand,)

class DemandSalesCountField(TableField):
    def __init__(self):
        return super(DemandSalesCountField, self).__init__(log2vis(u"מכירות\nמס'"),
                                                           50, is_summarized=True)
    def format(self, item):
        return len(item.get_sales())
    
    class Meta:
        models = (models.Demand,)

class DemandSalesTotalPriceField(TableField):
    def __init__(self):
        return super(DemandSalesTotalPriceField, self).__init__(log2vis(u'מכירות\nסה"כ'),
                                                           50, is_commaised=True, is_summarized=True)
    def format(self, item):
        return item.get_sales().total_price()
    
    class Meta:
        models = (models.Demand,)

class DemandTotalAmountField(TableField):
    def __init__(self):
        return super(DemandTotalAmountField, self).__init__(log2vis(u'עמלה\nסה"כ'),
                                                           50, is_commaised=True, is_summarized=True)
    def format(self, item):
        return item.get_total_amount()
    
    class Meta:
        models = (models.Demand,)
        
class InvoicesNumField(TableField):
    def __init__(self):
        return super(InvoicesNumField, self).__init__(log2vis(u"מס' ח-ן"),
                                                           50)
    def format(self, item):
        return Paragraph('<br/>'.join([str(i.num) for i in item.invoices.all()]), styleRow9)
    
    def get_height(self, item):
        return 18 * item.invoices.count()
    
    class Meta:
        models = (models.Demand,)
        
class InvoicesAmountField(TableField):
    def __init__(self):
        return super(InvoicesAmountField, self).__init__(log2vis(u"סך ח-ן"),
                                                           50)
    def format(self, item):
        return Paragraph('<br/>'.join([commaise(i.amount) for i in item.invoices.all()]), styleRow9)
    
    def get_height(self, item):
        return 18 * item.invoices.count()
    
    class Meta:
        models = (models.Demand,)
        
class PaymentsNumField(TableField):
    def __init__(self):
        return super(PaymentsNumField, self).__init__(log2vis(u"מס' צ'ק"),
                                                           50)
    def format(self, item):
        return Paragraph('<br/>'.join([str(p.num) for p in item.payments.all()]), styleRow9)
    
    def get_height(self, item):
        return 18 * item.payments.count()
    
    class Meta:
        models = (models.Demand,)
        
class PaymentsAmountField(TableField):
    def __init__(self):
        return super(PaymentsAmountField, self).__init__(log2vis(u"סך צ'ק"),
                                                           50)
    def format(self, item):
        return Paragraph('<br/>'.join([commaise(p.amount) for p in item.payments.all()]), styleRow9)
    
    def get_height(self, item):
        return 18 * item.payments.count()
        
    class Meta:
        models = (models.Demand,)
    
