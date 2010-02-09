import django.forms as forms
import sys
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext
from models import *
from datetime import datetime, date

class SeasonForm(forms.Form):
    from_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('from_year'), initial = Demand.current_month().year)
    from_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('from_month'),
                              initial = Demand.current_month().month)
    to_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('to_year'), initial = Demand.current_month().year)
    to_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('to_month'),
                              initial = Demand.current_month().month)
    def clean_from_year(self):
        return int(self.cleaned_data['from_year'])
    def clean_from_month(self):
        return int(self.cleaned_data['from_month'])
    def clean_to_year(self):
        return int(self.cleaned_data['to_year'])
    def clean_to_month(self):
        return int(self.cleaned_data['to_month'])

class MonthForm(forms.Form):
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('month'),
                              initial = Demand.current_month().month)  
    def clean_year(self):
        return int(self.cleaned_data['year'])
    def clean_month(self):
        return int(self.cleaned_data['month'])
    
class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
    class Meta:
        model = Contact

class ExistContactForm(forms.Form):
    contact = forms.ModelChoiceField(queryset=Contact.objects.all())

class SalePriceModForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['date'].widget = forms.TextInput({'class':'vDateField'})    
    class Meta:
        model = SalePriceMod

class SaleHouseModForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['date'].widget = forms.TextInput({'class':'vDateField'})    
    class Meta:
        model = SaleHouseMod

class SalePreForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['date'].widget = forms.TextInput({'class':'vDateField'})   
        self.fields['employee_pay'].widget = forms.TextInput({'class':'vDateField'})    
    class Meta:
        model = SalePre
        
class SaleRejectForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['date'].widget = forms.TextInput({'class':'vDateField'})   
        self.fields['employee_pay'].widget = forms.TextInput({'class':'vDateField'}) 
        self.fields['to_month'].widget = forms.TextInput({'class':'vDateField'})    
    class Meta:
        model = SaleReject
        
class ProjectForm(forms.ModelForm):    
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'5'})
        self.fields['start_date'].widget = forms.TextInput({'class':'vDateField'})
        self.fields['end_date'].widget = forms.TextInput({'class':'vDateField'})
    class Meta:
        model = Project

class ProjectDetailsForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
    class Meta:
        model = ProjectDetails

class BuildingForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
    class Meta:
        model = Building

class PricelistForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'5'})
        self.fields['settle_date'].widget = forms.TextInput({'class':'vDateField'})
    class Meta:
        model = Pricelist

class PricelistUpdateForm(forms.Form):
    pricelisttype = forms.ModelChoiceField(queryset = PricelistType.objects.all(), 
                                           required=False, label = ugettext('pricelisttype'))
    all_pricelists = forms.BooleanField(required=False, label=ugettext('all_pricelists'))
    date = forms.DateField(label=ugettext('date'))
    amount = forms.FloatField(label=ugettext('amount'), required=False)
    precentage = forms.FloatField(label=ugettext('precentage'), required=False)
    def __init__(self, *args, **kw):
        forms.Form.__init__(self, *args, **kw)
        self.fields['date'].widget = forms.TextInput({'class':'vDateField'})

class ParkingForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
        if self.instance.id > 0:
            self.fields['house'].queryset = self.instance.building.houses.all()
    class Meta:
        model = Parking
        
class StorageForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
        if self.instance.id > 0:
            self.fields['house'].queryset = self.instance.building.houses.all()
    class Meta:
        model = Storage

class HouseForm(forms.ModelForm):
    parking1 = forms.ModelChoiceField(queryset=Parking.objects.all(), required=False, label = ugettext('parking') + ' 1')
    parking2 = forms.ModelChoiceField(queryset=Parking.objects.all(), required=False, label = ugettext('parking') + ' 2')
    parking3 = forms.ModelChoiceField(queryset=Parking.objects.all(), required=False, label = ugettext('parking') + ' 3')
    storage1 = forms.ModelChoiceField(queryset=Storage.objects.all(), required=False, label = ugettext('storage') + ' 1')
    storage2 = forms.ModelChoiceField(queryset=Storage.objects.all(), required=False, label = ugettext('storage') + ' 2')
    price = forms.IntegerField(label=ugettext('price'), required=False)
    def save(self, price_type_id, *args, **kw):
        h = forms.ModelForm.save(self, *args, **kw)
        for f in ['parking1','parking2','parking3']:
            if self.cleaned_data[f]:
                h.parkings.add(self.cleaned_data[f])
        for f in ['storage1','storage2']:
            if self.cleaned_data[f]:
                h.storages.add(self.cleaned_data[f])
        price = self.cleaned_data['price']
        q = self.instance.versions.filter(type__id = price_type_id)
        if price and (q.count() == 0 or q.latest().price != price):
            self.instance.versions.add(HouseVersion(type=PricelistType.objects.get(pk=price_type_id), price = price,
                                                    date = datetime.now()))
        return h
    def __init__(self, price_type_id, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        if not self.instance.id:
            return
        i=1
        for p in self.instance.parkings.all():
            self.initial['parking%s' % i] = p.id
            i=i+1
        i=1
        for s in self.instance.storages.all():
            self.initial['storage%s' % i] = s.id
            i=i+1
        vs = self.instance.versions.filter(type__id = price_type_id)
        if vs.count() > 0:
            self.initial['price'] = vs.latest().price
    class Meta:
        model = House

class EmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['work_start'].widget = forms.TextInput(attrs={'class':'vDateField'})
        self.fields['work_end'].widget = forms.TextInput(attrs={'class':'vDateField'})
        if self.instance.id:
            self.fields['main_project'].queryset = self.instance.projects
    class Meta:
        model = Employee

class NHEmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['work_start'].widget = forms.TextInput(attrs={'class':'vDateField'})
        self.fields['work_end'].widget = forms.TextInput(attrs={'class':'vDateField'})
    class Meta:
        model = NHEmployee
      
class ProjectCommissionForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'5'})
    class Meta:
        model = ProjectCommission

class EmployeeAddProjectForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), label=ugettext('employee'))
    project = forms.ModelChoiceField(queryset=Project.objects.active(), label=ugettext('project'))
    start_date = forms.DateField(label=ugettext('start date'))
    def __init__(self, *args, **kw):
        super(EmployeeAddProjectForm, self).__init__(*args, **kw)
        self.fields['start_date'].widget.attrs = {'class':'vDateField'}

class EmployeeRemoveProjectForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), label=ugettext('employee'))
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label=ugettext('project'))
    end_date = forms.DateField(label=ugettext('end_date'))
    def __init__(self, *args, **kw):
        super(EmployeeRemoveProjectForm, self).__init__(*args, **kw)
        self.fields['end_date'].widget.attrs = {'class':'vDateField'}
    
class BDiscountSaveForm(forms.ModelForm):
    class Meta:
        model = BDiscountSave
        
class BDiscountSavePrecentageForm(forms.ModelForm):
    class Meta:
        model = BDiscountSavePrecentage

class CVarForm(forms.ModelForm):    
    class Meta:
        model = CVar
        
class CVarPrecentageForm(forms.ModelForm):          
    class Meta:
        model = CVarPrecentage
    
class CVarPrecentageFixedForm(forms.ModelForm):
    class Meta:
        model = CVarPrecentageFixed
        
class CZilberForm(forms.ModelForm):
    class Meta:
        model = CZilber

class NHCBaseForm(forms.ModelForm):
    class Meta:
        model = NHCBase
        
class NHCBranchIncomeForm(forms.ModelForm):
    class Meta:
        model = NHCBranchIncome

class CByPriceForm(forms.ModelForm):
    def save(self, *args, **kw):
        if self.instance.price == 0:
            self.instance.price == sys.maxint
        return forms.ModelForm.save(self, *args, **kw)
    class Meta:
        model = CByPrice
 
class SignupForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    building = forms.ModelChoiceField(queryset = Building.objects.all(), label=ugettext('building'))
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget.attrs = {'cols':'20', 'rows':'3'}
        self.fields['clients'].widget.attrs = {'cols':'20', 'rows':'3'}
        self.fields['clients_phone'].widget.attrs = {'cols':'20', 'rows':'3'}
        self.fields['clients_address'].widget.attrs = {'cols':'20', 'rows':'3'}
        self.fields['date'].widget.attrs = {'class':'vDateField'}
        self.fields['sale_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = Signup 

class SignupCancelForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['reason'].widget.attrs = {'cols':'20', 'rows':'3'}
        self.fields['date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model =SignupCancel

class DemandDiffForm(forms.ModelForm):
    add_type = forms.ChoiceField(choices=((1,u'תוספת'),
                                          (2,'קיזוז')), 
                                          label=ugettext('add_type'))
    def clean(self):
        add_type, amount = self.cleaned_data['add_type'], self.cleaned_data['amount']
        self.cleaned_data['amount'] = int(add_type) == 2 and (amount * -1) or amount 
        return self.cleaned_data
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        if self.instance.id:
            self.fields['add_type'].initial = self.instance.amount >= 0 and 1 or 2
    class Meta:
        model = DemandDiff
        
class SaleAnalysisForm(SeasonForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    include_clients = forms.ChoiceField(label = ugettext('include_clients'), required = False, choices = ((0,u'לא'),
                                                                                                          (1,u'כן')))
    house_type = forms.ModelChoiceField(queryset=HouseType.objects.all(), required = False, label = ugettext('house_type'))
    rooms_num = forms.ChoiceField(label = ugettext('rooms'), required = False, choices = RoomsChoices)
            
class SaleForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    building = forms.ModelChoiceField(queryset = Building.objects.all(), label=ugettext('building'))
    joined_sale = forms.BooleanField(label = ugettext('joined sale'), required = False)
    signup_date = forms.DateField(label=ugettext('signup_date'), required=False)
    def clean_house(self):
        house = self.cleaned_data['house']
        if self.instance.id:
            s = house.get_sale()
            if s and s != self.instance:
                raise forms.ValidationError(u"כבר קיימת מכירה לדירה זו")
        else:
            if house.get_sale():
                raise forms.ValidationError(u"כבר קיימת מכירה לדירה זו")
        return house
    def clean(self):
        if self.cleaned_data['joined_sale']: 
            self.cleaned_data['employee'] = None
        return self.cleaned_data
    def save(self, *args, **kw):
        house, discount, allowed_discount = self.cleaned_data['house'], self.cleaned_data['discount'], self.cleaned_data['allowed_discount']
        '''checks if entered a allowed discount but not discount -> will fill
        discount automatically'''
        if allowed_discount and not discount:
            max_p = house.versions.filter(type__id = PricelistType.Company).latest().price
            min_p = max_p * (1 - allowed_discount/100)
            price = self.cleaned_data['price']
            self.cleaned_data['discount'] = 100 - (100 / float(max_p) * price)
            self.cleaned_data['contract_num'] = 0
        '''fill Signup automatically. it is temp fix until signup_date field will be removed.'''
        if self.cleaned_data['signup_date'] != None:
            signup = house.get_signup() or Signup()
            signup.date = self.cleaned_data['signup_date']
            for attr in ['house','clients','clients_phone','sale_date','price','price_include_lawyer']:
                setattr(signup, attr, self.cleaned_data[attr])
            signup.save()
        return forms.ModelForm.save(self, *args, **kw)
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
        self.fields['clients'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
        self.fields['sale_date'].widget = forms.TextInput({'class':'vDateField'})
        self.fields['signup_date'].widget = forms.TextInput({'class':'vDateField'})
        if self.instance.id:
            self.fields['project'].initial = self.instance.house.building.project.id
            self.fields['building'].initial = self.instance.house.building.id
            self.fields['house'].initial = self.instance.house.id
            self.fields['building'].queryset = self.instance.house.building.project.buildings.all()
            self.fields['house'].queryset = self.instance.house.building.houses.all()
            #fill signup_date field.
            signup= self.instance.house.get_signup()
            if signup:
                self.fields['signup_date'].initial = signup.date
            if not self.instance.employee:
                self.fields['joined_sale'].initial = True
    class Meta:
        model = Sale

class EmployeeEndForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['work_end'].widget = forms.TextInput({'class':'vDateField'})
    class Meta:
        model = EmployeeBase
        fields = ('work_end',)
        
class ProjectEndForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['end_date'].widget = forms.TextInput({'class':'vDateField'})
    class Meta:
        model = Project
        fields = ('end_date',)
        
class DemandForm(forms.ModelForm):    
    remarks = forms.CharField(widget=forms.Textarea(attrs={'cols':'20', 'rows':'3'}), required = False ,
                              label=ugettext('remarks'))
    def save(self, *args, **kw):
        if self.instance.id:
            i=forms.ModelForm.save(self, *args, **kw)
        else:
            i=forms.ModelForm.save(self, *args, **kw)
            self.instance.feed()
        return i
    class Meta:
        model = Demand

class DemandInvoiceForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label = ugettext('project'))
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i,i) for i in range(1,12)), label = ugettext('month'),
                              initial = datetime.now().month)
    
    def save(self, *args, **kw):
        d = Demand.objects.get(project = self.cleaned_data['project'], year = self.cleaned_data['year'],
                               month = self.cleaned_data['month'])
        self.instance.demands.clear()
        i = forms.ModelForm.save(self, *args, **kw)
        d.invoices.add(i)
        return i
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['date'].widget.attrs = {'class':'vDateField'}
        if self.instance.id and self.instance.demands.count() == 1:
            demand = self.instance.demands.all()[0]
            self.fields['project'].initial = demand.project_id
            self.fields['year'].initial = demand.year
            self.fields['month'].initial = demand.month
    class Meta:
        model = Invoice

class InvoiceForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = Invoice
        
class InvoiceOffsetForm(forms.ModelForm):
    invoice_num = forms.IntegerField(label=ugettext('invoice_num'))       
    add_type = forms.ChoiceField(choices=((1,u'תוספת'),
                                          (2,'קיזוז')), 
                                          label=ugettext('add_type'))
    def clean(self):
        add_type, amount = self.cleaned_data['add_type'], self.cleaned_data['amount']
        self.cleaned_data['amount'] = int(add_type) == 2 and (amount * -1) or amount 
        return self.cleaned_data
    def clean_invoice_num(self):
        invoice_num = self.cleaned_data['invoice_num']
        invoices = Invoice.objects.filter(num = invoice_num)
        if invoices.count() == 0:
            raise forms.ValidationError(u"לא קיימת חשבונית שזה מספרה.")
        elif invoices.count() > 1:
            raise forms.ValidationError(u"קיימת יותר מחשבונית אחת עם מספר זה.")
        return invoice_num
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['date'].widget.attrs = {'class':'vDateField'}
        if self.instance.id:
            self.fields['add_type'].initial = self.instance.amount >= 0 and 1 or 2 
    class Meta:
        model = InvoiceOffset
        fields = ['invoice_num','date','add_type','amount','reason','remarks']
        
class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'1'})
        self.fields['payment_date'].widget.attrs = {'class':'vDateField', 'size':10}
        for field in ['num','support_num','bank','branch_num','amount']:
            self.fields[field].widget.attrs = {'size':10}
    class Meta:
        model = Payment

class SplitPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'1'})
        self.fields['payment_date'].widget.attrs = {'class':'vDateField', 'size':10}
    class Meta:
        model = Payment
        exclude = ('amount')

class SplitPaymentDemandForm(MonthForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label = ugettext('project'))
    amount = forms.IntegerField(label=ugettext('amount'))
    
class DemandPaymentForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label = ugettext('project'))
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i+1,i+1) for i in range(12)), label = ugettext('month'),
                              initial = datetime.now().month)
    
    def save(self, *args, **kw):
        d = Demand.objects.get(project = self.cleaned_data['project'], year = self.cleaned_data['year'],
                               month = self.cleaned_data['month'])
        self.instance.demands.clear()
        p = forms.ModelForm.save(self, *args, **kw)
        d.payments.add(p)
        return p
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['payment_date'].widget.attrs = {'class':'vDateField'}
        if self.instance.id and self.instance.demands.count() == 1:
            demand = self.instance.demands.all()[0]
            self.fields['project'].initial = demand.project_id
            self.fields['year'].initial = demand.year
            self.fields['month'].initial = demand.month
    class Meta:
        model = Payment

class NHSaleForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['sale_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = NHSale

class NHSaleSideForm(forms.ModelForm):
    lawyer1_pay = forms.FloatField(label=ugettext('lawyer_pay'), required=False)
    lawyer2_pay = forms.FloatField(label=ugettext('lawyer_pay'), required=False)
    def save(self, *args, **kw):
        nhs = forms.ModelForm.save(self, *args,**kw)
        nhsale = nhs.nhsale
        year, month = nhsale.nhmonth.year, nhsale.nhmonth.month
        income = self.cleaned_data['income']
        self.cleaned_data['actual_commission'] = income / nhsale.price * 100
        l1, l2 = self.cleaned_data['lawyer1'], self.cleaned_data['lawyer2']
        lp1, lp2 = self.cleaned_data['lawyer1_pay'], self.cleaned_data['lawyer2_pay']
        if l1 and lp1:
            q = l1.nhpays.filter(nhsaleside = nhs)
            nhp = q.count() == 1 and q[0] or NHPay(lawyer=l1, nhsaleside = nhs, year = year, month = month)
            nhp.amount = lp1
            nhp.save()
        if l2 and lp2:
            q = l2.nhpays.filter(nhsaleside = nhs)
            nhp = q.count() == 1 and q[0] or NHPay(lawyer=l2, nhsaleside = nhs, year = year, month = month)
            nhp.amount = lp2
            nhp.save()
        return nhs
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['employee_remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['voucher_date'].widget.attrs = {'class':'vDateField'}
        if self.instance.id:
            nhss = self.instance
            if self.instance.lawyer1:
                pays = self.instance.lawyer1.nhpays.filter(nhsaleside=nhss)
                if pays.count() == 1:
                    self.fields['lawyer1_pay'].initial = pays[0].amount
            if self.instance.lawyer2:
                pays = self.instance.lawyer2.nhpays.filter(nhsaleside=nhss)
                if pays.count() == 1:
                    self.fields['lawyer2_pay'].initial = pays[0].amount
    class Meta:
        model = NHSaleSide

class AdvancePaymentForm(forms.ModelForm):
    class Meta:
        model = AdvancePayment

class LoanForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        super(LoanForm, self).__init__(*args, **kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'30', 'rows':'6'})
    class Meta:
        model= Loan

class DemandSendForm(forms.ModelForm):
    is_finished = forms.BooleanField(required=False)
    by_mail = forms.BooleanField(required=False)
    mail = forms.EmailField(required=False)
    by_fax = forms.BooleanField(required=False)
    fax = forms.CharField(max_length=20, required=False)
    class Meta:
        model = Demand
        exclude = ('project','year','month','sale_count')

class SeasonDivisionTypeForm(SeasonForm):
    division_type = forms.ModelChoiceField(queryset = DivisionType.objects.all(), label=ugettext('division_type'))

class LoanPayForm(forms.ModelForm):
    class Meta:
        model = LoanPay
        
class ReminderForm(forms.ModelForm):
    status = forms.ModelChoiceField(queryset=ReminderStatusType.objects.all(), label=ugettext('status'))
    def save(self, *args, **kw):
        r = forms.ModelForm.save(self, *args, **kw)
        if not self.instance.statuses.count() or self.instance.statuses.latest().type.id != self.cleaned_data['status']:
            r.statuses.create(type=self.cleaned_data['status'])
        return r
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['content'].widget = forms.Textarea(attrs={'cols':'30', 'rows':'6'})
        if self.instance.statuses.count():
            self.fields['status'].initial = self.instance.statuses.latest().type.id
    class Meta:
        model = Reminder

class SalaryExpensesForm(forms.ModelForm):
    class Meta:
        model = SalaryExpenses
        
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task

class TaxForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        super(TaxForm, self).__init__(*args, **kw)
        self.fields['date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = Tax

class AttachmentForm(forms.ModelForm):
    tag_new = forms.CharField(max_length=20, required=False, label=ugettext('tag_new'))
    
    def save(self, *args, **kw):
        forms.ModelForm.save(self, *args, **kw)
        tag = self.cleaned_data['tag_new'].strip()
        if tag and tag != '':
            self.instance.tags.create(name=tag)
        return self.instance
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
    
    class Meta:
        model = Attachment

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account

class NHBranchEmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        super(NHBranchEmployeeForm, self).__init__(*args, **kw)
        self.fields['start_date'].widget.attrs = {'class':'vDateField'}
        self.fields['end_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = NHBranchEmployee

class IncomeFilterForm(SeasonForm):
    division_type = forms.ModelChoiceField(queryset = DivisionType.objects.all(), label=ugettext('division_type'), 
                                           required=False)
    income_type = forms.ModelChoiceField(queryset = IncomeType.objects.all(), label=ugettext('income_type'), 
                                         required=False)
    client_type = forms.ModelChoiceField(queryset = ClientType.objects.all(), label=ugettext('client_name'), 
                                         required=False)
    income_producer_type = forms.ModelChoiceField(queryset = IncomeProducerType.objects.all(), label=ugettext('income_producer_type'), 
                                                  required=False)
    
class CheckFilterForm(SeasonForm):
    division_type = forms.ModelChoiceField(queryset = DivisionType.objects.all(), label=ugettext('division_type'), 
                                           required=False)
    expense_type = forms.ModelChoiceField(queryset = ExpenseType.objects.all(), label=ugettext('expense_type'), 
                                          required=False)
    supplier_type = forms.ModelChoiceField(queryset = SupplierType.objects.all(), label=ugettext('supplier_type'), 
                                           required=False)

class EmployeeCheckFilterForm(SeasonForm):
    employee = forms.ModelChoiceField(queryset = EmployeeBase.objects.all(), label=ugettext('employee'), required=False)
    division_type = forms.ModelChoiceField(queryset = DivisionType.objects.all(), label=ugettext('division_type'), 
                                           required=False)
    expense_type = forms.ModelChoiceField(queryset = ExpenseType.objects.all(), label=ugettext('expense_type'), 
                                          required=False)

class CheckForm(forms.ModelForm):
    invoice_num = forms.IntegerField(label = ugettext('invoice_num'), help_text=u'החשבונית חייבת להיות מוזנת במערכת',
                                     required=False)
    new_division_type = forms.CharField(label = ugettext('new_division_type'), max_length = 20, required=False)
    new_expense_type = forms.CharField(label = ugettext('new_expense_type'), max_length = 20, required=False)
    new_supplier_type = forms.CharField(label = ugettext('new_supplier_type'), max_length = 20, required=False)

    def clean_invoice_num(self):
        invoice_num = self.cleaned_data['invoice_num']
        query = Invoice.objects.filter(num = invoice_num)
        if query.count()==0:
            raise forms.ValidationError(u"אין חשבונית עם מס' זה")
        return invoice_num
    def save(self, *args, **kw):
        invoice_num = self.cleaned_data['invoice_num']
        invoice = Invoice.objects.get(num = invoice_num)
        self.instance.invoice = invoice
        return forms.ModelForm.save(self,*args,**kw)
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['issue_date'].widget.attrs = {'class':'vDateField'}
        self.fields['pay_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = Check
        fields = ['division_type','new_division_type','expense_type','new_expense_type',
                  'supplier_type', 'new_supplier_type','invoice_num','type','issue_date','pay_date','num','amount',
                  'tax_deduction_source','order_verifier','payment_verifier','remarks']

class EmployeeCheckForm(forms.ModelForm):
    invoice_num = forms.IntegerField(label = ugettext('invoice_num'), help_text=u'החשבונית חייבת להיות מוזנת במערכת',
                                     required=False)
    new_division_type = forms.CharField(label = ugettext('new_division_type'), max_length = 20, required=False)
    new_expense_type = forms.CharField(label = ugettext('new_expense_type'), max_length = 20, required=False)
    
    def clean_invoice_num(self):
        invoice_num = self.cleaned_data['invoice_num']
        query = Invoice.objects.filter(num = invoice_num)
        if query.count()==0:
            raise forms.ValidationError(u"אין חשבונית עם מס' זה")
        return invoice_num
    def save(self, *args, **kw):
        invoice_num = self.cleaned_data['invoice_num']
        invoice = Invoice.objects.get(num = invoice_num)
        self.instance.invoice = invoice
        return forms.ModelForm.save(self,*args,**kw)
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['issue_date'].widget.attrs = {'class':'vDateField'}
        self.fields['pay_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = EmployeeCheck
        fields = ['division_type','new_division_type','employee','year','month','expense_type','new_expense_type','purpose_type',
                  'invoice_num','type','amount','num','issue_date','pay_date','remarks']

class IncomeForm(forms.ModelForm):
    new_division_type = forms.CharField(label = ugettext('new_division_type'), max_length = 20, required=False)
    new_income_type = forms.CharField(label = ugettext('new_income_type'), max_length = 20, required=False)
    new_income_producer_type = forms.CharField(label = ugettext('new_income_producer_type'), max_length = 20, required=False)
    new_client_type = forms.CharField(label=ugettext('new_client_type'), max_length = 30, required = False)

    def clean(self):
        if not self.cleaned_data['division_type'] and not self.cleaned_data['new_division_type']:
            raise forms.ValidationError(ugettext('missing_division_type'))
        if not self.cleaned_data['income_type'] and not self.cleaned_data['new_income_type']:
            raise forms.ValidationError(ugettext('missing_income_type'))
        if not self.cleaned_data['income_producer_type'] and not self.cleaned_data['new_income_producer_type']:
            raise forms.ValidationError(ugettext('missing_income_producer_type'))
        if not self.cleaned_data['client_type'] and not self.cleaned_data['new_client_type']:
            raise forms.ValidationError(ugettext('missing_client_type'))
        return self.cleaned_data
    
    class Meta:
        model = Income
        fields = ['year','month','division_type','new_division_type','income_type','new_income_type',
                  'income_producer_type','new_income_producer_type','client_type','new_client_type']

class DealForm(forms.ModelForm):
    new_client_status_type = forms.CharField(label=ugettext('new_client_status_type'), max_length = 30, required = False)
    
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        
    def clean(self):
        if not self.cleaned_data['client_status_type'] and not self.cleaned_data['new_client_status_type']:
            raise forms.ValidationError(ugettext('missing_client_status_type'))
        return self.cleaned_data
    
    class Meta:
        model = Deal
        fields = ['client_status_type','new_client_status_type','address','rooms','floor','price','commission_precentage','commission','remarks']

class NHMonthForm(MonthForm):
    nhbranch = forms.ModelChoiceField(queryset = NHBranch.objects.all(), label=ugettext('nhbranch'))  
    
class EmploymentTermsForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        self.fields['tax_deduction_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = EmploymentTerms

class DemandRemarksForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields= ('remarks',)
        
class DemandSaleCountForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields= ('sale_count',)

class EmployeeSalaryForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        super(EmployeeSalaryForm, self).__init__(*args, **kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['pdf_remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
    class Meta:
        model = EmployeeSalary
  
class NHEmployeeSalaryForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        super(NHEmployeeSalaryForm, self).__init__(*args, **kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['pdf_remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
    class Meta:
        model = NHEmployeeSalary
            
class EmployeeSalaryRemarksForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields= ('employee', 'remarks')

class EmployeeSalaryRefundForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields= ('employee', 'refund','refund_type')

class NHEmployeeSalaryRemarksForm(forms.ModelForm):
    class Meta:
        model = NHEmployeeSalary
        fields= ('nhemployee', 'remarks')

class NHEmployeeSalaryRefundForm(forms.ModelForm):
    class Meta:
        model = NHEmployeeSalary
        fields= ('nhemployee', 'refund','refund_type')

class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(choices = [('done', 'בוצעו'), ('undone','לא בוצעו'), ('all','הכל')])
    sender = forms.ChoiceField(choices = [('me', 'אני שלחתי'), ('others','נשלחו אלי')])

class DemandReportForm(MonthForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))

class ProjectSeasonForm(SeasonForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))

class NHBranchSeasonForm(SeasonForm):
    nhbranch = forms.ModelChoiceField(queryset = NHBranch.objects.all(), label=ugettext('nhbranch'))

class EmployeeSeasonForm(SeasonForm):
    employee = forms.ModelChoiceField(queryset = EmployeeBase.objects.all(), label=ugettext('employee'))
    
class MadadBIForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        self.fields['publish_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = MadadBI

class MadadCPForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        self.fields['publish_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = MadadCP
        
class ContactFilterForm(forms.Form):
    first_name = forms.CharField(label=ugettext('first_name'), required=False)
    last_name = forms.CharField(label=ugettext('last_name'), required=False)
    role = forms.CharField(label=ugettext('role'), required=False)
    company = forms.CharField(label=ugettext('company'), required=False)

class LocateDemandForm(MonthForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    
class LocateHouseForm(forms.Form):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    building_num = forms.IntegerField(widget=forms.TextInput(attrs={'size':'3'}),
                                      min_value=1, label=ugettext('building_num'))
    house_num = forms.IntegerField(widget=forms.TextInput(attrs={'size':'3'}),
                                   min_value=1, label=ugettext('house_num'))