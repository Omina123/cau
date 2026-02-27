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
    path('stations', views.stations, name='stations'),
    path('groups', views.groups, name='groups'),
]
