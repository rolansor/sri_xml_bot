from licensing.methods import Key, Helpers
import tkinter as tk
from librerias.auxiliares import centrar_ventana

# Inicializa Cryptolens con tu Access Token
acces_token = "WyI5NTc0MTEzOCIsIkNENTQxbW1ETnYwSnpNZ0x4S1h0L1FDMTRjWXFkUVRYUDVvVndNWnAiXQ=="
rsa_pubkey = "<RSAKeyValue><Modulus>n47zx+ONiULs5nhOlCAJvx7KV9P3HxiHpxHCfSpAjAHIItmKyZA3QhngTCbdvygEvHSCBCWObGDDxAoACOKE4d7xSmAFGmLR9N6jutiz2QDj2pvinowjVAxkSU+JGYKujNYoPDSqogXh0TNednzD0cXyGY7bB+8z5gxnco79o8rI+ahbXDX55gnI8jtZJ4lIHVWrZjYOaWBjo1I1ZbAN2cfCJF7fhkduNEdJ7O7xOEF+tnLELhZLIdqEnfAkvVQQfQfnDgbojuoXi0Oq1WzdVC9Zj5lcSOsjOsywvQnQo2uh5FVSHDvxUVyW72+BHTTl/cwGa1jnvqLCHi5Hy2PF3w==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"

def pedir_licencia():
    """
    Crea una ventana que solicita al usuario su clave de licencia y la retorna.
    """
    licencia = None

    def obtener_licencia():
        nonlocal licencia
        licencia = entrada_licencia.get()
        root.quit()

    root = tk.Tk()
    root.title("Validar Licencia")
    centrar_ventana(root)

    etiqueta = tk.Label(root, text="Por favor, ingrese su clave de licencia:")
    etiqueta.pack(pady=10)

    entrada_licencia = tk.Entry(root, width=40)
    entrada_licencia.pack(pady=5)

    boton_validar = tk.Button(root, text="Validar", command=obtener_licencia)
    boton_validar.pack(pady=10)

    root.mainloop()

    root.destroy()  # Cierra la ventana después de obtener la licencia
    return licencia


def verificar_licencia():
    licencia_usuario = pedir_licencia()  # Cambiado para usar la ventana de entrada gráfica

    if not licencia_usuario:
        print("No se ingresó ninguna licencia.")
        return False

    try:
        # Verifica la licencia con Cryptolens
        result = Key.activate(token=acces_token, rsa_pub_key=rsa_pubkey, product_id=27730, key=licencia_usuario,
                              machine_code=Helpers.GetMachineCode(v=2))

        if result[0] is None or not Helpers.IsOnRightMachine(result[0], v=2):
            print("Licencia inválida: {0}".format(result[1]))
            return False
        else:
            print("Licencia válida.")
            return True
    except Exception as e:
        print(f"Error en la validación de la licencia: {str(e)}")
        return False
