from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView, DetailView, UpdateView
from django.urls import reverse_lazy

from holdings.models import Holding, Rate, Userrates
from holdings.forms import CreateForm, UpdateForm, RateCreateForm
from .stock_check import StockCheck


class HoldingListView(LoginRequiredMixin, ListView):
    model = Holding
    template_name = 'holdings/holding_list.html'

    def get_queryset(self):
        return Holding.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        holding_objects = Holding.objects.filter(owner=self.request.user)

        if holding_objects:
            total_value = sum([holding.value for holding in holding_objects])
            last = list(holding_objects.order_by('id'))[-1].updated_at
            holdings_names = [holding.ticker for holding in holding_objects]
            holdings_price = [float(holding.price) for holding in holding_objects]
            holdings_vals = [float(holding.value) for holding in holding_objects]

        else:
            total_value, last, holdings_names, holdings_price, holdings_vals = 0, '-', 0, 0, 0

        # load many-to-many joiner table 'Userrates' results for User
        userrate_objects = list(Userrates.objects.filter(user=self.request.user))
        currency_names = []
        exchange_rates = []
        symbols = []
        # iterate through each userrate for the current user
        for userrate in userrate_objects:
            # load the Rate linked to this joiner table entry
            rate = userrate.rate
            currency_names.append(str(rate.name))
            exchange_rates.append(float(rate.rate))
            symbols.append(str(rate.symbol))

        context = {'total_value': total_value,
                   'last_updated': last,
                   'exchange_rates': list(exchange_rates),
                   'currency_names': list(currency_names),
                   'symbols': list(symbols),
                   'rates_count': len(currency_names),
                   'holdings_names': holdings_names,
                   'holdings_price': holdings_price,
                   'holdings_vals': holdings_vals,
                   }
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
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        holding.value = round(float(holding.amt) * stock_price, 2)
        holding.save()
        return redirect(self.success_url)

class HoldingUpdateAllView(LoginRequiredMixin, View):
    success_url = 'holdings:all'

    def get(self, request):

        user_holdings = Holding.objects.filter(owner=self.request.user)
        userrates = Userrates.objects.filter(user=self.request.user)
        rates = [userrate.rate for userrate in userrates]
        holdings_list = [holding.ticker for holding in user_holdings]
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

class RateCreateView(LoginRequiredMixin, View):
    template_name = 'holdings/rate_form.html'
    success_url = reverse_lazy('holdings:all')

    def get(self, request, pk=None):
        form = RateCreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = RateCreateForm(request.POST)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        rate = form.save(commit=False)

        if len(rate.ticker) != 3:
            ctx = {'form': form, 'not_found': True}
            return render(request, self.template_name, ctx)

        # append =X to ticker for CURR/USD rate
        search_rate = rate.ticker + '=X'

        try:
            Rate.objects.get(ticker=search_rate)
        except:
            # create Rate if it does not already exist
            stock_check = StockCheck()
            exchange_rate = stock_check.add_rate(search_rate)
            print(exchange_rate)
            if not exchange_rate:
                ctx = {'form': form, 'not_found': True}
                return render(request, self.template_name, ctx)
            # first element of tuple is name, second is rate
            rate.name = exchange_rate[0]
            rate.rate = exchange_rate[1]
            rate.ticker = search_rate
            rate.save()
        # create Userrates linking User to Rate (many-to-many)
        userrate = Userrates(user=self.request.user, rate=Rate.objects.get(ticker=search_rate))
        userrate.save()
        return redirect(self.success_url)