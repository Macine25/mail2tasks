import requests
import json
import logging
from config import MISTRAL_API_KEY, MISTRAL_API_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_task_from_email(email_content):
    """
    Extrait les informations de tâche d'un email en utilisant l'API Mistral
    """
    if not MISTRAL_API_KEY:
        logger.error("Clé API Mistral non configurée")
        return None
    
    prompt = create_prompt(email_content)
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Nettoyer la réponse pour extraire le JSON
        json_str = extract_json_from_response(ai_response)
        
        if json_str:
            task_data = json.loads(json_str)
            logger.info("Tâche extraite avec succès")
            return task_data
        else:
            logger.error("Impossible d'extraire le JSON de la réponse")
            return create_fallback_task(email_content)
            
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API Mistral: {e}")
        return create_fallback_task(email_content)

def create_prompt(email_content):
    """
    Crée le prompt optimisé pour l'extraction de tâches
    """
    return f"""
Analyse le contenu de cet email et extrais les informations de tâche. 
Retourne UNIQUEMENT un objet JSON valide sans aucun texte supplémentaire.

Format JSON requis :
{{
    "tache": "description courte et précise de la tâche",
    "priorite": "basse, moyenne ou haute",
    "deadline": "date au format YYYY-MM-DD si présente, sinon null",
    "info": "informations complémentaires importantes"
}}

Règles d'extraction :
- La tâche doit être concise (max 10 mots)
- Priorité : "haute" pour urgent/délai court, "moyenne" pour normal, "basse" pour non urgent
- Deadline : extraire la date si mentionnée explicitement
- Info : contexte supplémentaire utile

Contenu de l'email :
{email_content[:2000]}  # Limite pour éviter les tokens excessifs

Réponse JSON :
"""

def extract_json_from_response(text):
    """
    Extrait le JSON de la réponse texte de l'IA
    """
    try:
        # Chercher le début et la fin du JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start != -1 and end != 0:
            json_str = text[start:end]
            # Valider que c'est du JSON valide
            json.loads(json_str)
            return json_str
    except:
        pass
    
    return None

def create_fallback_task(email_content):
    """
    Crée une tâche par défaut en cas d'échec de l'IA
    """
    # Extraire les premières lignes comme tâche
    lines = email_content.split('\n')
    subject_line = lines[0] if lines else "Tâche extraite de l'email"
    
    return {
        "tache": subject_line[:100],  # Limiter la longueur
        "priorite": "moyenne",
        "deadline": None,
        "info": "Extraction automatique (mode fallback)"
    }