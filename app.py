
import streamlit as st
import duckdb
import os
import unicodedata

from google import genai
from google.genai import types


# Configuration

st.set_page_config(
    page_title="Dalili — Assistant Administratif Marocain",
    page_icon="🇲🇦",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    [data-testid="stChatMessage"] {
        padding: 1rem;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🇲🇦 Dalili (دليلي)")
st.subheader(
    "Votre assistant intelligent pour les démarches administratives au Maroc"
)

DB_PATH = "/home/atm/atm2526/bootc/Capstone_Project/dalili_local_warehouse.duckdb"

MODEL_NAMES = [
    "gemini-3.5-flash-lite"
]


# Retrieval Layer

def normalize_text(text):
    text = str(text).lower().strip()
    text = unicodedata.normalize("NFKD", text)

    return "".join(
        char for char in text
        if not unicodedata.combining(char)
    )


def detect_procedure(user_input):

    query = normalize_text(user_input)

    if any(word in query for word in [
        "passeport", "pass", "passport"
    ]):
        return "passeport"

    if any(word in query for word in [
        "cnie", "cni", "cine", "cin",
    "carte nationale", "identite nationale"
    ]):
        return "cnie"

    if any(word in query for word in [
        "carte grise", "certificat d'immatriculation",
        "transfert de propriete", "vehicule",
        "voiture", "carte grise"
    ]):
        return "transfert"

    return None


def get_administrative_context(user_input):

    procedure = detect_procedure(user_input)

    if not procedure:
        return ""

    if not os.path.exists(DB_PATH):
        st.error("Une erreur est survenue lors de l'accès aux informations.")
        return ""

    search_patterns = {
        "passeport": ["%passeport%"],
        "cnie": [
            "%cnie%",
            "%carte nationale d'identite%",
            "%carte nationale d'identité%"
        ],
        "transfert": [
            "%transfert%",
            "%carte grise%"
        ]
    }

    try:
        with duckdb.connect(DB_PATH, read_only=True) as con:

            conditions = " OR ".join(
                ["LOWER(nom_procedure) LIKE ?" for _ in search_patterns[procedure]]
            )

            results = con.execute(f"""
                SELECT
                    nom_procedure,
                    ministere,
                    frais_en_mad,
                    piece_a_fournir,
                    url_officielle
                FROM main.v_reponse_business
                WHERE {conditions}
            """, search_patterns[procedure]).fetchall()

        if not results:
            return ""

        procedure_name = results[0][0]
        ministere = results[0][1]
        frais = results[0][2]
        url = results[0][4]

        if frais is not None and str(frais).strip():

            frais_formate = str(frais).strip()

            if not any(unit in frais_formate.lower() for unit in [
                "mad", "dh", "dirham"
            ]):
                frais_formate += " MAD"

        else:
            frais_formate = "Non renseignés dans les données disponibles"

        pieces = []

        for row in results:
            piece = row[3]

            if piece and str(piece).strip():
                piece = str(piece).strip()

                if piece not in pieces:
                    pieces.append(piece)

        pieces_text = (
            "\n".join(f"- {piece}" for piece in pieces)
            if pieces
            else "Non renseignées dans les données disponibles"
        )

        context = f"""
Procédure : {procedure_name or "Non renseignée"}

Frais : {frais_formate}

Pièces requises :
{pieces_text}

Administration concernée : {ministere or "Non renseignée"}

Site officiel : {url or "Non renseigné"}
"""

        return context

    except Exception:
        st.error(
            "Une erreur est survenue lors de la récupération des informations."
        )
        return ""


# Generation Layer

def generate_rag_response(user_query, context):

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return (
            "Le service est momentanément indisponible. "
            "Veuillez réessayer plus tard."
        )

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=20000,
                retry_options=types.HttpRetryOptions(
                    attempts=1
                )
            )
        )

    except Exception:
        return (
            "Le service est momentanément indisponible. "
            "Veuillez réessayer plus tard."
        )

    system_instruction = """
Tu es Dalili, un assistant spécialisé dans les démarches
administratives marocaines.

RÈGLES :

- Réponds dans la même langue que le citoyen.
- Utilise exclusivement les informations du contexte fourni.
- N'invente aucune information.
- Ne complète jamais une information absente par tes connaissances.
- Si une information manque, indique clairement qu'elle n'est pas renseignée.
- Conserve exactement les montants du contexte.
- Affiche les montants avec leur devise, notamment MAD lorsque celle-ci est indiquée.
- Ne mélange jamais deux procédures administratives différentes.
- Ne confonds jamais la CNIE avec la carte grise.
- Présente les pièces justificatives sous forme de liste à puces.
- Ne numérote pas les titres ni les listes de pièces.
- Utilise une présentation claire, aérée et professionnelle.
- Ne mentionne jamais les détails techniques internes.

ORDRE OBLIGATOIRE DE LA RÉPONSE :

**Procédure**

Nom de la procédure.

**Frais**

Montant exact et devise.

**Pièces requises**

Liste à puces des documents.

**Administration concernée**

Nom de l'administration.

**Site officiel**

Lien officiel, toujours en dernière position.

Ne place aucun texte après le lien officiel.

N'ajoute pas de rubrique si aucune information correspondante
n'est disponible dans le contexte.
"""

    prompt = f"""
Contexte disponible :

{context}

Question du citoyen :

{user_query}
"""

    for model_name in MODEL_NAMES:

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2
                )
            )

            if response.text and response.text.strip():
                return response.text.strip()

        except Exception as e:

            error_message = str(e).lower()

            if any(code in error_message for code in [
                "503", "429", "500",
                "unavailable", "resource_exhausted",
                "deadline_exceeded", "timeout"
            ]):
                continue

            break

    return (
        "Je rencontre actuellement une difficulté pour préparer "
        "votre réponse. Veuillez réessayer dans quelques instants."
    )


# User Interface

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar="🇲🇦" if message["role"] == "assistant" else None
    ):
        st.markdown(message["content"])

user_query = st.chat_input(
    "Posez votre question administrative..."
)

if user_query:

    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant", avatar="🇲🇦"):

        with st.spinner(
            "Un instant, Dalili prépare votre réponse..."
        ):

            context_data = get_administrative_context(user_query)

            if context_data:

                llm_response = generate_rag_response(
                    user_query,
                    context_data
                )

            else:

                llm_response = (
                    "💡 Je ne dispose pas encore d'informations "
                    "suffisantes sur cette démarche. "
                    "Essayez une question concernant le passeport, "
                    "la CNIE ou la carte grise."
                )

        st.markdown(llm_response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": llm_response
    })
