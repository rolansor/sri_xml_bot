import pdfplumber
import re
import pandas as pd

# Cargar el archivo PDF
pdf_path = "bgenero.pdf"

# Inicializar las listas para almacenar los datos procesados
data = []
csv_lines = []

# Expresión regular para validar la estructura de la fila
valor_pattern = re.compile(r'\s\d+\.\d{2}')

# Procesar el PDF
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text().splitlines()
        for line in text:
            # Buscar el valor usando un número decimal precedido por un espacio
            match = valor_pattern.search(line)
            if match:
                # Posición del valor
                valor_pos = match.start()

                # Dividir la línea en dos partes: antes del valor y después del valor
                descripcion_parte = line[:valor_pos].strip()
                valor_y_restante = line[valor_pos:].strip()

                try:
                    # Dividir el valor y el saldo total (y posiblemente la base imponible)
                    valor, *resto = valor_y_restante.split(maxsplit=2)
                    # Validar que el siguiente sea otro número decimal (el saldo total)
                    if not re.match(r'\d{1,3}(?:,\d{3})*\.\d{2}', resto[0]):
                        continue  # Si no es un número decimal válido, descartar la línea
                    saldo_total = resto[0]
                    base_imponible = resto[1] if len(resto) > 1 else "0.00"
                except Exception as e:
                    print(f"Error procesando la línea: {line}")
                    continue

                # Validar que la descripción no contenga palabras clave como "SALDO ANTERIOR"
                if "SALDO ANTERIOR" in descripcion_parte or "NUMERO DE DIAS" in descripcion_parte:
                    continue  # Ignorar líneas que no son transacciones válidas

                # Dividir la parte antes del valor en sus componentes
                try:
                    fecha, oficina, numero, canal, tipo, descripcion = descripcion_parte.split(maxsplit=5)
                except ValueError:
                    print(f"Error en la estructura de la línea: {line}")
                    continue

                # Agregar los datos procesados a la lista
                data.append([fecha, oficina, numero, canal, tipo, descripcion, valor, saldo_total, base_imponible])

                # Generar la línea CSV
                csv_line = f"{fecha},{oficina},{numero},{canal},{tipo},{descripcion},{valor},{saldo_total},{base_imponible}"
                csv_lines.append(csv_line)


# Crear DataFrame y guardar en Excel
df = pd.DataFrame(data, columns=["Fecha", "Oficina", "Numero", "Canal", "Tipo", "Descripcion", "Valor", "Saldo Total", "Base Imponible IVA"])

# Guardar el DataFrame y las líneas CSV en un archivo Excel
output_path = "estado_cuenta_procesado.xlsx"
with pd.ExcelWriter(output_path) as writer:
    df.to_excel(writer, sheet_name="Datos Procesados", index=False)
    pd.DataFrame(csv_lines, columns=["Linea CSV"]).to_excel(writer, sheet_name="CSV Lineas", index=False)

