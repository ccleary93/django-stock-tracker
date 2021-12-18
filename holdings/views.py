from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView, DetailView, UpdateView
from django.urls import reverse_lazy

from holdings.models import Holding
from holdings.forms import CreateForm, UpdateForm
from .stock_check import StockCheck
# Create your views here.

class HoldingListView(LoginRequiredMixin, ListView):
    model = Holding
    #template_name = 'holdings/holding_list.html'
    
class HoldingDetailView(DetailView):
    model = Holding

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
        print(stock_price)
        if not stock_price:
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

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
        holding.save()
        return redirect(self.success_url)
        
    
class HoldingDeleteView(LoginRequiredMixin, DeleteView):
    model = Holding