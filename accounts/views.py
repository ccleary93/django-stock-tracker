from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.views import generic, View
from accounts.forms import LoginForm

# Create your views here.

class SignupView(generic.CreateView):
    print('hello')
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class CustomLoginView(View):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('holdings:all')

    def get(self, request, pk=None):
        form = LoginForm
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(self.success_url)
        else:
            form = LoginForm
            ctx = {'form': form, 'form.errors': True}
            return render(request, self.template_name, ctx)