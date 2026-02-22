import asyncio
from http import client
import logging
from dotenv import load_dotenv
import os
from azure.identity import DefaultAzureCredential # pip install azure-identity azure-keyvault-secrets
from azure.keyvault.secrets import SecretClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import  TextDocumentInput



# URL de tu Key Vault
key_vault_url = "https://kv-ai-textanalytics.vault.azure.net/"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)





async def main():
    global ai_endpoint
    global ai_key

    try:
        # Cliente con credenciales administradas
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_url, credential=credential)

        # Obtener configuración
        load_dotenv()
        # ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        # ai_key = os.getenv('AI_SERVICE_KEY')

        # Obtener secretos
        ai_endpoint = client.get_secret("AIServicesEndpoint").value
        ai_key = client.get_secret("AIServicesKey").value


        # Obtener entrada del usuario (hasta que escriba "quit")
        userText =''
        while userText.lower() != 'quit':
            userText = input('\nEnter some text ("quit" to stop)\n')
            if userText.lower() != 'quit':
                # Detectar idioma
                language = await get_language_async(userText)

                # Analizar sentimiento
                sentiment = await get_sentiment_async(userText)

                # Extraer frases clave                
                keyPhrases = await get_key_phrases_async(userText)

                # Reconocer entidades nombradas
                entities = await get_named_entities_async(userText)
                logger.info('Entidades nombradas: %s', entities)

                # Resumen extractivo asíncrono
                summary = await get_extracted_summary_async(userText)

                logger.info(f"Idioma detectado: {language}")              
                logger.info(f'Sentimiento: {sentiment}')
                logger.info(f'Frases clave: {keyPhrases}')
                logger.info(f'Entidades nombradas: {entities}')
                logger.info(f'Resumen extractivo: {summary}')

                

    except Exception as ex:
        logger.error(f"Error en main: {ex}")


# Método GetLanguage que detecte el idioma de un texto usando Azure Text Analytics
async def get_language_async(text):
    try:
        # Crear credenciales
        credential = AzureKeyCredential(ai_key)
        # Usar 'async with' para manejar la conexión asíncrona
        async with TextAnalyticsClient(endpoint=ai_endpoint, credential=credential) as client:
            # En el SDK asíncrono, detect_language devuelve una lista de resultados
            response = await client.detect_language(documents=[text])
            # Obtener el primer resultado (índice 0)
            detectedLanguage = response[0]
            # Retornar el nombre del idioma (ej: "Spanish", "English")
            return detectedLanguage.primary_language.name
    except Exception as ex:
        logger.error(f"Error en GetLanguage: {ex}")
        return "Unknown"


# Método AnalyzeSentiment que detecte polaridad de un texto usando Azure Text Analytics
async def get_sentiment_async(text):
    try:
        credential = AzureKeyCredential(ai_key)
        async with TextAnalyticsClient(endpoint=ai_endpoint, credential=credential) as client:
            responses = await client.analyze_sentiment(documents=[text])
            sentiment_result = responses[0]
            # 1. Retornar el sentimiento (ej: "positive", "neutral", "negative")
            return sentiment_result.sentiment

    except Exception as ex:
        logger.error(f"Error en AnalyzeSentiment: {ex}")
        return "Unknown"


# Metodo ExtractKeyPhrases (Extracción de frases clave) de un texto usando Azure Text Analytics
async def get_key_phrases_async(text):
    try:
        credential = AzureKeyCredential(ai_key)
        async with TextAnalyticsClient(endpoint=ai_endpoint, credential=credential) as client:
            responses = await client.extract_key_phrases(documents=[text])
            key_phrases_result = responses[0]
            # 1. Retornar la lista de frases clave (ej: ['viaje', 'servicio', 'rutas'])
            return key_phrases_result.key_phrases

    except Exception as ex:
        logger.error(f"Error en ExtractKeyPhrases: {ex}")
        return [] # Retornamos una lista vacía en caso de error


# Metodo RecognizeEntities (Reconocimiento de entidades) nombradas de un texto usando Azure Text Analytics
async def get_named_entities_async(text):
    try:
        credential = AzureKeyCredential(ai_key)
        async with TextAnalyticsClient(endpoint=ai_endpoint, credential=credential) as client:
            responses = await client.recognize_entities(documents=[text])
            entities_result = responses[0]
            # 1. Retornar la lista de tuplas (texto, categoría)
            return [(entity.text, entity.category) for entity in entities_result.entities]

    except Exception as ex:
        logger.error(f"Error en RecognizeEntities: {ex}")
        return [] # Retornamos una lista vacía en caso de error



# Método ExtractiveSummarizeAsync de resumen extractivo
async def get_extracted_summary_async(text):
    try:
        # 1. Detectar idioma usando la función asíncrona anterior
        language = await get_language_iso_async(text)
        print(f"Sigla lenguaje detectado: {language}")

        credential = AzureKeyCredential(ai_key)
        async with TextAnalyticsClient(endpoint=ai_endpoint, credential=credential) as client:
            documents = [
                TextDocumentInput(id="1", text=text, language=language)
            ]
            # 1. Iniciar la operación de resumen (LRO)
            poller = await client.begin_extract_summary(
                documents,
                max_sentence_count=10
            )
            # 2. Esperar a que la operación complete (equivale a WaitUntil.Completed)
            result_pages = await poller.result()
            summary_parts = []
            async for page in result_pages: 
                for doc_result in page: # (equivale al await foreach)
                    if not doc_result.is_error:
                        for sentence in doc_result.sentences:
                            summary_parts.append(sentence.text)
                    else:
                        logger.error(f"Error en documento: {doc_result.error}")

            # 3. Unir las partes y devolver el string
            return " ".join(summary_parts)

    except Exception as ex:
        logger.error(f"Error en GetExtractedSummary: {ex}")
        return None
    
# Método GetLanguageISO que detecte el idioma de un texto y retorne la sigla ISO639-1 usando Azure Text Analytics
async def get_language_iso_async(text):
    try:
        credential = AzureKeyCredential(ai_key)
        async with TextAnalyticsClient(endpoint=ai_endpoint, credential=credential) as client:
            results = await client.detect_language(documents=[text])
            detectedLanguage = results[0]
            return detectedLanguage.primary_language.iso6391_name
    except Exception as ex:
        logger.error(f"Error en DetectLanguage: {ex}")
        return None



if __name__ == "__main__":
    asyncio.run(main())
 