import django.forms as forms
import sys
from django.utils.translation import ugettext
from django.forms.formsets import formset_factory
from models import *
from datetime import datetime

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
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'5'})
        self.fields['settle_date'].widget = forms.TextInput({'class':'vDateField'})
    class Meta:
        model = Pricelist

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
    def save(self, *args, **kw):
        h = forms.ModelForm.save(self, *args, **kw)
        for f in ['parking1','parking2','parking3']:
            if self.cleaned_data[f]:
                h.parkings.add(self.cleaned_data[f])
        for f in ['storage1','storage2']:
            if self.cleaned_data[f]:
                h.storages.add(self.cleaned_data[f])
        if self.cleaned_data['price']:
            self.instance.versions.add(HouseVersion(house=h, type=PricelistType.objects.get(pk=self.price_type_id),
                                                    price = self.cleaned_data['price']))
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
        self.price_type_id = price_type_id
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
        
class SaleForm(forms.ModelForm):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    building = forms.ModelChoiceField(queryset = Building.objects.all(), label=ugettext('building'))
    def save(self, *args, **kw):
        if not self.instance.id and self.cleaned_data['house'].get_sale() != None:
            raise AttributeError
        allowed_discount = self.cleaned_data['allowed_discount']
        '''checks if entered a allowed discount but not discount -> will fill
        discount automatically'''
        if allowed_discount and not self.cleaned_data['discount']:
            max_p = self.cleaned_data['house'].versions.filter(type__id = PricelistTypeCompany).latest().price
            min_p = max_p * (1 - allowed_discount/100)
            price = self.cleaned_data['price']
            self.cleaned_data['discount'] = 100 - (100 / float(max_p) * price)
            self.cleaned_data['contract_num'] = 0
        return forms.ModelForm.save(self, *args, **kw)
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
        self.fields['clients'].widget = forms.Textarea({'cols':'20', 'rows':'3'})
        self.fields['sale_date'].widget = forms.TextInput({'class':'vDateField'})
        if self.instance.id:
            self.fields['project'].initial = self.instance.house.building.project.id
            self.fields['building'].initial = self.instance.house.building.id
            self.fields['house'].initial = self.instance.house.id
            self.fields['building'].queryset = self.instance.house.building.project.buildings.all()
            self.fields['house'].queryset = self.instance.house.building.houses.all()           
    class Meta:
        model = Sale
        
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
        
class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['payment_date'].widget.attrs = {'class':'vDateField'}
    class Meta:
        model = Payment

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
    class Meta:
        model = NHSale

class NHSaleSideForm(forms.ModelForm):
    employee1_commission = forms.FloatField(label=ugettext('commission_precent'))
    employee2_commission = forms.FloatField(label=ugettext('commission_precent'), required=False)
    director_commission = forms.FloatField(label=ugettext('commission_precent'), required=False)
    lawyer1_pay = forms.FloatField(label=ugettext('lawyer_pay'))
    lawyer2_pay = forms.FloatField(label=ugettext('lawyer_pay'), required=False)
    def save(self, *args, **kw):
        e1, e2, d = (self.cleaned_data['employee1'], self.cleaned_data['employee2'],
                     self.cleaned_data['director'])
        ec1, ec2, dc = (self.cleaned_data['employee1_commission'], self.cleaned_data['employee2_commission'],
                        self.cleaned_data['director_commission'])
        l1, l2 = (self.cleaned_data['lawyer1'], self.cleaned_data['lawyer2'])
        lp1, lp2 = (self.cleaned_data['lawyer1_pay'], self.cleaned_data['lawyer2_pay'])
        side = forms.ModelForm.save(self, *args,**kw)
        nhsale = side.nhsale
        if e1 and ec1:
            nhp = e1.nhpays.get_or_create(nhsale = nhsale)[0]
            nhp.amount = nhsale.price * ec1 / 100
            nhp.save()
        if e2 and ec2:
            nhp = e2.nhpays.get_or_create(nhsale = nhsale)[0]
            nhp.amount = nhsale.price * ec2 / 100
            nhp.save()
        if d and dc:
            nhp = d.nhpays.get_or_create(nhsale = nhsale)[0]
            nhp.amount = nhsale.price * ec2 / 100
            nhp.save()
        if l1 and lp1:
            nhp = l1.nhpays.get_or_create(nhsale = nhsale)[0]
            nhp.amount = lp1
            nhp.save()
        if l2 and lp2:
            nhp = l2.nhpays.get_or_create(nhsale = nhsale)[0]
            nhp.amount = lp2
            nhp.save()
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'20', 'rows':'3'})
        self.fields['voucher_date'].widget.attrs = {'class':'vDateField'}
        if self.instance.id:
            nhsale = self.instance.nhsale
            if self.instance.employee1:
                pays = self.employee1.pays.filter(nhsale=nhsale)
                self.fields['employee1_commission'].initial = pays[0] / nhsale.price * 100
            if self.instance.employee2:
                pays = self.employee2.pays.filter(nhsale=nhsale)
                self.fields['employee2_commission'].initial = pays[0] / nhsale.price * 100
            if self.instance.lawyer1:
                pays = self.lawyer1.pays.filter(nhsale=nhsale)
                self.fields['lawyer1_pay'].initial = pays[0]
            if self.instance.lawyer2:
                pays = self.lawyer2.pays.filter(nhsale=nhsale)
                self.fields['lawyer2_pay'].initial = pays[0]
    class Meta:
        model = NHSaleSide

class AdvancePaymentForm(forms.ModelForm):
    class Meta:
        model = AdvancePayment

class LoanForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['remarks'].widget = forms.Textarea(attrs={'cols':'30', 'rows':'6'})
    class Meta:
        model= Loan

class DemandSendForm(forms.ModelForm):
    is_finished = forms.BooleanField()
    by_mail = forms.BooleanField()
    mail = forms.EmailField(required=False)
    by_fax = forms.BooleanField()
    fax = forms.CharField(max_length=20, required=False)
    class Meta:
        model = Demand
        fields = ['id']
        
class LoanPayForm(forms.ModelForm):
    class Meta:
        model = LoanPay
        
class ReminderForm(forms.ModelForm):
    status = forms.ModelChoiceField(queryset=ReminderStatusType.objects.all(), label=ugettext('status'))
    def save(self, *args, **kw):
        r = forms.ModelForm.save(self, *args, **kw)
        r.statuses.create(type=self.cleaned_data['status'])
        return r
    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self,*args,**kw)
        self.fields['content'].widget = forms.Textarea(attrs={'cols':'30', 'rows':'6'})
    class Meta:
        model = Reminder
        
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        
class LinkForm(forms.ModelForm):
    class Meta:
        model = Link

class CarForm(forms.ModelForm):
    class Meta:
        model = Car

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
        
class EmploymentTermsForm(forms.ModelForm):
    class Meta:
        model = EmploymentTerms

class DemandRemarksForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields= ('remarks',)

class EmployeeSalaryRemarksForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields= ('employee', 'remarks')

class EmployeeSalaryRefundForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields= ('employee', 'refund','refund_type')

class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(initial = 'undone', choices = [('done', 'בוצעו'), ('undone','לא בוצעו'), ('all','הכל')])
    sender = forms.ChoiceField(initial = 'others', choices = [('me', 'אני שלחתי'), ('others','נשלחו אלי')])

class DemandReportForm(forms.Form):
    project = forms.ModelChoiceField(queryset = Project.objects.all(), label=ugettext('project'))
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('month'),
                              initial = demand_month().month)

class MonthFilterForm(forms.Form):    
    year = forms.ChoiceField(choices=((i,i) for i in range(datetime.now().year - 10, datetime.now().year+10)), 
                             label = ugettext('year'), initial = datetime.now().year)
    month = forms.ChoiceField(choices=((i,i) for i in range(1,13)), label = ugettext('month'),
                              initial = demand_month().month)

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