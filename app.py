# app.py
from flask import Flask, render_template, request
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
app = Flask(__name__)

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configurando la API de Gemini: {e}")
    model = None

def generar_publicacion_completa_con_ia(tipo_prenda, marca, color, talla, estado, caracteristicas):
    if not model:
        return {"error": "Modelo de IA no configurado."}

    prompt = f"""
    Actúa como una experta en marketing de moda y ventas para GoTrendier. Tu reputación es 5 estrellas.
    Tu tarea es generar un paquete completo de publicación.

    DATOS DE LA PRENDA:
    - Tipo de prenda: {tipo_prenda}, Marca: {marca}, Talla: {talla}, Color: {color}, Estado: {estado}
    - Características extra: {caracteristicas if caracteristicas else "ninguna"}

    INSTRUCCIONES DE FORMATO DE SALIDA:
    Responde estrictamente con un objeto JSON con cuatro claves: "rango_precio", "titulo", "descripcion_gotrendier" y "descripcion_facebook".

    REGLAS PARA CADA CLAVE:
    1. "rango_precio": Analiza el mercado de GoTrendier para prendas similares. Calcula un precio promedio, auméntalo en un 30% por ser de una vendedora Top. Finalmente, presenta el resultado como un string de texto con un rango sugerido. Ejemplo: "Te sugiero un rango de precio de entre $250 y $300 MXN."
    2. "titulo": Crea un título atractivo de 6 a 8 palabras. La marca ('{marca}') debe ir SIEMPRE al final y EN MAYÚSCULAS.
    3. "descripcion_gotrendier": Crea una descripción chic, juvenil y persuasiva para GoTrendier.
    4. "descripcion_facebook": Crea una descripción para Facebook, amigable y con emojis. NO debe mencionar la palabra 'GoTrendier'.

    Genera únicamente el objeto JSON válido.
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned_response)
        return data
        
    except Exception as e:
        print(f"Error en la llamada a la API o procesando la respuesta: {e}")
        return {"error": f"Error de IA: {e}"}

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == 'POST':
        tipo_prenda = request.form.get('tipo_prenda')
        marca = request.form.get('marca')
        estado = request.form.get('estado')
        talla = request.form.get('talla')
        color = request.form.get('color')
        caracteristicas = request.form.get('caracteristicas_especiales')

        if all([tipo_prenda, marca, talla, color]):
            results_ia = generar_publicacion_completa_con_ia(tipo_prenda, marca, color, talla, estado, caracteristicas)
            
            if "error" not in results_ia:
                results = {
                    'titulo': results_ia.get("titulo"),
                    'descripcion_gotrendier': results_ia.get("descripcion_gotrendier"),
                    'descripcion_facebook': results_ia.get("descripcion_facebook"),
                    'precio': results_ia.get("rango_precio") # Usamos la nueva clave
                }
            else:
                results = {'error': results_ia.get("error")}

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)