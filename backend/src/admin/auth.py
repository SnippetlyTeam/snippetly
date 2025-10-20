from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AuthProvider
from starlette_admin.exceptions import LoginFailed

from src.adapters.postgres.models import UserModel


class SnippetlyAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        db_session = request.state.session

        stmt = select(UserModel).where(UserModel.username == username)
        user = (await db_session.execute(stmt)).scalar_one_or_none()

        if (
            user is None
            or not user.is_active
            or not user.is_admin
            or not user.verify_password(password)
        ):
            raise LoginFailed("Invalid username or password")

        request.session.update({"identity": user.username, "pk": user.id})
        return response

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response

    async def is_authenticated(self, request: Request) -> bool:
        if "identity" not in request.session:
            return False

        if not hasattr(request.state, "user"):
            db_session = request.state.session
            user = await db_session.get(UserModel, request.session["pk"])
            request.state.user = user

        return True
