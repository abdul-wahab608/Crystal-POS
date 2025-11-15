from django.contrib import admin
from .models import Vendor, VendorTransaction, VendorProduct

# Register your models here.
admin.site.register(Vendor)
admin.site.register(VendorTransaction)
admin.site.register(VendorProduct)
