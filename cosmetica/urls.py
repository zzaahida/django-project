from django.urls import path
from django.views.decorators.cache import cache_page

from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path("search/", cache_page(60)(SearchView.as_view()), name="search"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('cart/', CartPageView.as_view(), name="cart"),
    path("manager-cart/<int:cp_id>/", ManagerCartView.as_view(), name="manager_cart"),
    path('buy/all/product/', bylAllInCart, name="buyAllProduct"),
    path('update/money/', updateUserMoney, name="updateMoney"),
    path('category/<slug:slug>/', CategoryView.as_view(), name="category"),
    path('category/<slug:cat_slug>/<slug:slug>', ProductShowView.as_view(), name='product_details'),
    path('auth/register/', Register.as_view(), name="myRegister"),
    path('auth/login/', LoginUser.as_view(), name="myLogin"),
    path('auth/logout/', my_user_logout, name="myLogout"),
]
