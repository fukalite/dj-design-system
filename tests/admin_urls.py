"""Two admin sites over the same models: one stock, one using the design system."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import path

from dj_design_system.contrib.django_admin.sites import DesignSystemAdminSite


class UserAdmin(admin.ModelAdmin):
    list_display = ["username"]
    list_filter = ["is_staff"]
    search_fields = ["username"]
    list_per_page = 2
    list_max_show_all = 100
    ordering = ["username"]


stock_site = admin.AdminSite(name="stock_admin")
stock_site.register(get_user_model(), UserAdmin)

dds_site = DesignSystemAdminSite(name="dds_admin")
dds_site.register(get_user_model(), UserAdmin)

urlpatterns = [
    path("stock-admin/", stock_site.urls),
    path("dds-admin/", dds_site.urls),
]
