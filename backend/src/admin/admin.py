from starlette_admin.contrib.sqla import Admin, ModelView

from src.adapters.postgres.async_db import engine
from src.adapters.postgres.models import (
    UserModel,
    ActivationTokenModel,
    PasswordResetTokenModel,
    UserProfileModel,
    SnippetModel,
    TagModel,
    SnippetFavoritesModel,
    RefreshTokenModel,
)
from .auth import SnippetlyAuthProvider

admin = Admin(
    engine,
    title="Snippetly Admin Dashboard",
    auth_provider=SnippetlyAuthProvider(),
)

admin.add_view(ModelView(UserModel, "fa fa-users", label="Users"))
admin.add_view(
    ModelView(UserProfileModel, "fa fa-user-circle", label="User Profiles")
)
admin.add_view(
    ModelView(
        ActivationTokenModel, "fa fa-certificate", label="Activation Tokens"
    )
)
admin.add_view(
    ModelView(
        PasswordResetTokenModel, "fa fa-key", label="Password Reset Tokens"
    )
)
admin.add_view(
    ModelView(RefreshTokenModel, "fa fa-ticket", label="Refresh Tokens")
)
admin.add_view(ModelView(SnippetModel, "fa fa-code", label="Snippets"))
admin.add_view(
    ModelView(
        SnippetFavoritesModel, "fa fa-thumbs-up", label="Snippet Favorites"
    )
)
admin.add_view(ModelView(TagModel, "fa fa-tags", label="Tags"))
