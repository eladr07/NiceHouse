import Management.models as models

from reportlab.platypus import Paragraph
from pyfribidi import log2vis
from Management.templatetags.management_extras import commaise
from django.utils.translation import ugettext
from styles import *

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
        return super(ProjectNameAndCityField, self).__init__(log2vis(ugettext('pdf_project_name')),130)
    def format(self, item):
        return log2vis(item.project.name_and_city)
    
    class Meta:
        models = (models.Demand, models.Sale)

class ProjectInitiatorField(TableField):
    def __init__(self):
        return super(ProjectInitiatorField, self).__init__(log2vis(ugettext('pdf_initiator')),150)
    def format(self, item):
        return log2vis(item.project.initiator)
    
    class Meta:
        models = (models.Demand, models.Sale)

class MonthField(TableField):
    def __init__(self):
        return super(MonthField, self).__init__(log2vis(ugettext('pdf_month')))
    def format(self, item):
        return '%s/%s' % (item.month, item.year)
    
    class Meta:
        models = (models.Demand,)

class DemandSalesCountField(TableField):
    def __init__(self):
        return super(DemandSalesCountField, self).__init__(log2vis(ugettext('pdf_demand_sales_count')),50, is_summarized=True)
    def format(self, item):
        return len(item.get_sales())
    
    class Meta:
        models = (models.Demand,)

class DemandSalesTotalPriceField(TableField):
    def __init__(self):
        return super(DemandSalesTotalPriceField, self).__init__(log2vis(ugettext('pdf_demand_total_sales_price')),50, 
                                                                is_commaised=True, is_summarized=True)
    def format(self, item):
        return item.get_sales().total_price()
    
    class Meta:
        models = (models.Demand,)

class DemandTotalAmountField(TableField):
    def __init__(self):
        return super(DemandTotalAmountField, self).__init__(log2vis(ugettext('pdf_demand_total_amount')),50, is_commaised=True, 
                                                            is_summarized=True)
    def format(self, item):
        return item.get_total_amount()
    
    class Meta:
        models = (models.Demand,)
        
class InvoicesNumField(TableField):
    def __init__(self):
        return super(InvoicesNumField, self).__init__(log2vis(ugettext('pdf_invoices_num')),50)
    def format(self, item):
        return Paragraph('<br/>'.join([str(i.num) for i in item.invoices.all()]), styleRow9)
    
    def get_height(self, item):
        return 18 * item.invoices.count()
    
    class Meta:
        models = (models.Demand,)
        
class InvoicesAmountField(TableField):
    def __init__(self):
        return super(InvoicesAmountField, self).__init__(log2vis(ugettext('pdf_invoices_amount')), 50)
    def format(self, item):
        return Paragraph('<br/>'.join([commaise(i.amount) for i in item.invoices.all()]), styleRow9)
    
    def get_height(self, item):
        return 18 * item.invoices.count()
    
    class Meta:
        models = (models.Demand,)
        
class PaymentsNumField(TableField):
    def __init__(self):
        return super(PaymentsNumField, self).__init__(log2vis(ugettext('pdf_payments_num')),50)
    def format(self, item):
        return Paragraph('<br/>'.join([str(p.num) for p in item.payments.all()]), styleRow9)
    
    def get_height(self, item):
        return 18 * item.payments.count()
    
    class Meta:
        models = (models.Demand,)
        
class PaymentsAmountField(TableField):
    def __init__(self):
        return super(PaymentsAmountField, self).__init__(log2vis(ugettext('pdf_payments_amount')),50)
    def format(self, item):
        return Paragraph('<br/>'.join([commaise(p.amount) for p in item.payments.all()]), styleRow9)
    
    def get_height(self, item):
        return 18 * item.payments.count()
        
    class Meta:
        models = (models.Demand,)

class SaleClientsField(TableField):
    def __init__(self):
        return super(SaleClientsField, self).__init__(log2vis(ugettext('pdf_clients_name')), 65)
    def format(self, item):
        clients = item.clients
        str2 = ''
        parts = clients.strip().split('\r\n')
        parts.reverse()
        for s in parts:
            str2 += log2vis(s)
        return Paragraph(str2, styleRow10)
    
    class Meta:
        models = (models.Sale,)
        
class SalePriceWithTaxField(TableField):
    def __init__(self):
        return super(SalePriceWithTaxField, self).__init__(log2vis(ugettext('pdf_price_with_tax')), 50, is_commaised = True,
                                                           is_summarized = True)
    def format(self, item):
        return item.price_taxed
    
    class Meta:
        models = (models.Sale,)
        
class SaleIncludeLawyerTaxField(TableField):
    def __init__(self):
        return super(SaleIncludeLawyerTaxField, self).__init__(log2vis(ugettext('pdf_include_lawyer_tax')), 50)
    def format(self, item):
        if item.price_include_lawyer == None:
            return '---'
        elif item.price_include_lawyer == False:
            return ugettext('no')
        elif item.price_include_lawyer == True:
            return ugettext('yes')
    
    class Meta:
        models = (models.Sale,)
        
class SaleEmployeeNameField(TableField):
    def __init__(self):
        return super(SaleEmployeeNameField, self).__init__(log2vis(ugettext('pdf_employee_name')), 50)
    def format(self, item):
        return item.employee
    
    class Meta:
        models = (models.Sale,)

class HouseNumField(TableField):
    def __init__(self):
        return super(HouseNumField, self).__init__(log2vis(ugettext('pdf_house_num')),50)
    def format(self, item):
        return item.num
    
    class Meta:
        models = (models.House,)
        
class HouseRoomsField(TableField):
    def __init__(self):
        return super(HouseRoomsField, self).__init__(log2vis(ugettext('pdf_rooms_num')),50)
    def format(self, item):
        return item.rooms
    
    class Meta:
        models = (models.House,)
        
class HouseFloorField(TableField):
    def __init__(self):
        return super(HouseFloorField, self).__init__(log2vis(ugettext('pdf_floor')),50)
    def format(self, item):
        return item.floor
    
    class Meta:
        models = (models.House,)
        
class HouseSizeField(TableField):
    def __init__(self):
        return super(HouseSizeField, self).__init__(log2vis(ugettext('pdf_house_size')),50)
    def format(self, item):
        return item.net_size
    
    class Meta:
        models = (models.House,)
        
class HouseGardenSizeField(TableField):
    def __init__(self):
        return super(HouseGardenSizeField, self).__init__(log2vis(ugettext('pdf_garden_size')),50)
    def format(self, item):
        return item.garden_size
    
    class Meta:
        models = (models.House,)
        
class HouseTypeField(TableField):
    def __init__(self):
        return super(HouseTypeField, self).__init__(log2vis(ugettext('pdf_house_type')),50)
    def format(self, item):
        return item.type
    
    class Meta:
        models = (models.House,)