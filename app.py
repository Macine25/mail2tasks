from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
from datetime import datetime

from email_reader import EmailReader
from ai_extractor import extract_task_from_email
from database import init_db, add_task, get_tasks, mark_task_done, delete_task, task_exists
from database import is_email_processed, mark_email_processed, clear_processed_emails, get_processed_emails_count
from config import KEYWORDS

app = Flask(__name__)
app.secret_key = 'mail2tasks_secret_key_2024'

# Initialisation de la base de données au démarrage
init_db()

@app.route('/')
def index():
    """Page principale - liste des tâches"""
    tasks = get_tasks(include_done=False)
    processed_count = get_processed_emails_count()
    return render_template('index.html', tasks=tasks, keywords=KEYWORDS, processed_count=processed_count)

@app.route('/sync')
def sync_emails():
    """Synchronisation avec les emails"""
    try:
        # Créer une instance de EmailReader
        reader = EmailReader()
        emails = reader.search_emails(mark_as_read=True)
        
        tasks_added = 0
        emails_processed = 0
        emails_skipped = 0
        
        for email_msg in emails:
            # Vérifier si cet email a déjà été traité
            if is_email_processed(email_msg['subject'], email_msg['body']):
                emails_skipped += 1
                continue
            
            # Combiner sujet et corps pour l'analyse
            email_content = f"Sujet: {email_msg['subject']}\n\nCorps: {email_msg['body']}"
            
            # Extraire la tâche avec l'IA
            task_data = extract_task_from_email(email_content)
            
            if task_data:
                # Vérifier si la tâche existe déjà (basé sur le texte)
                if not task_exists(task_data['tache'], task_data['deadline']):
                    add_task(
                        tache=task_data['tache'],
                        priorite=task_data['priorite'],
                        deadline=task_data['deadline'],
                        info=task_data['info']
                    )
                    tasks_added += 1
                
                # Marquer l'email comme traité (même si la tâche existait déjà)
                mark_email_processed(email_msg['subject'], email_msg['body'])
                emails_processed += 1
        
        # Messages selon le résultat
        if tasks_added > 0:
            flash(f'✅ {tasks_added} nouvelles tâches ajoutées! ({emails_processed} emails traités)', 'success')
        else:
            if emails_processed > 0:
                flash(f'ℹ️ Aucune nouvelle tâche trouvée ({emails_processed} emails analysés)', 'info')
            elif emails_skipped > 0:
                flash(f'🔁 Tous les emails ont déjà été traités ({emails_skipped} emails ignorés)', 'info')
            else:
                flash('📭 Aucun email à traiter', 'info')
            
    except Exception as e:
        flash(f'❌ Erreur lors de la synchronisation: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_task_manual():
    """Ajout manuel d'une tâche"""
    if request.method == 'POST':
        tache = request.form.get('tache', '').strip()
        priorite = request.form.get('priorite', 'moyenne')
        deadline = request.form.get('deadline', '') or None
        info = request.form.get('info', '').strip()
        
        if not tache:
            flash('La description de la tâche est obligatoire', 'error')
            return render_template('add_task.html')
        
        try:
            add_task(tache, priorite, deadline, info)
            flash('Tâche ajoutée avec succès!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erreur lors de l\'ajout: {str(e)}', 'error')
    
    return render_template('add_task.html')

@app.route('/delete/<int:task_id>')
def delete_task_route(task_id):
    """Suppression d'une tâche"""
    try:
        delete_task(task_id)
        flash('Tâche supprimée avec succès!', 'success')
    except Exception as e:
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/done/<int:task_id>')
def mark_task_done_route(task_id):
    """Marquer une tâche comme terminée"""
    try:
        mark_task_done(task_id)
        flash('Tâche marquée comme terminée!', 'success')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/tasks')
def api_tasks():
    """API pour récupérer les tâches (format JSON)"""
    tasks = get_tasks(include_done=False)
    return jsonify(tasks)

@app.route('/debug-email')
def debug_email():
    """Route pour debugger la connexion email"""
    from email_reader import debug_email_connection_imaplib
    
    try:
        success = debug_email_connection_imaplib()
        if success:
            flash('✅ Debug réussi - Vérifiez les logs pour les détails', 'success')
        else:
            flash('❌ Debug échoué - Vérifiez les logs pour les erreurs', 'error')
    except Exception as e:
        flash(f'💥 Erreur lors du debug: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/reset-processed')
def reset_processed_emails():
    """Réinitialise la liste des emails traités"""
    try:
        clear_processed_emails()
        flash('✅ Liste des emails traités réinitialisée! Vous pouvez resynchroniser.', 'success')
    except Exception as e:
        flash(f'❌ Erreur lors de la réinitialisation: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    flash('Page non trouvée', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    flash('Erreur interne du serveur', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)