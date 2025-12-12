import imaplib
import email
from email.policy import default
import logging
from config import IMAP_SERVER, IMAP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, KEYWORDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_emails():
    """
    Version corrigée utilisant imaplib au lieu de IMAPClient
    """
    mail = None
    try:
        logger.info("🚀 Démarrage de la recherche d'emails (imaplib)...")
        
        # Connexion avec imaplib (plus stable)
        logger.info(f"🔗 Connexion à {IMAP_SERVER}:{IMAP_PORT}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.timeout = 30
        
        logger.info("🔑 Authentification...")
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        logger.info("✅ Authentification réussie")
        
        # Sélection de la boîte de réception
        mail.select('INBOX')
        logger.info("📂 Boîte INBOX sélectionnée")
        
        # Recherche de tous les emails
        status, messages = mail.search(None, 'ALL')
        if status != 'OK':
            logger.error("❌ Erreur lors de la recherche d'emails")
            return []
        
        email_ids = messages[0].split()
        logger.info(f"📧 {len(email_ids)} emails trouvés")
        
        # Limiter aux 10 derniers emails
        test_ids = email_ids[-10:] if len(email_ids) > 10 else email_ids
        logger.info(f"🔍 Analyse de {len(test_ids)} emails")
        
        relevant_emails = []
        
        for i, email_id in enumerate(test_ids):
            try:
                logger.info(f"--- Email {i+1}/{len(test_ids)} (ID: {email_id}) ---")
                
                # Récupération de l'email
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    logger.warning(f"Impossible de récupérer l'email {email_id}")
                    continue
                
                # Extraction du message
                msg = email.message_from_bytes(msg_data[0][1], policy=default)
                
                # Extraction des informations
                subject = str(msg.get('subject', 'Sans sujet')).strip()
                from_addr = str(msg.get('from', 'Expéditeur inconnu'))
                date = str(msg.get('date', 'Date inconnue'))
                body = extract_body_imaplib(msg)
                
                logger.info(f"📨 Sujet: {subject[:50]}...")
                
                # Recherche des mots-clés
                full_text = f"{subject} {body}".lower()
                found_keywords = [kw for kw in KEYWORDS if kw.lower() in full_text]
                
                if found_keywords:
                    logger.info(f"✅ MOTS-CLÉS TROUVÉS: {', '.join(found_keywords[:3])}...")
                    
                    email_info = {
                        'subject': subject,
                        'body': body,
                        'from': from_addr,
                        'date': date,
                        'keywords': found_keywords
                    }
                    relevant_emails.append(email_info)
                else:
                    logger.info("❌ Aucun mot-clé détecté")
                    
            except Exception as e:
                logger.error(f"⚠️ Erreur email {email_id}: {str(e)}")
                continue
        
        mail.close()
        mail.logout()
        logger.info(f"🎉 RECHERCHE TERMINÉE: {len(relevant_emails)} emails pertinents")
        return relevant_emails
        
    except Exception as e:
        logger.error(f"💥 ERREUR GÉNÉRALE: {str(e)}")
        if mail:
            try:
                mail.close()
                mail.logout()
            except:
                pass
        return []

def extract_body_imaplib(msg):
    """Extrait le corps texte avec imaplib"""
    try:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='ignore')
                            break
                    except Exception as e:
                        logger.warning(f"Erreur décodage: {e}")
        else:
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                except Exception as e:
                    logger.warning(f"Erreur décodage email simple: {e}")
        
        # Nettoyage
        if body:
            body = ' '.join(body.split())[:5000]
        
        return body or "Aucun contenu texte trouvé"
    except Exception as e:
        logger.error(f"Erreur extraction: {e}")
        return "Erreur extraction"

def debug_email_connection_imaplib():
    """Debug avec imaplib"""
    try:
        logger.info("🔧 DEBUG AVEC IMAPLIB")
        logger.info(f"📧 Email: {EMAIL_ADDRESS}")
        logger.info(f"🔑 Mot de passe: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else 'NON'}")
        logger.info(f"🌐 Serveur: {IMAP_SERVER}:{IMAP_PORT}")
        
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            logger.error("❌ Email ou mot de passe manquant")
            return False
        
        # Test connexion
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.timeout = 15
        
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        logger.info("✅ Authentification réussie!")
        
        mail.select('INBOX')
        status, messages = mail.search(None, 'ALL')
        
        if status == 'OK':
            email_ids = messages[0].split()
            logger.info(f"✅ {len(email_ids)} emails trouvés")
            
            if email_ids:
                # Test lecture d'un email
                status, msg_data = mail.fetch(email_ids[-1], '(RFC822)')
                if status == 'OK':
                    msg = email.message_from_bytes(msg_data[0][1], policy=default)
                    subject = str(msg.get('subject', 'Sans sujet'))
                    logger.info(f"✅ Test lecture: {subject[:30]}...")
        
        mail.close()
        mail.logout()
        logger.info("🎉 DEBUG RÉUSSI - Tout fonctionne!")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERREUR DEBUG: {str(e)}")
        return False

# Classe pour la compatibilité
class EmailReader:
    def search_emails(self, mark_as_read=True):
        return search_emails()
    
    def disconnect(self):
        pass
    
    def debug_connection(self):
        return debug_email_connection_imaplib()