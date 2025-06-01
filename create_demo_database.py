#!/usr/bin/env python3
"""
Script per creare un database di esempio con transazioni demo
Genera 20 transazioni (10 entrate e 10 uscite) con dati realistici
"""

import sys
import os
import json
from datetime import datetime, timedelta, date
from decimal import Decimal
import random

# Aggiungi la directory corrente al path per importare i moduli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import dei moduli del progetto
from database_config import DatabaseManager, DatabaseRegistry, FileManager
from categories import DefaultCategories
from models import Transaction, Category

class DemoDataGenerator:
    """Generatore di dati demo realistici"""
    
    # Dati demo per entrate
    ENTRATE_DEMO = [
        {"description": "Stipendio Gennaio", "amount": 2800.00, "category": "💼 Stipendio", "tags": ["lavoro", "fisso"]},
        {"description": "Freelance Web Design", "amount": 850.00, "category": "💻 Freelance", "tags": ["freelance", "design"]},
        {"description": "Dividendi Azioni Apple", "amount": 145.30, "category": "📈 Investimenti", "tags": ["dividendi", "azioni"]},
        {"description": "Vendita Oggetti Usati", "amount": 320.00, "category": "💰 Altro Entrate", "tags": ["vendita", "usato"]},
        {"description": "Consulenza Programmazione", "amount": 650.00, "category": "💻 Freelance", "tags": ["programmazione", "consulenza"]},
        {"description": "Bonus Performance", "amount": 500.00, "category": "🎁 Bonus", "tags": ["bonus", "performance"]},
        {"description": "Rimborso Spese Mediche", "amount": 180.00, "category": "↩️ Rimborsi", "tags": ["rimborso", "medico"]},
        {"description": "Interessi Conto Deposito", "amount": 78.50, "category": "📈 Investimenti", "tags": ["interessi", "deposito"]},
        {"description": "Regalo Compleanno", "amount": 200.00, "category": "🎁 Bonus", "tags": ["regalo", "compleanno"]},
        {"description": "Progetto E-commerce", "amount": 1200.00, "category": "💻 Freelance", "tags": ["ecommerce", "progetto"]}
    ]
    
    # Dati demo per uscite
    USCITE_DEMO = [
        {"description": "Affitto Appartamento", "amount": 950.00, "category": "🏠 Casa", "tags": ["affitto", "casa"]},
        {"description": "Spesa Supermercato", "amount": 85.60, "category": "🛒 Alimentari", "tags": ["spesa", "alimentari"]},
        {"description": "Bolletta Elettricità", "amount": 127.30, "category": "💡 Utility", "tags": ["bolletta", "elettricità"]},
        {"description": "Carburante Auto", "amount": 65.00, "category": "🚗 Trasporti", "tags": ["carburante", "auto"]},
        {"description": "Visita Dentista", "amount": 180.00, "category": "🏥 Sanità", "tags": ["dentista", "salute"]},
        {"description": "Corso Online Python", "amount": 89.99, "category": "📚 Educazione", "tags": ["corso", "programmazione"]},
        {"description": "Cena Ristorante", "amount": 45.50, "category": "🎉 Svago", "tags": ["ristorante", "cena"]},
        {"description": "Maglietta e Jeans", "amount": 68.00, "category": "👕 Abbigliamento", "tags": ["vestiti", "casual"]},
        {"description": "Smartphone Cover", "amount": 25.99, "category": "📱 Tecnologia", "tags": ["accessori", "telefono"]},
        {"description": "Regalo Anniversario", "amount": 120.00, "category": "🎁 Regali", "tags": ["regalo", "anniversario"]}
    ]
    
    @staticmethod
    def generate_random_date(days_back=90):
        """Genera una data casuale negli ultimi X giorni"""
        base_date = datetime.now() - timedelta(days=days_back)
        random_days = random.randint(0, days_back)
        return base_date + timedelta(days=random_days)
    
    @staticmethod
    def add_random_variation(amount, variation_percent=0.1):
        """Aggiunge una variazione casuale all'importo"""
        variation = amount * variation_percent
        return round(amount + random.uniform(-variation, variation), 2)

def create_demo_database():
    """Crea un database demo con transazioni di esempio"""
    
    print("🚀 Creazione Database Demo - Budget Familiare")
    print("=" * 50)
    
    # 1. Assicurati che esistano le cartelle
    print("📁 Verifica struttura cartelle...")
    FileManager.ensure_directories()
    
    # 2. Crea il database manager
    db_name = "budget_demo"
    print(f"🗄️ Creazione database: {db_name}.db")
    
    try:
        db_manager = DatabaseManager('sqlite', db_name=db_name)
        
        # 3. Crea le tabelle
        print("🏗️ Creazione tabelle database...")
        if not db_manager.create_tables():
            print("❌ Errore nella creazione delle tabelle")
            return False
        
        # 4. Aggiungi categorie di default
        print("🏷️ Aggiunta categorie di default...")
        DefaultCategories.ensure_default_categories(db_manager)
        
        # 5. Recupera le categorie per mappare i nomi agli ID
        print("📋 Mappatura categorie...")
        category_mapping = {}
        
        with db_manager.get_session() as session:
            categories = session.query(Category).all()
            for cat in categories:
                category_mapping[cat.name] = cat.id
        
        print(f"✅ Trovate {len(category_mapping)} categorie")
        
        # 6. Genera e inserisci transazioni demo
        print("💳 Generazione transazioni demo...")
        
        demo_generator = DemoDataGenerator()
        transactions_added = 0
        
        with db_manager.get_session() as session:
            
            # Aggiungi entrate
            print("📈 Aggiunta entrate...")
            for i, entrata_data in enumerate(demo_generator.ENTRATE_DEMO):
                category_id = category_mapping.get(entrata_data['category'])
                
                if not category_id:
                    print(f"⚠️ Categoria non trovata: {entrata_data['category']}")
                    continue
                
                # Genera data casuale
                transaction_date = demo_generator.generate_random_date()
                
                # Aggiungi variazione all'importo
                amount = demo_generator.add_random_variation(entrata_data['amount'])
                
                transaction = Transaction(
                    date=transaction_date,
                    amount=amount,
                    description=entrata_data['description'],
                    notes=f"Transazione demo generata automaticamente il {datetime.now().strftime('%d/%m/%Y')}",
                    category_id=category_id,
                    transaction_type='Entrata',
                    recurrence_type='Nessuna',
                    tags=','.join(entrata_data['tags']),
                    metadata_json=json.dumps({
                        'demo': True,
                        'generated_date': datetime.now().isoformat(),
                        'original_amount': entrata_data['amount']
                    })
                )
                
                session.add(transaction)
                transactions_added += 1
                print(f"  ✅ {entrata_data['description']}: €{amount:.2f}")
            
            # Aggiungi uscite
            print("📉 Aggiunta uscite...")
            for i, uscita_data in enumerate(demo_generator.USCITE_DEMO):
                category_id = category_mapping.get(uscita_data['category'])
                
                if not category_id:
                    print(f"⚠️ Categoria non trovata: {uscita_data['category']}")
                    continue
                
                # Genera data casuale
                transaction_date = demo_generator.generate_random_date()
                
                # Aggiungi variazione all'importo
                amount = demo_generator.add_random_variation(uscita_data['amount'])
                
                transaction = Transaction(
                    date=transaction_date,
                    amount=amount,
                    description=uscita_data['description'],
                    notes=f"Transazione demo generata automaticamente il {datetime.now().strftime('%d/%m/%Y')}",
                    category_id=category_id,
                    transaction_type='Uscita',
                    recurrence_type='Nessuna',
                    tags=','.join(uscita_data['tags']),
                    metadata_json=json.dumps({
                        'demo': True,
                        'generated_date': datetime.now().isoformat(),
                        'original_amount': uscita_data['amount']
                    })
                )
                
                session.add(transaction)
                transactions_added += 1
                print(f"  ✅ {uscita_data['description']}: €{amount:.2f}")
            
            # Commit delle transazioni
            session.commit()
        
        # 7. Registra il database nel registry
        print("📝 Registrazione database nel registry...")
        DatabaseRegistry.add_database_config(
            "Database Demo",
            'sqlite',
            db_name=db_name
        )
        
        # 8. Statistiche finali
        print("\n🎊 Database Demo Creato con Successo!")
        print("=" * 50)
        
        # Calcola statistiche
        with db_manager.get_session() as session:
            total_entrate = session.query(Transaction).filter_by(transaction_type='Entrata').count()
            total_uscite = session.query(Transaction).filter_by(transaction_type='Uscita').count()
            
            from sqlalchemy.sql import func
            sum_entrate = session.query(func.sum(Transaction.amount)).filter_by(transaction_type='Entrata').scalar() or 0
            sum_uscite = session.query(func.sum(Transaction.amount)).filter_by(transaction_type='Uscita').scalar() or 0
            
            saldo = sum_entrate - sum_uscite
        
        print(f"📊 Statistiche Database:")
        print(f"  📁 File: data/{db_name}.db")
        print(f"  📈 Entrate: {total_entrate} transazioni (€{sum_entrate:.2f})")
        print(f"  📉 Uscite: {total_uscite} transazioni (€{sum_uscite:.2f})")
        print(f"  💰 Saldo: €{saldo:.2f}")
        print(f"  🏷️ Categorie: {len(category_mapping)}")
        print(f"  📅 Periodo: Ultimi 90 giorni")
        
        print("\n🚀 Come utilizzare il database demo:")
        print("1. Avvia l'applicazione: streamlit run family_budget_app.py")
        print("2. Vai in 'Gestione Database' → 'Database Lista'")
        print("3. Seleziona 'Database Demo' per visualizzare i dati")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante la creazione del database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Funzione principale"""
    
    print("🎯 Script Generazione Database Demo")
    print("Questo script creerà un database di esempio con 20 transazioni")
    
    # Chiedi conferma
    response = input("\n❓ Vuoi continuare? (s/n): ").lower().strip()
    
    if response not in ['s', 'si', 'sì', 'y', 'yes']:
        print("❌ Operazione annullata dall'utente")
        return
    
    # Controlla se il database demo esiste già
    demo_db_path = FileManager.get_data_path("budget_demo.db")
    if demo_db_path.exists():
        print(f"\n⚠️ Il file {demo_db_path} esiste già!")
        overwrite = input("🔄 Vuoi sovrascriverlo? (s/n): ").lower().strip()
        
        if overwrite in ['s', 'si', 'sì', 'y', 'yes']:
            print("🗑️ Rimozione database esistente...")
            demo_db_path.unlink()
        else:
            print("❌ Operazione annullata")
            return
    
    # Crea il database demo
    success = create_demo_database()
    
    if success:
        print("\n🎉 Database demo creato con successo!")
        print("✨ Puoi ora testare l'applicazione con dati realistici")
    else:
        print("\n💥 Errore nella creazione del database demo")
        print("🔍 Controlla i log sopra per i dettagli")

if __name__ == "__main__":
    main()