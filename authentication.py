from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from db.context import SessionLocal
from db.models.user_model import User


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        db = SessionLocal()
        user = db.query(User).filter((User.name == username) & (User.password == password)).first()
        db.close()

        if not user:
            return False

        request.session.update({"token": username + " " + password})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        user = token.split(" ")
        if not user[0] or not user[1]:
            return False

        db = SessionLocal()
        usr = db.query(User).filter((User.name == user[0]) & (User.password == user[1])).first()
        db.close()

        if not usr:
            return False

        return True
