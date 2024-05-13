from django.urls import path
from . import views

urlpatterns = [
    path('start_page/', views.start_page, name='start_page'),
    path('session_login/', views.session_login, name='session_login'),
    path('factor_matrix/', views.factor_matrix, name='factor_matrix'),
    path('sw_impact/', views.sw_impact, name='sw_impact'),
    path('sw_impact_out/', views.sw_impact_out, name='sw_impact_out'),
    path('ot_impact/', views.ot_impact, name='ot_impact'),
    path('ot_impact_out/', views.ot_impact_out, name='ot_impact_out'),
    path('possibilities/', views.possibilities, name='possibilities'),
    path('result/', views.result, name='result'),
    path('result_out/', views.result_out, name='result_out'),
    path('room_handler/', views.room_handler, name='room_handler'),
    path('validate_session/', views.validate_session, name='validate_session'),
    path('', views.redirect_view)
]