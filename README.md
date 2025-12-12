# 📧 Mail2Tasks - Gestionnaire de Tâches depuis Emails

## 📋 Description
Application Flask qui extrait automatiquement des tâches depuis vos emails en utilisant l'intelligence artificielle (Mistral AI).

## ✨ Fonctionnalités
- 🔄 Synchronisation automatique avec votre boîte email
- 🧠 Extraction intelligente des tâches avec IA Mistral
- 🎨 Interface web intuitive et responsive
- 🔒 Système anti-doublons intégré
- 🚦 Priorisation automatique (basse/moyenne/haute)
- 📅 Détection automatique des deadlines
- ➕ Ajout manuel de tâches

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Compte email avec IMAP activé
- Clé API Mistral (gratuite sur [mistral.ai](https://mistral.ai))

### Étapes d'installation
```bash
# 1. Cloner le dépôt
git clone https://github.com/Macine25/mail2tasks.git
cd mail2tasks

# 2. Créer environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows :
venv\Scripts\activate
# Mac/Linux :
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer l'application
cp .env.example .env
# Éditer le fichier .env avec vos informations
