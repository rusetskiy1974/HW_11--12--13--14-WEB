from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and takes arguments that are passed to it.
        In this case, we're passing a list of Role objects.

        :param self: Represent the instance of the class
        :param allowed_roles: list[Role]: Define the allowed_roles attribute of the class
        :return: An object of the class
        :doc-author: SergiyRus1974
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        The __call__ function is a decorator that allows us to use the class as a function.
        It takes in two arguments: request and user. The request argument is passed by FastAPI,
        and the user argument is passed by our auth_service dependency.

        :param self: Refer to the object itself
        :param request: Request: Pass the request object to the function
        :param user: User: Get the current user from the database
        :return: A function that will be called with the request and user
        :doc-author: SergiyRus1974
        """
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="FORBIDDEN",
                )
