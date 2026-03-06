from django.contrib import admin
from django.urls import path
from  Ngoiso import views

urlpatterns = [
    path('', views.home, name= 'home'),
    path('about', views.about, name= 'about'),
    path('Contact', views.Contact, name= 'Contact'),
    path('sadaka', views.sadaka, name= 'sadaka'),
    path('zaka', views.zaka, name= 'zaka'),
    path('mavuno', views.mavuno, name= 'mavuno'),
    path('Special', views.Special, name= 'Special'),
    path('Dashbd', views.Dashbd, name= 'Dashbd'),
    path('register_member', views.register_member, name='register_member'),
    path('ajax/load-outstations/', views.load_outstations, name='ajax_load_outstations'),
    path('ajax/load-jumuiya/', views.load_jumuiya, name='ajax_load_jumuiya'),
    path('jumuiya', views.jumuiya, name='jumuiya'),
    path('Gallary', views.Gallary, name='Gallary'),
    path('pledge', views.pledge_view, name='pledge_view'),
    path('jumuiya_contribution', views.jumuiya_contribution, name='jumuiya_contribution'),  
    # path('mavuno_pdf_report', views.mavuno_pdf_report, name='mavuno_pdf_report'),
    path('out_station', views.out_station, name='out_station'),
    path('outstation/<int:pk>/', views.outstation, name='outstation'),
   path ('assign_outstation/<int:catechist_id>/', views.assign_outstation, name='assign_outstation'),
   path('catechists/', views.catechist_list, name='catechist_list'),
    
    #from 
    path('jumu_report', views.jumu_report, name='jumu_report'),
    path('mon_report', views.mon_report, name='mon_report'),
    path('zak_report', views.zak_report, name='zak_report'),
    path('mavreport', views.mavreport, name='mavreport'),
    path('sadreport', views.sadreport, name='sadreport'),
        
path('outstation/<int:outstation_id>/zakao/', views.zakao, name='zakao'),   
path('stations', views.stations, name='stations'),
#path('catechist_reports', views.catechist_reports, name='catechist_reports'),
path('groups', views.groups, name='groups'),
path('station_INT', views.station_INT, name='station_INT'),
path('catechist_dashboard', views.catechist_dashboard, name='catechist_dashboard'),
path ('parish_mavuno_report', views.parish_mavuno_report, name='parish_mavuno_report'),
path('parish_special_report', views.parish_special_report, name='parish_special_report'),
path('parish_zaka_report', views.parish_zaka_report, name='parish_zaka_report'),
path('Admin', views.Admin, name='Admin'),
path('StaffDashboard', views.StaffDashboard, name='StaffDashboard'),
path('outstation/<int:outstation_id>/specials/', views.special_report, name='special_report'),
path('outstation/<int:outstation_id>/mavuno/', views.mavuno_report, name='mavuno_report'),
]
