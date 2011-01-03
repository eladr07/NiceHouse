from django.contrib import admin
from Management.models import *
from reversion.admin import VersionAdmin

admin.site.register(Tag)
admin.site.register(Project)
admin.site.register(Employee)
admin.site.register(Contact)
admin.site.register(House)
admin.site.register(HouseVersion)
admin.site.register(Building)
admin.site.register(Attachment)

class CVarPrecentageAdmin(VersionAdmin):
    list_display = CVarPrecentage.Meta.fields

admin.site.register(CVarPrecentage, CVarPrecentageAdmin)
admin.site.register(CVarPrecentageFixed, VersionAdmin)
admin.site.register(CVar, VersionAdmin)
admin.site.register(CByPrice, VersionAdmin)
admin.site.register(CZilber, VersionAdmin)