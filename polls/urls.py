from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^today/$', views.index, name='today'),
    url(r'^create_restaurant/(?P<r_name>[a-zA-Z0-9_-]+)$', views.create_restaurant, name='create_r'),
    url(r'^create_employee/(?P<e_name>[a-zA-Z0-9]+)$', views.create_employee, name='create_e'),
    url(r'^menu/(?P<r_id>[0-9]+)$', views.upload_menu, name='upload'),
    url(r'^view_menu/(?P<m_id>[0-9]+)$', views.download_menu, name='dwnl_menu'),
    url(r'^vote/(?P<r_id>[0-9]+)/(?P<e_id>[0-9]+)$', views.vote_for_restaurant_menu, name='vote_for'),
    url(r'^winner/$', views.todays_result, name='winner'),
]