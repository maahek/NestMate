from django.contrib import admin

# Django admin works with SQL models only.
# MongoDB models are managed via the custom admin dashboard below.
# The custom dashboard is at: http://localhost:3000/admin-dashboard

admin.site.site_header  = 'NestMate Administration'
admin.site.site_title   = 'NestMate Admin'
admin.site.index_title  = 'Welcome to NestMate Admin Panel'