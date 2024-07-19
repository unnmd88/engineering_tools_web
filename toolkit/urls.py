from django.urls import path, re_path, register_converter
from . import views
from . import converters

register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path("manage_snmp/", views.manage_snmp, name='manage_snmp'),
    path("login/", views.login, name='login'),
    path("contact/", views.contact, name='contact'),
    path("options/", views.options, name='options'),
    path("post/<int:post_id>/", views.show_tab, name='post'),



    # path('toolkit/', views.index, name='toolkit'),
    # path('tabs/<int:tabs_id>/', views.tabs, name='tabs_id'), # http://127.0.0.1:8000/tabs/1/
    # path('tabs/<slug:tabs_slug>/', views.tabs_by_slug, name='tabs_slug'),  # http://127.0.0.1:8000/tabs/1/
    # path("archive/<year4:year>/", views.archive, name='archive'),

]