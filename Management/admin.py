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
    list_display = get_fields_names(Employee)
    list_filter = ('rank',)
    
class ProjectAdmin(admin.ModelAdmin):
    list_display = get_fields_names(Project)

class CVarPrecentageAdmin(VersionAdmin):
    list_display = get_fields_names(CVarPrecentage)
    
class CVarPrecentageFixedAdmin(VersionAdmin):
    list_display = get_fields_names(CVarPrecentageFixed)
    
class CVarAdmin(VersionAdmin):
    list_display = get_fields_names(CVar)

admin.site.register(Project, ProjectAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(CVarPrecentage, CVarPrecentageAdmin)
admin.site.register(CVarPrecentageFixed, CVarPrecentageFixedAdmin)
admin.site.register(CVar, CVarAdmin)
admin.site.register(CByPrice, VersionAdmin)
admin.site.register(CZilber, VersionAdmin)