from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import CartViewSet, DiscountApiView

router = DefaultRouter()
router.register('carts', CartViewSet, 'cart')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/discount/', DiscountApiView.as_view(), name='discount-view')
]