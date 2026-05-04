from stadium.models import UserProfile

def user_role_processor(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            role = 'executive' if request.user.is_superuser else 'manager'
            profile = UserProfile.objects.create(user=request.user, role=role)
        return {'user_role': profile.role, 'user_role_display': profile.get_role_display()}
    return {}
