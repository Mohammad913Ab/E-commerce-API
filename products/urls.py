from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('product/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('product/<int:pk>/like/', views.ProductLikeCreateView.as_view(), name='product-like'),
    path('product/<int:pk>/comment/', views.ProductCommentCreateView.as_view(), name='product-comment'),
]
