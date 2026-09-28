#Handles business logic of the login endpoint

from exceptions import InvalidCredentialsError
from pwdlib import PasswordHash
from utils.auth import create_access_token


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
        #"Invalid email or Password"  

    password_hash = PasswordHash.recommended()

    if not password_hash.verify(
                        login_data.password, 
                         user["password"]
        ):
        raise InvalidCredentialsError()
        #"Invalid email or Password"

    #creates and assigns token to user_id
    access_token = create_access_token(user["id"])

    return{"message": "Authentication successful",
           "access_token": access_token,
           "user_id": user["id"],
           "name": user["name"]}
