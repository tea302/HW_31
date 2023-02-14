from django.urls import path

from ads import views

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('<int:pk>', views.CategoryDetailView.as_view(), name='category_detail'),
    path('create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
