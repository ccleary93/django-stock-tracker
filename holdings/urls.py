from django.urls import path, reverse_lazy
from . import views

app_name = 'holdings'
urlpatterns = [
    path('', views.HoldingListView.as_view(), name='all'),
    path('holding/create', views.HoldingCreateView.as_view(success_url=reverse_lazy('holdings:all')), name='holding_create'),
    path('holding/<int:pk>/update', views.HoldingUpdateView.as_view(success_url=reverse_lazy('holdings:all')), name='holding_update'),
    path('holding/<int:pk>/updateprice', views.HoldingUpdatePriceView.as_view(success_url=reverse_lazy('holdings:all')), name='holding_update_price'),
    path('holding/updateall', views.HoldingUpdateAllView.as_view(success_url=reverse_lazy('holdings:all')), name='holding_update_all'),
    path('holding/<int:pk>/delete', views.HoldingDeleteView.as_view(success_url=reverse_lazy('holdings:all')), name='holding_delete'),
]