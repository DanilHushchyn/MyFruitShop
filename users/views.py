from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View

from admin_panel.forms import DeclarationForm
from admin_panel.models import FruitStorage, OperationJournal, Bank, ChatMessage
from admin_panel.views import main
from users.forms import MyAuthenticationForm


class MyLoginView(View):
    form_class = MyAuthenticationForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, 'admin_panel/main.html', context={'form': form, 'message': message})

    def post(self, request):
        form = self.form_class(data=request.POST)
        if form.is_valid():

            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('main')
        messages.error(request, 'Неправильно указан username или password')
        return main(request)
