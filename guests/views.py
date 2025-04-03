from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import Guest
from .forms import GuestForm, GuestCheckInForm, GuestFilterForm
from django.db import models
from django.contrib import messages

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.messages import get_messages

# guests/views.py
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseBadRequest
from django.contrib import messages
from .models import ConfirmationLink

# guests/views.py
from django.http import JsonResponse

# guests/views.py
from django.views.generic import DetailView

class GuestConfirmationDetailView(DetailView):
    model = Guest
    template_name = 'guest_confirmation_detail.html'
    context_object_name = 'guest'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['confirmation_history'] = self.object.get_confirmation_history()
        context['all_links'] = self.object.get_all_links()
        return context

def guest_confirmation_dashboard(request):
    guests = Guest.objects.annotate(
        last_confirmation_date=models.Max('confirmationlink__used_at')
    ).order_by('-last_confirmation_date')
    
    return render(request, 'confirmation_dashboard.html', {
        'guests': guests
    })

def generate_confirmation_links(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    links = guest.generate_confirmation_links(1)
    
    message = f"Olá {guest.name},\n\nPor favor, confirme sua presença no nosso evento acessando o link abaixo:\n\n"
    message += "\n".join([link['url'] for link in links])
    message += "\n\nAtenciosamente,\nOrganização do Evento"
    
    # Armazena na sessão apenas como backup
    request.session['confirmation_message'] = message
    
    return JsonResponse({
        'success': True,
        'guest_name': guest.name,
        'message': message,
        'links': [link['url'] for link in links]
    })

def confirm_presence(request, token):
    confirmation = get_object_or_404(ConfirmationLink, token=token)
    
    if not confirmation.is_valid():
        return HttpResponseBadRequest("Este link de confirmação já foi utilizado ou expirou.")
    
    if request.method == 'POST':
        if confirmation.confirm():
            confirmation.guest.checked_in = True
            confirmation.guest.save()
            return render(request, 'confirmation_success.html', {
                'guest': confirmation.guest
            })
        return HttpResponseBadRequest("Não foi possível confirmar a presença.")
    
    return render(request, 'confirm_presence.html', {
        'guest': confirmation.guest,
        'token': token
    })


@require_POST
def toggle_check_in(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    guest.checked_in = not guest.checked_in
    if guest.checked_in:
        guest.companions_checked_in = guest.companions
        messages.success(request, f"{guest.name} foi marcado como presente.")
    else:
        guest.companions_checked_in = 0
        messages.warning(request, f"{guest.name} foi marcado como ausente.")
    guest.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'checked_in': guest.checked_in,
            'companions_checked_in': guest.companions_checked_in,
            'messages': get_messages_json(request)
        })
    
    return redirect('guest_list')



def add_guest(request):
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Convidado adicionado com sucesso!")
            return redirect('guest_list')
        else:
            messages.error(request, "Erro ao adicionar o convidado. Verifique os dados.")
    else:
        form = GuestForm()
    return render(request, 'add_guest.html', {'form': form})


class GuestListView(ListView):
    model = Guest
    template_name = 'guest_list.html'
    context_object_name = 'guests'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(models.Q(name__icontains=search) | models.Q(code__icontains=search))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = GuestFilterForm(self.request.GET or None)
        return context


def check_in_out(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == 'POST':
        form = GuestCheckInForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            messages.success(request, "Check-in atualizado com sucesso!")
            return redirect('guest_list')
        else:
            messages.error(request, "Erro ao atualizar o check-in.")
    else:
        form = GuestCheckInForm(instance=guest)
    return render(request, 'check_in_out.html', {'form': form, 'guest': guest})

def get_messages_json(request):
    """Retorna mensagens do Django como JSON."""
    storage = get_messages(request)
    return [{'level': message.level, 'message': message.message, 'tags': message.tags} for message in storage]

def update_companions(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    if request.method == 'POST':
        new_count = int(request.POST.get('companions_checked_in', 0))
        guest.update_companions(new_count)
        messages.success(request, f"Quantidade de acompanhantes de {guest.name} atualizada para {new_count}.")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'messages': get_messages_json(request)})
    
    return redirect('guest_list')
