import json
from datetime import datetime

from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render
from django.views import View

from admin_panel.forms import DeclarationForm
from admin_panel.models import ChatMessage, FruitStorage, Bank, OperationJournal, Declaration
from users.forms import MyAuthenticationForm


# Create your views here.
def main(request):
    today = datetime.today()
    chat_messages = ChatMessage.objects.order_by('timestamp')
    if chat_messages.count() > 40:
        chat_messages = chat_messages[:40:-1]
    storage = Bank.objects.first()
    fruits = FruitStorage.objects.prefetch_related('operations').all()
    operations = OperationJournal.objects.all()[:40]
    form = MyAuthenticationForm()
    declaration_form = DeclarationForm()
    declaration_count = Declaration.objects.filter(timestamp__day=today.day, timestamp__month=today.month,
                                       timestamp__year=today.year).count()
    data = {
        'declaration_count': declaration_count,
        'declaration_form': declaration_form,
        'form': form,
        'fruits': fruits,
        'operations': operations,
        'chat_messages': chat_messages,
        'balance': storage.balance,
    }
    return render(request, 'admin_panel/main.html', context=data)


class UploadDeclarationView(View):
    def post(self, request):
        today = datetime.today()
        declaration_form = DeclarationForm(request.POST, request.FILES)
        if declaration_form.is_valid():
            declaration_form.save()
        count = Declaration.objects.filter(timestamp__day=today.day, timestamp__month=today.month,
                                           timestamp__year=today.year).count()
        data = {
            'count': count
        }
        return JsonResponse(json.dumps(data), safe=False)
