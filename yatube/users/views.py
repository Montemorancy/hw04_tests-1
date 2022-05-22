from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import ContactForm, CreationForm


class PasswordReset(PasswordResetView):
    success_url = reverse_lazy('users:login')
    template_name = 'users/password_reset_done.html'


class PasswordChangeDone(PasswordChangeView):
    success_url = reverse_lazy('users:pswrd_change_done')
    template_name = 'users/password_change_form.html'


def sign_up(request):
    sign_up_template = 'users/signup.html'
    form = CreationForm(request.POST or None)
    if request.user.is_authenticated:
        return redirect('posts:index')
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('users:login')
    return render(request, sign_up_template, {'form': form})


def user_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.cleaned_data['name']
            form.cleaned_data['email']
            form.cleaned_data['subject']
            form.cleaned_data['body']
            form.save()
            return redirect('/thank-you/')
        return render(request, 'contact.html', {'form': form})
    form = ContactForm()
    return render(request, 'contact.html', {'form': form})
