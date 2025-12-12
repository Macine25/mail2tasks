import os
from dotenv import load_dotenv

load_dotenv()

# Configuration IMAP
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
IMAP_PORT = int(os.getenv('IMAP_PORT', 993))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Configuration Mistral AI
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# 🔥 LISTE ÉTENDUE DES MOTS-CLÉS
KEYWORDS = [
    'urgent', 'action', 'à faire', 'deadline', 'important', 
    'tâche', 'task', 'réunion', 'meeting', 'projet', 'project',
    'préparer', 'préparation', 'todo', 'à réaliser', 'work',
    'travail', 'dossier', 'file', 'document', 'rapport',
    'dead line', 'échéance', 'reminder', 'rappeler', 'check',
    'vérifier', 'confirmer', 'valider', 'envoyer', 'mail',
    'email', 'message', 'contact', 'appel', 'call',
    'urgence', 'important', 'crucial', 'essentiel', 'nécessaire',
    'besoin', 'demande', 'request', 'required', 'must',
    'doit', 'devoir', 'obligatoire', 'impératif', 'priorité',
    'priority', 'high', 'haute', 'moyenne', 'basse',
    'asap', 'soon', 'rapidement', 'quick', 'fast',
    'livrable', 'deliverable', 'rendre', 'submit', 'due',
    'échéance', 'date limite', 'time limit', 'schedule',
    'calendrier', 'agenda', 'planning', 'plan', 'prévu',
    'prévoir', 'organiser', 'coordinate', 'gérer', 'manage',
    'superviser', 'supervise', 'contrôler', 'control', 'review',
    'réviser', 'corriger', 'correct', 'fix', 'repair',
    'réparer', 'modifier', 'modify', 'changer', 'change',
    'update', 'mettre à jour', 'upgrade', 'améliorer', 'improve',
    'créer', 'create', 'nouveau', 'new', 'develop', 'développer',
    'test', 'tester', 'valider', 'validate', 'approuver', 'approve',
    'signer', 'sign', 'confirmer', 'confirm', 'finaliser', 'finalize',
    'répondre', 'reply', 'answer', 'solution', 'résoudre', 'solve',
    'probleme', 'problem', 'issue', 'bug', 'erreur', 'error',
    'correction', 'correctif', 'hotfix', 'patch', 'correct'
]

# Configuration de la base de données
DATABASE_NAME = 'tasks.db'