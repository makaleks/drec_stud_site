from django.shortcuts import render
from .forms import UserInfoForm, UserForm

# Create your views here.

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance = request.user)
        info_form = UserInfoForm(request.POST, instance = request.user.info)
        if user_form.is_valid() and info_form.is_valid():
            user_form.save()
            info_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('settings:profile')
        else:
            messages.error(request, 'Please correct the error')
    else:
        user_form = UserForm(instance = request.user)
        info_form = UserInfoForm(instance = request.user.info)
    return render(request, 'login.html', {
        'user_form': user_form,
        'info_form': info_form
    })
