# Authentication routes
route_prefix = "/api/v1/auth/"

# Registration
register_url = f"{route_prefix}register"
activate_url = f"{route_prefix}activate"
resend_activation_url = f"{route_prefix}resend-activation"

# Login & Authentication
login_url = f"{route_prefix}login"
logout_url = f"{route_prefix}logout"
refresh_url = f"{route_prefix}refresh"
revoke_all_tokens_url = f"{route_prefix}revoke-all-tokens"

# Password Management
reset_password_request_url = f"{route_prefix}reset-password/request"
reset_password_complete_url = f"{route_prefix}reset-password/complete"
change_password_url = f"{route_prefix}change-password"

profile_url = "/api/v1/profile/"
avatar_url = f"{profile_url}avatar"
