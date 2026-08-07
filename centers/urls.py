from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('map/', views.map_view, name='map_view'),
    path('api/centers.geojson', views.centers_geojson, name='centers_geojson'),
    path('add/', views.add_center, name='add_center'),
    path('api/search.geojson', views.search_centers, name='search_centers'),
    path('export/geojson/', views.export_geojson, name='export_geojson'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('report/', views.city_report_view, name='city_report'),
]
