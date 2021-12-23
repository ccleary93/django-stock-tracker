from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView, DetailView, UpdateView
from django.urls import reverse_lazy

from holdings.models import Holding
from holdings.forms import CreateForm, UpdateForm
from .stock_check import StockCheck
# Create your views here.

class HoldingListView(LoginRequiredMixin, ListView):
    model = Holding
    template_name = 'holdings/holding_list.html'

    def get_queryset(self):
        return Holding.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        total_value = sum([holding.value for holding in Holding.objects.filter(owner=self.request.user)])
        context = {'total_value': total_value}
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class HoldingCreateView(LoginRequiredMixin, View):
    template_name = 'holdings/holding_form.html'
    success_url = reverse_lazy('holdings:all')
    
    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form':form}
        return render(request, self.template_name, ctx)
        
    def post(self, request, pk=None):
        form = CreateForm(request.POST)
        
        if not form.is_valid():
            ctx = {'form':form}
            return render(request, self.template_name, ctx)

        holding = form.save(commit=False)

        stock_check = StockCheck()
        stock_price = stock_check.price_check(holding.ticker)
        if not stock_price:
            ctx = {'form': form, 'not_found': True}
            return render(request, self.template_name, ctx)

        holding.price = stock_price
        holding.value = round(float(holding.amt) * stock_price, 2)
        holding.owner = self.request.user
        holding.save()
        return redirect(self.success_url)
    
class HoldingUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'holdings/holding_form.html'
    success_url = reverse_lazy('holdings:all')
    
    def get(self, request, pk):
        holding = get_object_or_404(Holding, id=pk, owner=self.request.user)
        form = UpdateForm(instance=holding)
        ctx = {'form':form}
        return render(request, self.template_name, ctx)
        
    def post(self, request, pk=None):
        holding = get_object_or_404(Holding, id=pk, owner=self.request.user)
        form = UpdateForm(request.POST, instance=holding)
        
        if not form.is_valid():
            ctx = {'form':form}
            return render(request, self.template_name, ctx)
            
        holding = form.save(commit=False)
        stock_check = StockCheck()
        stock_price = stock_check.price_check(holding.ticker)

        if not stock_price:
            ctx = {'form': form, 'api_calls_exceeded': True}
            return render(request, self.template_name, ctx)

        holding.value = round(float(holding.amt) * stock_price, 2)
        holding.save()
        return redirect(self.success_url)
        
class HoldingUpdatePriceView(LoginRequiredMixin, View):
    success_url = 'holdings: all'

    def get(self, request, pk):
        holding = get_object_or_404(Holding, id=pk, owner=self.request.user)
        stock_check = StockCheck()
        stock_price = stock_check.price_check(holding.ticker)
        holding.value = round(float(holding.amt) * stock_price, 2)
        holding.save()
        return redirect(self.success_url)

class HoldingUpdateAllView(LoginRequiredMixin, View):
    success_url = 'holdings:all'

    def get(self, request):
        user_holdings = Holding.objects.filter(owner=self.request.user)
        holdings_list = [holding.ticker for holding in user_holdings]
        stock_check = StockCheck()
        holdings_dict = stock_check.update_all(holdings_list)
        for holding in user_holdings:
            holding.price = holdings_dict[holding.ticker]
            holding.value = round(float(holding.amt) * holdings_dict[holding.ticker], 2)
            holding.save()
        return redirect(self.success_url)

class HoldingDeleteView(LoginRequiredMixin, DeleteView):
    model = Holding
