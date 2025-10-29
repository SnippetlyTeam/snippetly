from faker import Faker

from src.adapters.postgres.models import UserModel

fake = Faker()


class UserFactory:
    @staticmethod
    def build(
        email: str | None = None,
        username: str | None = None,
        password: str = "Test1234!",
    ) -> UserModel:
        user = UserModel.create(
            email=email or fake.unique.email(),
            username=username or fake.unique.user_name(),
            password=password,
        )
        return user

    @staticmethod
    async def create(
        db,
        email: str | None = None,
        username: str | None = None,
        password: str = "Test1234!",
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
    async def create_with_tokens(db, token: str):
        user = await UserFactory.create(db)

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
