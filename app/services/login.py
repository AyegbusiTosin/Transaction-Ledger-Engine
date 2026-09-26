#Handles business logic of the login endpoint
from exceptions import InvalidCredentialsError
from pwdlib import PasswordHash


async def process_login(login_data, conn):
    query = """
        SELECT id, name, email, password
        FROM users
        WHERE email = $1;
        """

    user = await conn.fetchrow(query,
                               login_data.email)

    if not user:
        raise InvalidCredentialsError()  

    password_hash = PasswordHash.recommended()

    if not password_hash.verify(
                        login_data.password, 
                         user["password"]
        ):
        raise InvalidCredentialsError()

    return{"message": "Authentication successful",
           "user_id": user["id"],
           "name": user["name"]}

