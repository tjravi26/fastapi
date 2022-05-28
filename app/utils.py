from passlib.context import CryptContext

# schemes tells passlib which hashing algorithm to use.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)
