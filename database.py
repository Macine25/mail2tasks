import sqlite3
import logging
import hashlib
from datetime import datetime
from config import DATABASE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tache TEXT NOT NULL,
            priorite TEXT NOT NULL,
            deadline TEXT,
            info TEXT,
            status INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NOUVELLE TABLE pour suivre les emails déjà traités
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_subject TEXT NOT NULL,
            email_body_hash TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Base de données initialisée")

def add_task(tache, priorite, deadline=None, info=""):
    """Ajoute une nouvelle tâche à la base de données"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks (tache, priorite, deadline, info, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (tache, priorite, deadline, info, 0))
    
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    logger.info(f"Tâche ajoutée: {tache}")
    return task_id

def get_tasks(include_done=False):
    """Récupère toutes les tâches"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if include_done:
        cursor.execute('''
            SELECT id, tache, priorite, deadline, info, status, created_at
            FROM tasks ORDER BY created_at DESC
        ''')
    else:
        cursor.execute('''
            SELECT id, tache, priorite, deadline, info, status, created_at
            FROM tasks WHERE status = 0 ORDER BY created_at DESC
        ''')
    
    tasks = cursor.fetchall()
    conn.close()
    
    # Formatage des tâches
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            'id': task[0],
            'tache': task[1],
            'priorite': task[2],
            'deadline': task[3],
            'info': task[4],
            'status': task[5],
            'created_at': task[6]
        })
    
    return formatted_tasks

def mark_task_done(task_id):
    """Marque une tâche comme terminée"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE tasks SET status = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    logger.info(f"Tâche {task_id} marquée comme terminée")
    return True

def delete_task(task_id):
    """Supprime une tâche"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    
    logger.info(f"Tâche {task_id} supprimée")
    return True

def task_exists(tache, deadline=None):
    """Vérifie si une tâche similaire existe déjà"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if deadline:
        cursor.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE tache LIKE ? AND deadline = ? AND status = 0
        ''', (f'%{tache}%', deadline))
    else:
        cursor.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE tache LIKE ? AND status = 0
        ''', (f'%{tache}%',))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

# NOUVELLES FONCTIONS POUR GÉRER LES EMAILS TRAITÉS

def is_email_processed(subject, body):
    """Vérifie si un email a déjà été traité"""
    body_hash = hashlib.md5(body.encode('utf-8')).hexdigest()
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM processed_emails 
        WHERE email_subject = ? AND email_body_hash = ?
    ''', (subject, body_hash))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    is_processed = count > 0
    if is_processed:
        logger.info(f"📧 Email déjà traité: {subject[:50]}...")
    
    return is_processed

def mark_email_processed(subject, body):
    """Marque un email comme traité"""
    body_hash = hashlib.md5(body.encode('utf-8')).hexdigest()
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO processed_emails (email_subject, email_body_hash)
        VALUES (?, ?)
    ''', (subject, body_hash))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Email marqué comme traité: {subject[:50]}...")
    return True

def clear_processed_emails():
    """Vide la table des emails traités (pour les tests)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM processed_emails')
    
    conn.commit()
    conn.close()
    
    logger.info("🗑️ Table processed_emails vidée")
    return True

def get_processed_emails_count():
    """Retourne le nombre d'emails traités"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM processed_emails')
    count = cursor.fetchone()[0]
    conn.close()
    
    return count