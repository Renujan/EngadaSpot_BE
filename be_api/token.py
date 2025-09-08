# be_api/token.py
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    # Add custom claims
    refresh['role'] = user.role  # assuming you have a 'role' field
    refresh['username'] = user.username
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }
