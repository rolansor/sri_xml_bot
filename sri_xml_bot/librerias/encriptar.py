import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derivar_clave(password: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """
    Deriva una clave de cifrado a partir de una contraseña y una sal.
    """
    password_bytes = password.encode()  # Convertir a bytes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    clave = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return clave


def encriptar_texto(texto: str, password: str, salt: bytes) -> str:
    """
    Encripta un texto usando la contraseña y la sal proporcionadas.
    Devuelve el texto encriptado en formato base64.
    """
    clave = derivar_clave(password, salt)
    fernet = Fernet(clave)
    token = fernet.encrypt(texto.encode())
    return token.decode()


def desencriptar_texto(token: str, password: str, salt: bytes) -> str:
    """
    Desencripta el token usando la contraseña y la sal proporcionadas.
    Devuelve el texto original.
    """
    clave = derivar_clave(password, salt)
    fernet = Fernet(clave)
    texto = fernet.decrypt(token.encode())
    return texto.decode()
