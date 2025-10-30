from faker import Faker

from src.adapters.postgres.models import UserModel

fake = Faker()


class UserFactory:
    DEFAULT_PASSWORD = "Test1234!"

    @staticmethod
    def build(
        email: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> UserModel:
        user = UserModel.create(
            email=email or fake.unique.email(),
            username=username or fake.unique.user_name(),
            password=password or UserFactory.DEFAULT_PASSWORD,
        )
        return user

    @staticmethod
    async def create(
        db,
        email: str | None = None,
        username: str | None = None,
        password: str | None = None,
        is_active: bool = False,
    ) -> UserModel:
        user = UserFactory.build(
            email=email, username=username, password=password
        )

        if is_active:
            user.is_active = is_active

        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def create_active(
        db,
        email: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> UserModel:
        return await UserFactory.create(
            db,
            email=email,
            username=username,
            password=password,
            is_active=True,
        )

    @staticmethod
    async def create_with_tokens(db, token: str, is_active: bool = False):
        user = await UserFactory.create(db, is_active=is_active)

        from src.adapters.postgres.models import (
            ActivationTokenModel,
            PasswordResetTokenModel,
            RefreshTokenModel,
        )

        tokens = [
            ActivationTokenModel.create(user.id, token),
            PasswordResetTokenModel.create(user.id, token),
            RefreshTokenModel.create(user.id, token),
        ]
        db.add_all(tokens)
        await db.flush()
        return user

    @staticmethod
    async def create_with_activation_token(
        db,
        token: str,
    ) -> tuple[UserModel, str]:
        from src.adapters.postgres.models import ActivationTokenModel

        user = await UserFactory.create(db)
        token_model = ActivationTokenModel.create(user.id, token)
        db.add(token_model)
        await db.flush()
        return user, token

    @staticmethod
    async def create_with_reset_token(
        db,
        token: str,
    ) -> tuple[UserModel, str]:
        from src.adapters.postgres.models import PasswordResetTokenModel

        user = await UserFactory.create(db, is_active=True)
        token_model = PasswordResetTokenModel.create(user.id, token)
        db.add(token_model)
        await db.flush()
        return user, token
