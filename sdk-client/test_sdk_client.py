"""
Pruebas unitarias para sdk-client.py
Ejecutar con: pytest sdk-client/test_sdk_client.py -v
"""

import importlib.util
import pathlib
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ── Importar módulo con guión en el nombre ──────────────────────────────────
spec = importlib.util.spec_from_file_location(
    "sdk_client",
    pathlib.Path(__file__).parent / "sdk-client.py",
)
sdk_client = importlib.util.module_from_spec(spec)
# Registrar en sys.modules para que patch() pueda resolverlo
sys.modules["sdk_client"] = sdk_client
spec.loader.exec_module(sdk_client)

# Variables globales requeridas por el módulo
sdk_client.ai_endpoint = ""
sdk_client.ai_key = ""


# ── Helper: crea un mock de async context manager ───────────────────────────
def make_async_cm(mock_instance):
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=mock_instance)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


# ── Helper: crea un async generator para paginar resultados ─────────────────
async def async_pages(pages):
    for page in pages:
        yield page


# ════════════════════════════════════════════════════════════════════════════
# get_language_async
# ════════════════════════════════════════════════════════════════════════════
class TestGetLanguageAsync:

    @pytest.mark.asyncio
    async def test_detecta_espanol(self):
        mock_client = AsyncMock()
        mock_lang = MagicMock()
        mock_lang.primary_language.name = "Spanish"
        mock_client.detect_language = AsyncMock(return_value=[mock_lang])

        with patch("sdk_client.TextAnalyticsClient", return_value=make_async_cm(mock_client)):
            result = await sdk_client.get_language_async("Hola mundo")

        assert result == "Spanish"

    @pytest.mark.asyncio
    async def test_detecta_ingles(self):
        mock_client = AsyncMock()
        mock_lang = MagicMock()
        mock_lang.primary_language.name = "English"
        mock_client.detect_language = AsyncMock(return_value=[mock_lang])

        with patch("sdk_client.TextAnalyticsClient", return_value=make_async_cm(mock_client)):
            result = await sdk_client.get_language_async("Hello world")

        assert result == "English"

    @pytest.mark.asyncio
    async def test_retorna_unknown_si_falla(self):
        with patch("sdk_client.TextAnalyticsClient", side_effect=Exception("API error")):
            result = await sdk_client.get_language_async("texto")

        assert result == "Unknown"


# ════════════════════════════════════════════════════════════════════════════
# get_sentiment_async
# ════════════════════════════════════════════════════════════════════════════
class TestGetSentimentAsync:

    @pytest.mark.asyncio
    async def test_sentimiento_positivo(self):
        mock_client = AsyncMock()
        mock_result = MagicMock()
        mock_result.sentiment = "positive"
        mock_client.analyze_sentiment = AsyncMock(return_value=[mock_result])

        with patch("sdk_client.TextAnalyticsClient", return_value=make_async_cm(mock_client)):
            result = await sdk_client.get_sentiment_async("Me encanta este servicio")

        assert result == "positive"

    @pytest.mark.asyncio
    async def test_sentimiento_negativo(self):
        mock_client = AsyncMock()
        mock_result = MagicMock()
        mock_result.sentiment = "negative"
        mock_client.analyze_sentiment = AsyncMock(return_value=[mock_result])

        with patch("sdk_client.TextAnalyticsClient", return_value=make_async_cm(mock_client)):
            result = await sdk_client.get_sentiment_async("Pésimo producto")

        assert result == "negative"

    @pytest.mark.asyncio
    async def test_retorna_unknown_si_falla(self):
        with patch("sdk_client.TextAnalyticsClient", side_effect=Exception("API error")):
            result = await sdk_client.get_sentiment_async("texto")

        assert result == "Unknown"


# ════════════════════════════════════════════════════════════════════════════
# get_key_phrases_async
# ════════════════════════════════════════════════════════════════════════════
class TestGetKeyPhrasesAsync:

    @pytest.mark.asyncio
    async def test_extrae_frases_clave(self):
        mock_client = AsyncMock()
        mock_result = MagicMock()
        mock_result.key_phrases = ["Azure", "inteligencia artificial", "nube"]
        mock_client.extract_key_phrases = AsyncMock(return_value=[mock_result])

        with patch("sdk_client.TextAnalyticsClient", return_value=make_async_cm(mock_client)):
            result = await sdk_client.get_key_phrases_async(
                "Azure ofrece servicios de inteligencia artificial en la nube"
            )

        assert result == ["Azure", "inteligencia artificial", "nube"]

    @pytest.mark.asyncio
    async def test_retorna_lista_vacia_si_falla(self):
        with patch("sdk_client.TextAnalyticsClient", side_effect=Exception("API error")):
            result = await sdk_client.get_key_phrases_async("texto")

        assert result == []


# ════════════════════════════════════════════════════════════════════════════
# get_named_entities_async
# ════════════════════════════════════════════════════════════════════════════
class TestGetNamedEntitiesAsync:

    @pytest.mark.asyncio
    async def test_reconoce_entidades(self):
        mock_client = AsyncMock()
        mock_result = MagicMock()

        entity1 = MagicMock()
        entity1.text = "Microsoft"
        entity1.category = "Organization"

        entity2 = MagicMock()
        entity2.text = "Madrid"
        entity2.category = "Location"

        mock_result.entities = [entity1, entity2]
        mock_client.recognize_entities = AsyncMock(return_value=[mock_result])

        with patch("sdk_client.TextAnalyticsClient", return_value=make_async_cm(mock_client)):
            result = await sdk_client.get_named_entities_async(
                "Microsoft tiene oficinas en Madrid"
            )

        assert result == [("Microsoft", "Organization"), ("Madrid", "Location")]

    @pytest.mark.asyncio
    async def test_retorna_lista_vacia_si_falla(self):
        with patch("sdk_client.TextAnalyticsClient", side_effect=Exception("API error")):
            result = await sdk_client.get_named_entities_async("texto")

        assert result == []


# ════════════════════════════════════════════════════════════════════════════
# get_language_iso_async
# ════════════════════════════════════════════════════════════════════════════
class TestGetLanguageIsoAsync:

    @pytest.mark.asyncio
    async def test_retorna_codigo_iso_espanol(self):
        mock_client = AsyncMock()
        mock_lang = MagicMock()
        mock_lang.primary_language.iso6391_name = "es"
        mock_client.detect_language = AsyncMock(return_value=[mock_lang])

        with patch("sdk_client.TextAnalyticsClient", return_value=make_async_cm(mock_client)):
            result = await sdk_client.get_language_iso_async("Hola mundo")

        assert result == "es"

    @pytest.mark.asyncio
    async def test_retorna_none_si_falla(self):
        with patch("sdk_client.TextAnalyticsClient", side_effect=Exception("API error")):
            result = await sdk_client.get_language_iso_async("texto")

        assert result is None


# ════════════════════════════════════════════════════════════════════════════
# get_extracted_summary_async
# ════════════════════════════════════════════════════════════════════════════
class TestGetExtractedSummaryAsync:

    @pytest.mark.asyncio
    async def test_genera_resumen(self):
        # Mock para get_language_iso_async (dependencia interna)
        with patch("sdk_client.get_language_iso_async", return_value="es"):
            mock_client = AsyncMock()

            # Construir resultado de la operación LRO
            sentence1 = MagicMock()
            sentence1.text = "Azure es una plataforma cloud."
            sentence2 = MagicMock()
            sentence2.text = "Ofrece más de 200 servicios."

            doc_result = MagicMock()
            doc_result.is_error = False
            doc_result.sentences = [sentence1, sentence2]

            mock_poller = AsyncMock()
            mock_poller.result = AsyncMock(return_value=async_pages([[doc_result]]))
            mock_client.begin_extract_summary = AsyncMock(return_value=mock_poller)

            with patch("sdk_client.TextAnalyticsClient", return_value=make_async_cm(mock_client)):
                result = await sdk_client.get_extracted_summary_async(
                    "Azure es una plataforma cloud. Ofrece más de 200 servicios."
                )

        assert result == "Azure es una plataforma cloud. Ofrece más de 200 servicios."

    @pytest.mark.asyncio
    async def test_retorna_none_si_falla(self):
        with patch("sdk_client.get_language_iso_async", side_effect=Exception("error")):
            result = await sdk_client.get_extracted_summary_async("texto")

        assert result is None
