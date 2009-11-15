import django.forms as forms
import sys
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext
from models import *
from datetime import datetime, date

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
        
class SaleForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    building = forms.ModelChoiceField(queryset = Building.objects.all(), label=ugettext('building'))
    joined_sale = forms.BooleanField(label = ugettext('joined sale'), required = False)
    signup_date = forms.DateField(label=ugettext('signup_date'), required=False)
    def clean_house(self):
        house = self.cleaned_data['house']
        if self.instance.id:
            s = house.get_sale()
            if s != None and s != self.instance:
                raise ValidationError(u"כבר קיימת מכירה לדירה זו")
        else:
            if house.get_sale() != None:
                raise ValidationError(u"כבר קיימת מכירה לדירה זו")
        return house
        
    def save(self, *args, **kw):
        house, discount, allowed_discount = (self.cleaned_data['house'],
                                             self.cleaned_data['discount'],
                                             self.cleaned_data['allowed_discount'])
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
        if self.cleaned_data['joined_sale']: self.cleaned_data['employee'] = None
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
        i = forms.ModelForm.save(self, *args, **kw)
        d.invoices.add(i)
        return i
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['date'].widget.attrs = {'class':'vDateField'}
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
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = InvoiceOffset
        
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

class SplitPaymentDemandForm(forms.Form):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label = ugettext('project'))
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i+1,i+1) for i in range(12)), label = ugettext('month'),
                              initial = datetime.now().month)
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
        p = forms.ModelForm.save(self, *args, **kw)
        d.payments.add(p)
        return p
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['payment_date'].widget.attrs = {'class':'vDateField'}
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
        year, month = nhs.nhsale.nhmonth.year, nhs.nhsale.nhmonth.month
        l1, l2 = self.cleaned_data['lawyer1'], self.cleaned_data['lawyer2']
        lp1, lp2 = self.cleaned_data['lawyer1_pay'], self.cleaned_data['lawyer2_pay']
        if l1 and lp1:
            q = l1.nhpays.filter(nhsaleside = self)
            nhp = q.count() == 1 and q[0] or NHPay(lawyer=l1, nhsaleside = nhs, year = year, month = month)
            nhp.amount = nhp.amount and (nhp.amount + lp1) or lp1
            nhp.save()
        if l2 and lp2:
            q = l2.nhpays.filter(nhsaleside = self)
            nhp = q.count() == 1 and q[0] or NHPay(lawyer=l2, nhsaleside = nhs, year = year, month = month)
            nhp.amount = nhp.amount and (nhp.amount + lp2) or lp2
            nhp.save()
        return nhs
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['employee_remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['voucher_date'].widget.attrs = {'class':'vDateField'}
        if self.instance.id:
            nhsale = self.instance.nhsale
            if self.instance.lawyer1:
                pays = self.instance.lawyer1.pays.filter(nhsale=nhsale)
                self.fields['lawyer1_pay'].initial = pays[0].amount
            if self.instance.lawyer2:
                pays = self.instance.lawyer2.pays.filter(nhsale=nhsale)
                self.fields['lawyer2_pay'].initial = pays[0].amount
    class Meta:
        model = NHSaleSide

class AdvancePaymentForm(forms.ModelForm):
    class Meta:
        model = AdvancePayment

class LoanForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        super(LoanForm, self).__init__(*args, **kw)
        self.fields['date'].widget.attrs = {'class':'vDateField'}
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
        
class LoanPayForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        super(LoanPayForm, self).__init__(*args, **kw)
        self.fields['date'].widget.attrs = {'class':'vDateField'}
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

class CheckForm(forms.ModelForm):
    remarks = forms.CharField(widget=forms.Textarea(attrs={'cols':'14', 'rows':'3'}), required = False ,
                              label=ugettext('remarks'))
    new_expense_type = forms.CharField(label = ugettext('new_expense_type'), max_length = 20, required=False)
    def save(self, account=None, *args, **kw):
        if account:
            self.instance.account = acccount
        expense_type = self.cleaned_data['new_expense_type']
        if expense_type:
            et = ExpenseType(name=expense_type)
            et.save()
            self.instance.expense_type = et
        forms.ModelForm.save(self, *args, **kw)
    class Meta:
        model = Check

class EmployeeCheckForm(forms.ModelForm):
    remarks = forms.CharField(widget=forms.Textarea(attrs={'cols':'20', 'rows':'3'}), required = False ,
                              label=ugettext('remarks'))
    class Meta:
        model = EmployeeCheck

class NHMonthForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        q = NHMonth.objects.filter(is_closed=False)
        if self.instance.id or q.count() == 0:
            return
        self.fields['year'].initial = q[0].year
        self.fields['month'].initial = q[0].month
    class Meta:
        model = NHMonth
        
class EmploymentTermsForm(forms.ModelForm):
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

class DemandReportForm(forms.Form):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('month'),
                              initial = Demand.current_month().month)

class ProjectSeasonForm(forms.Form):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    from_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('from_year'), initial = datetime.now().year)
    from_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('from_month'),
                              initial = Demand.current_month().month)
    to_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('to_year'), initial = datetime.now().year)
    to_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('to_month'),
                              initial = Demand.current_month().month)

class SeasonForm(forms.Form):
    from_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('from_year'), initial = datetime.now().year)
    from_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('from_month'),
                              initial = Demand.current_month().month)
    to_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('to_year'), initial = datetime.now().year)
    to_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('to_month'),
                              initial = Demand.current_month().month)

class NHBranchSeasonForm(forms.Form):
    nhbranch = forms.ModelChoiceField(queryset = NHBranch.objects.all(), label=ugettext('nhbranch'))
    from_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('from_year'), initial = datetime.now().year)
    from_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('from_month'),
                              initial = Demand.current_month().month)
    to_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('to_year'), initial = datetime.now().year)
    to_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('to_month'),
                              initial = Demand.current_month().month)

class EmployeeSeasonForm(forms.Form):
    employee = forms.ModelChoiceField(queryset = Employee.objects.all(), label=ugettext('employee'))
    from_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('from_year'), initial = datetime.now().year)
    from_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('from_month'),
                              initial = Demand.current_month().month)
    to_year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('to_year'), initial = datetime.now().year)
    to_month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('to_month'),
                              initial = Demand.current_month().month)
    
class MonthFilterForm(forms.Form):    
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('month'),
                              initial = Demand.current_month().month)

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

class LocateDemandForm(forms.Form):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('month'),
                              initial = datetime.now().month)
    
class LocateHouseForm(forms.Form):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    building_num = forms.IntegerField(widget=forms.TextInput(attrs={'size':'3'}),
                                      min_value=1, label=ugettext('building_num'))
    house_num = forms.IntegerField(widget=forms.TextInput(attrs={'size':'3'}),
                                   min_value=1, label=ugettext('house_num'))