from django.contrib import admin

# Register your models here.
from .models import Profile, Education, Employment, Partner, PartnerAdmin, Program, Scholar, Application

admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(Employment)
admin.site.register(Partner)
admin.site.register(PartnerAdmin)
admin.site.register(Program)
admin.site.register(Scholar)
admin.site.register(Application)