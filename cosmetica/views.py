from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from cosmetica.forms import RegisterForm
from cosmetica.models import Product, Category, Cart
from cosmetica.serializers import ProductSerializer, UserSerializer
from cosmetica.utils import DataMixin


def pageNotFound(request, exeption):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


class IndexView(DataMixin, ListView):
    paginate_by = 3
    model = Product
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        list_exam = Product.objects.all()
        paginator = Paginator(list_exam, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            file_exams = paginator.page(page)
        except PageNotAnInteger:
            file_exams = paginator.page(1)
        except EmptyPage:
            file_exams = paginator.page(paginator.num_pages)
        context['object_list'] = file_exams
        context = super().get_context_data(**kwargs)
        mixin = self.get_user_context(title="index")
        return dict(list(context.items()) + list(mixin.items()))

    def get_queryset(self):
        return Product.objects.select_related("category")


class AboutView(DataMixin, TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        return self.get_user_context(title="about page")


class ProductShowView(DataMixin, DetailView):
    model = Product
    template_name = "product_show.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mixin = self.get_user_context(title=context.get("product").title)
        return dict(list(context.items()) + list(mixin.items()))

    def post(self, request, **kwargs):
        my_data = request.POST
        user = request.user
        newCart = Cart()
        newCart.user = user
        newCart.product = Product.objects.get(pk=my_data.get("product_id", None))
        newCart.save()
        return redirect('cart')


class CategoryView(DataMixin, DetailView):
    model = Category
    template_name = "category.html"

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        activ = self.rel()

        context['rel'] = activ
        context['page_obj'] = activ
        mixin = self.get_user_context(title="category")
        return dict(list(context.items()) + list(mixin.items()))

    def rel(self):
        queryset = self.object.product_set.all()
        paginator = Paginator(queryset, 4)
        page = self.request.GET.get('page')
        activities = paginator.get_page(page)
        return activities


class SearchView(DataMixin, TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        results = Product.objects.filter(
            Q(title__icontains=kw) | Q(description__icontains=kw))
        print(results)
        context["results"] = results
        mixin = self.get_user_context(title="search")
        return dict(list(context.items()) + list(mixin.items()))


class ProfileView(DataMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        cart = Cart.objects.select_related("user").select_related("product").filter(user=user, status=True).all()
        totalSum = 0
        for i in cart:
            totalSum += i.product.selling_price * i.count
        context = super().get_context_data(**kwargs)
        context["total_summa"] = totalSum
        context["cart_items"] = cart
        mixin = self.get_user_context(title=f"profile {self.request.user}")
        return dict(list(context.items()) + list(mixin.items()))


class Register(DataMixin, CreateView):
    pass
    form_class = RegisterForm
    template_name = "registration.html"
    success_url = reverse_lazy('myLogin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mixin = self.get_user_context(title="registration")
        return dict(list(context.items()) + list(mixin.items()))


#
#
class LoginUser(DataMixin, LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mixin = self.get_user_context(title="login")
        return dict(list(context.items()) + list(mixin.items()))


class CartPageView(DataMixin, ListView):
    template_name = "mycart.html"
    model = Cart

    def get_queryset(self):
        user = self.request.user
        cart = Cart.objects.select_related("user").select_related("product").filter(user=user, status=False).all()
        return cart

    def get_context_data(self, **kwargs):
        totalSum = 0
        for i in self.object_list:
            totalSum += i.product.selling_price * i.count
        context = super().get_context_data(**kwargs)
        context["total_summa"] = totalSum
        mixin = self.get_user_context(title="cart")
        return dict(list(context.items()) + list(mixin.items()))

    def post(self, request, **kwargs):
        cart = request.POST.get("cart_id", None)
        if cart:
            Cart.objects.get(pk=cart).delete()
            messages.error(request, "товар удалено")
        else:
            return HttpResponseNotFound

        return redirect('cart')


@login_required
def my_user_logout(request):
    logout(request)
    messages.info(request, "успешно")
    return redirect("/")


def bylAllInCart(request):
    if request.method == "POST":
        userItems = Cart.objects.select_related("product").select_related("product__category").filter(user=request.user, status=False).all()
        itemsMoney = 0
        for i in userItems:
            itemsMoney += i.product.selling_price
        if request.user.money > itemsMoney:
            Cart.objects.filter(user=request.user, status=False).all().order_by('product').update(status=True)
            request.user.money = request.user.money - itemsMoney
            request.user.save()
        else:
            messages.error(request, "денег не хватает")
            return redirect('cart')
        messages.info(request, "вы успешно купили")
        return redirect('profile')


def updateUserMoney(request):
    if request.method == "POST":
        req = request.POST.get("money", None)
        if req is not None:
            request.user.money = request.user.money + int(req)
            request.user.save()
        return redirect('profile')


class ManagerCartView(View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = Cart.objects.get(id=cp_id)
        if action == "inc":
            cp_obj.count += 1
            cp_obj.save()
        elif action == "dcr":
            cp_obj.count -= 1
            cp_obj.save()
            if cp_obj.count == 0:
                cp_obj.delete()
        elif action == "rmv":
            cp_obj.delete()
        else:
            return redirect("cart")
        return redirect("cart")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action == 'post' or self.action == 'put' or self.action == 'delete':
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
