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
    ) -> UserModel:
        user = UserFactory.build(
            email=email, username=username, password=password
        )
        db.add(user)
        await db.flush()
        return user
