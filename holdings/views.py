from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView, DetailView, UpdateView
from django.urls import reverse_lazy

from holdings.models import Holding, Rate
from holdings.forms import CreateForm, UpdateForm
from .stock_check import StockCheck

import json
# Create your views here.

class HoldingListView(LoginRequiredMixin, ListView):
    model = Holding
    template_name = 'holdings/holding_list.html'

    def get_queryset(self):
        return Holding.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        total_value = sum([holding.value for holding in Holding.objects.filter(owner=self.request.user)])
        last = list(Holding.objects.filter(owner=self.request.user).order_by('id'))[-1].updated_at

        rate_objects = Rate.objects.all()
        currency_names = []
        exchange_rates = []
        symbols = []
        for rate in rate_objects:
            currency_names.append(str(rate.name))
            exchange_rates.append(float(rate.rate))
            symbols.append(str(rate.symbol))

        context = {'total_value': total_value,
                   'last_updated': last,
                   'exchange_rates': list(exchange_rates),
                   'currency_names': list(currency_names),
                   'symbols': list(symbols),
                   'rates_count': len(currency_names)}
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
        rates = Rate.objects.all()
        holdings_list = [holding.ticker for holding in user_holdings]
        # holdings_list.append('GBP=X')
        # holdings_list.append('EUR=X')
        for rate in rates:
            holdings_list.append(rate.ticker)
        stock_check = StockCheck()
        holdings_dict = stock_check.update_all(holdings_list)
        for holding in user_holdings:
            holding.price = holdings_dict[holding.ticker]
            holding.value = round(float(holding.amt) * holdings_dict[holding.ticker], 2)
            holding.save()
        for rate in rates:
            rate.rate = holdings_dict[rate.ticker]
            rate.save()
        return redirect(self.success_url)

class HoldingDeleteView(LoginRequiredMixin, DeleteView):
    model = Holding
