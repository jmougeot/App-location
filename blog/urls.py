from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.client_management, name='client_management'),
    path('nouveau_equipement/', views.nouveau_equipement, name='nouveau_equipement'),
    path('client/<int:pk>/', views.client_detail, name='client_detail'),
    path('equipement/<int:pk>/', views.equipement_detail, name='equipement_detail'),
    path('nouveau_client/', views.nouveau_client, name='nouveau_client'),
    path('equipement/<int:pk>/emprunter/', views.emprunter_equipement, name='emprunter_equipement'),
    path('equipement/<int:pk>/retourner/', views.retourner_equipement, name='retourner_equipement'),
path('equipement/<int:pk>/supprimer/', views.supprimer_equipement, name='supprimer_equipement'),    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)