import logging
from dotenv import load_dotenv
import os
import http.client, json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    global ai_endpoint
    global ai_key

    try:
        # Cargar las variables de entorno (AI_SERVICE_ENDPOINT y AI_SERVICE_KEY)
        # Portal Azure > servicios de Azure AI > tu servicio de Azure AI > Claves y punto de conexión
        load_dotenv()
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')

        # Solicitar al usuario que ingrese texto para detectar el idioma, hasta que escriba "quit"
        userText =''
        while userText.lower() != 'quit':
            userText = input('Ingrese el texto ("quit" para deternerlo)\n')
            if userText.lower() != 'quit':
                GetLanguage(userText)

    except Exception as ex:
        logger.error(f"Error en la App: {ex}")

def GetLanguage(text):
    try:
        # construir el cuerpo de la solicitud con el texto del usuario para detectar el idioma
        jsonBody = {
            "documents":[
                {"id": 1,
                 "text": text}
            ]
        }

        # Mostrar el JSON de la solicitud (solo para fines de demostración)
        logger.info(f"Request JSON: {json.dumps(jsonBody, indent=2)}")

        # Crear la conexión HTTPS al punto de conexión del servicio de Azure AI
        uri = ai_endpoint.rstrip('/').replace('https://', '')
        conn = http.client.HTTPSConnection(uri)

        # Configurar los encabezados de la solicitud, incluyendo la clave de suscripción para autenticación
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': ai_key
        }

        # Enviar la solicitud POST al servicio de Azure AI para detectar el idioma
        conn.request("POST", "/text/analytics/v3.1/languages?", str(jsonBody).encode('utf-8'), headers)

        # Obtener la respuesta del servicio de Azure AI
        response = conn.getresponse()
        data = response.read().decode("UTF-8")

        # Verificar si la respuesta fue exitosa (código de estado 200)
        if response.status == 200:

            # Analizar la respuesta JSON y mostrar el resultado de la detección de idioma
            results = json.loads(data)
            logger.info(f"Response JSON: {json.dumps(results, indent=2)}")

            # Recorrer los documentos en la respuesta y mostrar el idioma detectado para cada uno
            for document in results["documents"]:
                logger.info(f"\nLenguaje: {document['detectedLanguage']['name']}")

        else:
            # Si la respuesta no fue exitosa, mostrar el código de estado y el mensaje de error
            logger.error(f"Error respuesta: {data}")

        conn.close()


    except Exception as ex:
        logger.error(f"Error in GetLanguage: {ex}")


if __name__ == "__main__":
    main()