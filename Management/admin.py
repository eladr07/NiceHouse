from django.contrib import admin
from Management.models import *
from reversion.admin import VersionAdmin
from inspect import isclass

admin.site.register(Tag)
admin.site.register(Contact)
admin.site.register(House)
admin.site.register(HouseVersion)
admin.site.register(Building)
admin.site.register(Attachment)

def get_fields_names(model):
    return [field.name for field in model._meta.fields]

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','pid','work_start','work_end')
    list_filter = ('rank',)
    
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','initiator','city','hood','start_date','end_date')
    list_filter = ('initiator',)

class CPrecentageInline(admin.StackedInline):
    model = CPrecentage
    
class CAmountInline(admin.StackedInline):
    model = CAmount
    
class CPriceAmountInline(admin.StackedInline):
    model = CPriceAmount

class CVarPrecentageAdmin(VersionAdmin):
    list_display = get_fields_names(CVarPrecentage)
    inlines = [CPrecentageInline]
    
class CVarPrecentageFixedAdmin(VersionAdmin):
    list_display = get_fields_names(CVarPrecentageFixed)
    
class CVarAdmin(VersionAdmin):
    list_display = get_fields_names(CVar)
    inlines = [CAmount]
    
class CByPriceAdmin(VersionAdmin):
    list_display = get_fields_names(CByPrice)
    inlines = [CPriceAmountInline]
    
class CZilberAdmin(VersionAdmin):
    list_display = get_fields_names(CZilber)
    
class DemandStatusInline(admin.TabularInline):
    model = DemandStatus
    
class DemandDiffInline(admin.TabularInline):
    model = DemandDiff
    
class DemandAdmin(admin.ModelAdmin):
    list_display = get_fields_names(Demand)
    inlines = [DemandStatusInline, DemandDiffInline]
    
class SaleCommissionDetailAdmin(admin.TabularInline):
    model = SaleCommissionDetail

class SaleHouseModInline(admin.TabularInline):
    model = SaleHouseMod
    
class SalePriceModInline(admin.TabularInline):
    model = SalePriceMod
    
class SalePreInline(admin.TabularInline):
    model = SalePre
    
class SaleRejectInline(admin.TabularInline):
    model = SaleReject
    
class SaleCancelInline(admin.TabularInline):
    model = SaleCancel
    
class SaleAdmin(admin.ModelAdmin):
    list_display = get_fields_names(Sale)
    inlines = [SaleCommissionDetailAdmin, SaleHouseModInline, SalePriceModInline, SalePreInline, SaleRejectInline, SaleCancelInline]

admin.site.register(Project, ProjectAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(CVarPrecentage, CVarPrecentageAdmin)
admin.site.register(CVarPrecentageFixed, CVarPrecentageFixedAdmin)
admin.site.register(CVar, CVarAdmin)
admin.site.register(CByPrice, CByPriceAdmin)
admin.site.register(CZilber, CZilberAdmin)
admin.site.register(Demand, DemandAdmin)
admin.site.register(Sale, SaleAdmin)