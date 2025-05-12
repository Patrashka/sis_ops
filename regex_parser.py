#!/usr/bin/env python3
import os
import re
import pandas as pd
import csv
from datetime import datetime, timedelta
import PyPDF2

# Lista de campos requeridos (en el orden deseado)
required_fields = [
    "Name",
    "Date of Birth",
    "Place of Birth",
    "Date of Interview",
    "Location of Interview",
    "Parent's Names",
    "Parent's Birthplace",
    "Parent's Occupation",
    "Siblings",
    "Spouse's Name",
    "Children's Names",
    "Grandchildren's Names",
    "Date of Immigration",
    "Country of Origin",
    "Reason for Immigration",
    "Mode of Travel",
    "Ports of Entry",
    "Destinations",
    "Occupation",
    "Employer",
    "Job Title",
    "Education Level",
    "Schools Attended",
    "Year of Graduation",
    "Health Issues",
    "Medical Treatments",
    "Cause of Death",
    "Church Affiliation",
    "Community Involvement",
    "Social Activities",
    "Language Spoken",
    "Cultural Practices",
    "Historical Events Experienced",
    "Geographical Locations",
    "Notes",
    "Sources"
]

# Lista de campos que se deben formatear como fecha
date_fields = ["Date of Birth", "Date of Interview", "Date of Immigration", "Year of Graduation"]

def format_date(value):
    """
    Intenta formatear el valor recibido a "YYYY-MM-DD".
    
    Supuestos:
      - Si se recibe un número entre 1800 y 2100 se asume que es un año (se retorna "YYYY-01-01").
      - Si se recibe una cadena, se utiliza pandas.to_datetime para el parseo.
      - En caso de error se retorna "Invalid Date".
    """
    try:
        # Si el valor es numérico y parece un año
        if isinstance(value, (int, float)):
            if 1800 <= value <= 2100:
                return f"{int(value)}-01-01"
            else:
                base = datetime(1899, 12, 30)
                converted = base + timedelta(days=float(value))
                return converted.strftime("%Y-%m-%d")
        # Intentar parsear la cadena
        parsed = pd.to_datetime(value, errors='coerce')
        if pd.isna(parsed):
            return "Invalid Date"
        return parsed.strftime("%Y-%m-%d")
    except Exception as e:
        return "Invalid Date"

def extract_text_from_pdf(file_path):
    """
    Extrae todo el texto de un archivo PDF usando PyPDF2.
    """
    text = ""
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
    return text

def extract_fields_unlabeled(text, filename):
    """
    Función que utiliza expresiones regulares heurísticas para extraer información
    de un texto sin etiquetas fijas. Se asigna "N/A" a los campos que no se logran detectar.
    
    Algunos ejemplos de extracción:
      - "Name": Se busca el patrón "interview with" seguido de un nombre (dos o más palabras).
      - "Date of Interview": Se busca una fecha (ej. "11th of March 1986") en el contexto de "interview".
      - "Siblings": Se extraen las menciones de "my brother" o "my sister" y se agrupan.
      - "Church Affiliation": Se detecta la mención de "Salvation Army".
      - "Employer": Se detecta la mención de "John Deere".
      - "Schools Attended": Se busca la mención de "training college in Chicago".
      - "Geographical Locations": Se comprueba la presencia de algunas locaciones conocidas.
      
    Para otros campos se puede agregar nuevas reglas según el comportamiento de los documentos.
    """
    # Inicializar todos los campos con "N/A"
    data = { field: "N/A" for field in required_fields }
    
    # --- Extracción heurística de algunos campos ---
    
    # Date of Interview: se busca una fecha cercana a la palabra "interview"
    date_int_match = re.search(
        r'interview.*?(\d{1,2}(?:st|nd|rd|th)?\s+of\s+[A-Za-z]+\s+\d{4})',
        text, re.IGNORECASE | re.DOTALL)
    if date_int_match:
        data["Date of Interview"] = date_int_match.group(1).strip()
    
    # Name: se busca "interview with" seguido de un nombre (2 o más palabras que empiecen con mayúscula)
    name_match = re.search(
        r'interview with\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
        text, re.IGNORECASE)
    if name_match:
        data["Name"] = name_match.group(1).strip()
    
    # Date of Birth: buscar patrones simples como "born on" o "born 12/05/1920"
    dob_match = re.search(r"born (?:on\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.IGNORECASE)
    if dob_match:
        data["Date of Birth"] = dob_match.group(1).strip()
    
    # Place of Birth: buscar la frase "born in" (por ejemplo: "born in Stockholm, Sweden")
    pob_match = re.search(r"born in\s+([A-Za-z\s]+)[\.,]", text, re.IGNORECASE)
    if pob_match:
        data["Place of Birth"] = pob_match.group(1).strip()
    
    # Siblings: buscar menciones de "my brother" o "my sister" seguido de un nombre
    siblings_matches = re.findall(r"my\s+(?:younger\s+)?(brother|sister)\s+([A-Z][a-zA-Z]+)", text, re.IGNORECASE)
    if siblings_matches:
        siblings_names = {match[1] for match in siblings_matches}
        data["Siblings"] = ", ".join(siblings_names)
    
    # Church Affiliation: buscar la presencia de "Salvation Army"
    church_match = re.search(r"(Salvation Army(?: training college)?)", text, re.IGNORECASE)
    if church_match:
        data["Church Affiliation"] = church_match.group(1).strip()
    
    # Employer: detectar si se menciona "John Deere" (ejemplo específico)
    employer_match = re.search(r"(John Deere)", text, re.IGNORECASE)
    if employer_match:
        data["Employer"] = employer_match.group(1).strip()
    
    # Schools Attended: búsqueda de la mención de "training college in Chicago"
    education_match = re.search(r"(Salvation Army training college in Chicago)", text, re.IGNORECASE)
    if education_match:
        data["Schools Attended"] = education_match.group(1).strip()
    
    # Geographical Locations: comprobación simple de locaciones conocidas
    locations_found = []
    for loc in ["California", "Moline", "Campbells Island", "Chicago", "Florida", "Sweden"]:
        if re.search(loc, text, re.IGNORECASE):
            locations_found.append(loc)
    if locations_found:
        data["Geographical Locations"] = ", ".join(sorted(set(locations_found)))
    
    # --- Otros campos se dejan en "N/A" o se pueden implementar reglas adicionales ---
    # Si necesitas extraer más datos (por ejemplo, "Parent's Names", "Occupation", "Spouse's Name",
    # "Children's Names", etc.), se recomienda analizar muestras representativas y definir las expresiones
    # regulares adecuadas. Aquí solo se implementan algunos ejemplos.
    
    # Asignar el campo "Sources" con el nombre del archivo procesado
    data["Sources"] = filename

    # Formatear los campos de fecha (si fueron capturados)
    for field in date_fields:
        if data[field] not in ["N/A", "", "Invalid Date"]:
            data[field] = format_date(data[field])
    
    return data

def main():
    # Directorio de entrada: ajustar el path según donde estén tus archivos PDF/TXT
    input_dir = "./input_files"  
    output_file = "Resultado.csv"
    
    resultados = []
    
    # Iterar sobre cada archivo del directorio
    for filename in os.listdir(input_dir):
        lower_filename = filename.lower()
        if lower_filename.endswith((".pdf", ".txt")):
            file_path = os.path.join(input_dir, filename)
            print(f"Procesando archivo: {filename}")
            
            # Extraer el texto: usar PyPDF2 si es PDF o leer directamente si es TXT
            if lower_filename.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            else:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                except Exception as e:
                    print(f"Error leyendo {file_path}: {e}")
                    text = ""
            
            # Aplicar la función de extracción heurística
            data = extract_fields_unlabeled(text, filename)
            resultados.append(data)
    
    if resultados:
        # Crear DataFrame con los campos en el orden requerido
        df_result = pd.DataFrame(resultados, columns=required_fields)
        # Exportar a CSV (puedes cambiar a .xlsx si prefieres)
        df_result.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
        print(f"Extracción completada. Resultado guardado en '{output_file}'.")
    else:
        print("No se encontraron archivos compatibles en el directorio especificado.")

if __name__ == '__main__':
    main()
