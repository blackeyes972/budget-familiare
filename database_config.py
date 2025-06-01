# database_config.py
"""
Modulo avanzato per la configurazione e gestione database multipli.
Supporta creazione, switching e gestione configurazioni multiple.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


class FileManager:
    """Manager per la gestione organizzata dei file dell'applicazione"""
    
    # Definizione cartelle
    BASE_DIR = Path(".")
    DATA_DIR = BASE_DIR / "data"
    CONFIG_DIR = BASE_DIR / "config"
    BACKUPS_DIR = BASE_DIR / "backups"
    EXPORTS_DIR = BASE_DIR / "exports"
    LOGS_DIR = BASE_DIR / "logs"
    
    @classmethod
    def ensure_directories(cls):
        """Crea le cartelle necessarie se non esistono"""
        directories = [
            cls.DATA_DIR,
            cls.CONFIG_DIR, 
            cls.BACKUPS_DIR,
            cls.EXPORTS_DIR,
            cls.LOGS_DIR
        ]
        
        for directory in directories:
            try:
                directory.mkdir(exist_ok=True)
                print(f"📁 Cartella verificata: {directory}")
            except Exception as e:
                print(f"❌ Errore creazione cartella {directory}: {e}")
    
    @classmethod
    def migrate_existing_files(cls) -> List[str]:
        """Sposta i file esistenti nelle cartelle appropriate"""
        moved_files = []
        
        try:
            # Database files (.db) -> data/
            for db_file in cls.BASE_DIR.glob("*.db"):
                if db_file.name != "database_configs.json":  # Skip config file
                    new_path = cls.DATA_DIR / db_file.name
                    if not new_path.exists():
                        shutil.move(str(db_file), str(new_path))
                        moved_files.append(f"{db_file.name} -> data/")
            
            # JSON config files -> config/
            config_files = ["database_configs.json"]
            for config_name in config_files:
                config_file = cls.BASE_DIR / config_name
                if config_file.exists():
                    new_path = cls.CONFIG_DIR / config_name
                    if not new_path.exists():
                        shutil.move(str(config_file), str(new_path))
                        moved_files.append(f"{config_name} -> config/")
            
            # Backup files -> backups/
            for backup_file in cls.BASE_DIR.glob("backup_*"):
                new_path = cls.BACKUPS_DIR / backup_file.name
                if not new_path.exists():
                    shutil.move(str(backup_file), str(new_path))
                    moved_files.append(f"{backup_file.name} -> backups/")
            
            # Export files -> exports/
            for export_file in cls.BASE_DIR.glob("*_export_*.json"):
                new_path = cls.EXPORTS_DIR / export_file.name
                if not new_path.exists():
                    shutil.move(str(export_file), str(new_path))
                    moved_files.append(f"{export_file.name} -> exports/")
            
            # Log files -> logs/
            for log_file in cls.BASE_DIR.glob("*.log"):
                new_path = cls.LOGS_DIR / log_file.name
                if not new_path.exists():
                    shutil.move(str(log_file), str(new_path))
                    moved_files.append(f"{log_file.name} -> logs/")
                    
        except Exception as e:
            print(f"⚠️ Errore durante migrazione file: {e}")
        
        return moved_files
    
    @classmethod
    def get_backup_path(cls, filename: str) -> Path:
        """Restituisce il percorso completo per un file di backup"""
        return cls.BACKUPS_DIR / filename
    
    @classmethod
    def get_export_path(cls, filename: str) -> Path:
        """Restituisce il percorso completo per un file di export"""
        return cls.EXPORTS_DIR / filename
    
    @classmethod
    def get_data_path(cls, filename: str) -> Path:
        """Restituisce il percorso completo per un file di dati"""
        return cls.DATA_DIR / filename
    
    @classmethod
    def get_config_path(cls, filename: str) -> Path:
        """Restituisce il percorso completo per un file di configurazione"""
        return cls.CONFIG_DIR / filename
    
    @classmethod
    def get_log_path(cls, filename: str) -> Path:
        """Restituisce il percorso completo per un file di log"""
        return cls.LOGS_DIR / filename
    
    @classmethod
    def list_files_by_type(cls) -> Dict[str, List[str]]:
        """Elenca tutti i file organizzati per tipo"""
        file_types = {
            'databases': [],
            'configs': [],
            'backups': [],
            'exports': [],
            'logs': []
        }
        
        try:
            # Database files
            if cls.DATA_DIR.exists():
                file_types['databases'] = [f.name for f in cls.DATA_DIR.glob("*.db")]
            
            # Config files
            if cls.CONFIG_DIR.exists():
                file_types['configs'] = [f.name for f in cls.CONFIG_DIR.glob("*.json")]
            
            # Backup files
            if cls.BACKUPS_DIR.exists():
                file_types['backups'] = [f.name for f in cls.BACKUPS_DIR.iterdir() if f.is_file()]
            
            # Export files
            if cls.EXPORTS_DIR.exists():
                file_types['exports'] = [f.name for f in cls.EXPORTS_DIR.glob("*.json")]
            
            # Log files
            if cls.LOGS_DIR.exists():
                file_types['logs'] = [f.name for f in cls.LOGS_DIR.glob("*.log")]
                
        except Exception as e:
            print(f"❌ Errore elencazione file: {e}")
        
        return file_types
    
    @classmethod
    def cleanup_old_files(cls, days_old: int = 30) -> List[str]:
        """Elimina file più vecchi del numero di giorni specificato"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_files = []
        
        try:
            # Cleanup directories to check
            cleanup_dirs = [cls.BACKUPS_DIR, cls.EXPORTS_DIR, cls.LOGS_DIR]
            
            for directory in cleanup_dirs:
                if not directory.exists():
                    continue
                
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        # Check file modification time
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        if file_mtime < cutoff_date:
                            try:
                                file_path.unlink()
                                cleaned_files.append(f"{directory.name}/{file_path.name}")
                            except Exception as e:
                                print(f"⚠️ Errore eliminazione {file_path}: {e}")
                                
        except Exception as e:
            print(f"❌ Errore durante pulizia: {e}")
        
        return cleaned_files
    
    @classmethod
    def get_file_info(cls, file_type: str, filename: str) -> Optional[Dict]:
        """Ottiene informazioni dettagliate su un file"""
        try:
            if file_type == 'databases':
                file_path = cls.DATA_DIR / filename
            elif file_type == 'configs':
                file_path = cls.CONFIG_DIR / filename
            elif file_type == 'backups':
                file_path = cls.BACKUPS_DIR / filename
            elif file_type == 'exports':
                file_path = cls.EXPORTS_DIR / filename
            elif file_type == 'logs':
                file_path = cls.LOGS_DIR / filename
            else:
                return None
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            return {
                'name': filename,
                'path': str(file_path),
                'size_bytes': stat.st_size,
                'size_human': f"{stat.st_size / 1024:.1f} KB",
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'type': file_type
            }
            
        except Exception as e:
            print(f"❌ Errore info file {filename}: {e}")
            return None


class DatabaseRegistry:
    """Registro per gestire configurazioni database multiple"""
    
    CONFIG_FILE = "database_configs.json"
    
    @classmethod
    def _get_config_path(cls):
        """Ottiene il percorso del file di configurazione"""
        return FileManager.get_config_path(cls.CONFIG_FILE)
    
    @classmethod
    def load_configs(cls) -> Dict:
        """Carica configurazioni database salvate"""
        try:
            config_path = cls._get_config_path()
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Errore caricamento configurazioni: {e}")
        
        return {
            'databases': {},
            'current_database': None,
            'last_used': None
        }
    
    @classmethod
    def save_configs(cls, configs: Dict):
        """Salva configurazioni database"""
        try:
            config_path = cls._get_config_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Errore salvataggio configurazioni: {e}")
    
    @classmethod
    def add_database_config(cls, name: str, db_type: str, **params) -> bool:
        """Aggiunge nuova configurazione database"""
        configs = cls.load_configs()
        
        if name in configs['databases']:
            return False  # Nome già esistente
        
        configs['databases'][name] = {
            'type': db_type,
            'params': params,
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'is_active': True
        }
        
        cls.save_configs(configs)
        return True
    
    @classmethod
    def update_database_config(cls, name: str, **updates) -> bool:
        """Aggiorna configurazione esistente"""
        configs = cls.load_configs()
        
        if name not in configs['databases']:
            return False
        
        configs['databases'][name].update(updates)
        configs['databases'][name]['updated_at'] = datetime.now().isoformat()
        
        cls.save_configs(configs)
        return True
    
    @classmethod
    def remove_database_config(cls, name: str) -> bool:
        """Rimuove configurazione database"""
        configs = cls.load_configs()
        
        if name not in configs['databases']:
            return False
        
        del configs['databases'][name]
        
        # Update current if was the current one
        if configs['current_database'] == name:
            configs['current_database'] = None
        
        cls.save_configs(configs)
        return True
    
    @classmethod
    def set_current_database(cls, name: str):
        """Imposta database corrente"""
        configs = cls.load_configs()
        configs['current_database'] = name
        configs['last_used'] = datetime.now().isoformat()
        
        if name in configs['databases']:
            configs['databases'][name]['last_used'] = datetime.now().isoformat()
        
        cls.save_configs(configs)
    
    @classmethod
    def get_current_database_config(cls) -> Optional[Dict]:
        """Ottiene configurazione database corrente"""
        configs = cls.load_configs()
        current_name = configs.get('current_database')
        
        if current_name and current_name in configs['databases']:
            config = configs['databases'][current_name].copy()
            config['name'] = current_name
            return config
        
        return None
    
    @classmethod
    def list_database_configs(cls) -> List[Dict]:
        """Lista tutte le configurazioni database"""
        configs = cls.load_configs()
        result = []
        
        for name, config in configs['databases'].items():
            config_copy = config.copy()
            config_copy['name'] = name
            config_copy['is_current'] = (name == configs.get('current_database'))
            result.append(config_copy)
        
        # Sort by last used
        result.sort(key=lambda x: x.get('last_used') or '1970-01-01', reverse=True)
        return result


class DatabaseConfig:
    """Configurazione database multi-ambiente"""
    
    SUPPORTED_DATABASES = {
        'sqlite': {
            'name': 'SQLite',
            'description': 'Database embedded, ideale per sviluppo e uso personale',
            'url_template': 'sqlite:///{db_path}',
            'driver_package': None,
            'features': ['basic', 'local_storage', 'zero_config'],
            'icon': '📁',
            'color': '#4CAF50',
            'fields': [
                {'name': 'db_name', 'label': 'Nome File Database', 'type': 'text', 'default': 'budget_famiglia', 'required': True}
            ]
        },
        'postgresql': {
            'name': 'PostgreSQL',
            'description': 'Database professionale con funzionalità avanzate',
            'url_template': 'postgresql://{user}:{password}@{host}:{port}/{db_name}',
            'driver_package': 'psycopg2-binary',
            'features': ['json', 'fulltext', 'advanced_analytics', 'window_functions'],
            'icon': '🐘',
            'color': '#336791',
            'fields': [
                {'name': 'host', 'label': 'Host', 'type': 'text', 'default': 'localhost', 'required': True},
                {'name': 'port', 'label': 'Porta', 'type': 'number', 'default': 5432, 'required': True},
                {'name': 'db_name', 'label': 'Nome Database', 'type': 'text', 'default': 'budget_famiglia', 'required': True},
                {'name': 'user', 'label': 'Username', 'type': 'text', 'default': 'budget_user', 'required': True},
                {'name': 'password', 'label': 'Password', 'type': 'password', 'default': '', 'required': True}
            ]
        },
        'mysql': {
            'name': 'MySQL',
            'description': 'Database popolare per applicazioni web',
            'url_template': 'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}',
            'driver_package': 'PyMySQL',
            'features': ['json', 'basic_analytics', 'web_oriented'],
            'icon': '🐬',
            'color': '#4479A1',
            'fields': [
                {'name': 'host', 'label': 'Host', 'type': 'text', 'default': 'localhost', 'required': True},
                {'name': 'port', 'label': 'Porta', 'type': 'number', 'default': 3306, 'required': True},
                {'name': 'db_name', 'label': 'Nome Database', 'type': 'text', 'default': 'budget_famiglia', 'required': True},
                {'name': 'user', 'label': 'Username', 'type': 'text', 'default': 'budget_user', 'required': True},
                {'name': 'password', 'label': 'Password', 'type': 'password', 'default': '', 'required': True}
            ]
        }
    }
    
    @classmethod
    def get_available_databases(cls) -> List[Dict]:
        """Restituisce database disponibili nel sistema"""
        available = []
        
        for db_type, config in cls.SUPPORTED_DATABASES.items():
            is_available = cls._check_driver(db_type)
            
            db_info = config.copy()
            db_info['type'] = db_type
            db_info['available'] = is_available
            
            if not is_available and config['driver_package']:
                db_info['install_command'] = f"pip install {config['driver_package']}"
            
            available.append(db_info)
        
        return available
    
    @classmethod
    def _check_driver(cls, db_type: str) -> bool:
        """Verifica disponibilità driver"""
        if db_type == 'sqlite':
            return True
        
        try:
            if db_type == 'postgresql':
                import psycopg2
                return True
            elif db_type == 'mysql':
                import pymysql
                return True
        except ImportError:
            return False
        
        return False
    
    @classmethod
    def get_database_url(cls, db_type: str, **kwargs) -> str:
        """Genera URL database"""
        if db_type not in cls.SUPPORTED_DATABASES:
            raise ValueError(f"Database {db_type} non supportato")
        
        config = cls.SUPPORTED_DATABASES[db_type]
        
        if db_type == 'sqlite':
            # Per SQLite, usa il percorso nella cartella data/
            db_name = kwargs.get('db_name', 'budget_famiglia')
            db_path = FileManager.get_data_path(f"{db_name}.db")
            return config['url_template'].format(db_path=db_path)
        else:
            return config['url_template'].format(**kwargs)
    
    @classmethod
    def test_connection(cls, db_type: str, **params) -> Tuple[bool, str]:
        """Testa connessione database"""
        try:
            url = cls.get_database_url(db_type, **params)
            engine_config = cls.get_engine_config(url)
            
            engine = create_engine(url, **engine_config)
            
            with engine.connect() as conn:
                if db_type == 'sqlite':
                    conn.execute(text("SELECT 1"))
                elif db_type == 'postgresql':
                    conn.execute(text("SELECT version()"))
                elif db_type == 'mysql':
                    conn.execute(text("SELECT @@version"))
            
            engine.dispose()
            return True, "Connessione riuscita"
            
        except Exception as e:
            return False, str(e)
    
    @classmethod
    def get_engine_config(cls, database_url: str) -> Dict:
        """Configurazione engine ottimizzata per tipo database"""
        if database_url.startswith('sqlite'):
            return {
                'echo': False,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 30
                },
                'poolclass': StaticPool
            }
        
        elif 'postgresql' in database_url:
            return {
                'echo': False,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_pre_ping': True,
                'pool_recycle': 3600
            }
        
        elif 'mysql' in database_url:
            return {
                'echo': False,
                'pool_size': 10,
                'max_overflow': 20,
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'connect_args': {
                    'charset': 'utf8mb4'
                }
            }
        
        return {'echo': False}


class DatabaseManager:
    """Manager principale per operazioni database"""
    
    def __init__(self, db_type: str = 'sqlite', **db_params):
        self.db_type = db_type
        self.db_params = db_params
        
        # Ensure directories exist and migrate old files
        FileManager.ensure_directories()
        FileManager.migrate_existing_files()
        
        self.database_url = DatabaseConfig.get_database_url(db_type, **db_params)
        
        # Configurazione engine
        engine_config = DatabaseConfig.get_engine_config(self.database_url)
        self.engine = create_engine(self.database_url, **engine_config)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        print(f"🗄️ Database inizializzato: {db_type.upper()}")
    
    def get_session(self) -> Session:
        """Restituisce nuova sessione database"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Crea tutte le tabelle dal modello"""
        from models import Base
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Tabelle create/verificate")
            return True
        except Exception as e:
            print(f"❌ Errore creazione tabelle: {e}")
            return False
    
    def check_and_migrate_schema(self):
        """Verifica e migra lo schema del database se necessario"""
        try:
            with self.get_session() as session:
                from models import Budget, Goal
                
                session.query(Budget).first()
                session.query(Goal).first()
                
                print("✅ Schema database verificato")
                return True
                
        except Exception as e:
            print(f"⚠️ Schema database obsoleto: {e}")
            print("🔄 Ricreazione schema necessaria...")
            
            if self.db_type == 'sqlite':
                return self._recreate_sqlite_schema()
            else:
                print("❌ Migrazione automatica non supportata per questo database")
                return False
    
    def _recreate_sqlite_schema(self):
        """Ricrea lo schema SQLite (solo per SQLite)"""
        try:
            backup_data = None
            try:
                backup_data = self.export_all_data()
                print("📦 Backup dati creato")
            except:
                print("⚠️ Nessun dato da salvare")
            
            from models import Base
            Base.metadata.drop_all(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            
            if backup_data and (backup_data.get('transactions') or backup_data.get('categories')):
                self.import_data(backup_data)
                print("📥 Dati ripristinati")
            
            print("✅ Schema ricreato con successo")
            return True
            
        except Exception as e:
            print(f"❌ Errore ricreazione schema: {e}")
            return False
    
    def drop_all_tables(self):
        """Elimina tutte le tabelle (ATTENZIONE!)"""
        from models import Base
        try:
            Base.metadata.drop_all(bind=self.engine)
            print("🗑️ Tutte le tabelle eliminate")
            return True
        except Exception as e:
            print(f"❌ Errore eliminazione tabelle: {e}")
            return False
    
    def reset_database(self):
        """Reset completo database"""
        try:
            self.drop_all_tables()
            self.create_tables()
            print("🔄 Database resettato completamente")
            return True
        except Exception as e:
            print(f"❌ Errore reset database: {e}")
            return False
    
    def get_database_info(self) -> Dict:
        """Informazioni dettagliate sul database"""
        try:
            with self.get_session() as session:
                from models import Transaction, Category, Budget, Goal
                
                info = {
                    'type': self.db_type,
                    'url': self.database_url,
                    'config': DatabaseConfig.SUPPORTED_DATABASES[self.db_type],
                    'stats': {
                        'transactions': session.query(Transaction).count(),
                        'categories': session.query(Category).count(),
                        'budgets': session.query(Budget).count(),
                        'goals': session.query(Goal).count()
                    }
                }
                
                if self.db_type == 'sqlite':
                    # Extract database path from URL
                    db_path_str = self.database_url.replace('sqlite:///', '')
                    db_path = Path(db_path_str)
                    
                    if db_path.exists():
                        file_size = db_path.stat().st_size
                        info['file_size'] = f"{file_size / 1024:.1f} KB"
                        info['file_path'] = str(db_path.absolute())
                        info['file_location'] = str(db_path.parent)
                    
                elif self.db_type == 'postgresql':
                    try:
                        result = session.execute(text("SELECT version()")).scalar()
                        info['version'] = result.split()[1] if result else 'Unknown'
                        
                        db_name = self.db_params.get('db_name', 'budget_famiglia')
                        size_query = text(f"SELECT pg_size_pretty(pg_database_size('{db_name}'))")
                        info['database_size'] = session.execute(size_query).scalar()
                    except:
                        pass
                
                return info
                
        except Exception as e:
            print(f"❌ Errore info database: {e}")
            return {'type': self.db_type, 'error': str(e)}
    
    def backup_database(self, backup_name: Optional[str] = None) -> str:
        """Backup del database con organizzazione in cartelle"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not backup_name:
            backup_name = f"backup_{self.db_type}_{timestamp}"
        
        try:
            if self.db_type == 'sqlite':
                # Copy SQLite file to backups directory
                # Extract database path from URL
                db_path_str = self.database_url.replace('sqlite:///', '')
                db_path = Path(db_path_str)
                
                if db_path.exists():
                    backup_file = FileManager.get_backup_path(f"{backup_name}.db")
                    shutil.copy2(db_path, backup_file)
                    print(f"💾 Backup SQLite creato: {backup_file}")
                    return str(backup_file)
            
            else:
                # Export data to JSON for other databases
                data = self.export_all_data()
                backup_file = FileManager.get_backup_path(f"{backup_name}.json")
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                print(f"💾 Backup JSON creato: {backup_file}")
                return str(backup_file)
                
        except Exception as e:
            print(f"❌ Errore backup: {e}")
            return None
    
    def export_all_data(self, export_name: Optional[str] = None) -> Dict:
        """Esporta tutti i dati in formato JSON organizzato"""
        try:
            with self.get_session() as session:
                from models import Transaction, Category
                
                categories = session.query(Category).all()
                categories_data = [
                    {
                        'id': c.id,
                        'name': c.name,
                        'transaction_type': c.transaction_type,
                        'color': c.color,
                        'icon': c.icon,
                        'is_active': c.is_active,
                        'metadata_json': getattr(c, 'metadata_json', '{}')
                    }
                    for c in categories
                ]
                
                transactions = session.query(Transaction).all()
                transactions_data = [
                    {
                        'id': str(t.id),
                        'date': t.date.isoformat() if t.date else None,
                        'amount': float(t.amount) if t.amount else 0,
                        'description': t.description or '',
                        'notes': t.notes or '',
                        'category_id': t.category_id,
                        'transaction_type': t.transaction_type,
                        'recurrence_type': getattr(t, 'recurrence_type', 'Nessuna'),
                        'tags': getattr(t, 'tags', ''),
                        'metadata_json': getattr(t, 'metadata_json', '{}')
                    }
                    for t in transactions
                ]
                
                export_data = {
                    'export_info': {
                        'timestamp': datetime.now().isoformat(),
                        'database_type': self.db_type,
                        'version': '1.0',
                        'source': 'Budget Familiare App'
                    },
                    'categories': categories_data,
                    'transactions': transactions_data
                }
                
                # Save to exports directory if name provided
                if export_name:
                    export_file = FileManager.get_export_path(f"{export_name}.json")
                    with open(export_file, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
                    print(f"📤 Export salvato: {export_file}")
                
                return export_data
                
        except Exception as e:
            print(f"❌ Errore export: {e}")
            return {}
    
    def import_data(self, data: Dict) -> bool:
        """Importa dati da JSON con gestione conflitti"""
        try:
            with self.get_session() as session:
                from models import Transaction, Category
                
                # Import categories first with conflict resolution
                imported_categories = 0
                for cat_data in data.get('categories', []):
                    try:
                        # Check if category already exists
                        existing = session.query(Category).filter_by(
                            name=cat_data['name'],
                            transaction_type=cat_data['transaction_type']
                        ).first()
                        
                        if existing:
                            # Update existing category
                            existing.color = cat_data.get('color', existing.color)
                            existing.icon = cat_data.get('icon', existing.icon)
                            existing.is_active = cat_data.get('is_active', existing.is_active)
                            existing.metadata_json = cat_data.get('metadata_json', existing.metadata_json)
                            print(f"📝 Categoria esistente aggiornata: {cat_data['name']}")
                        else:
                            # Create new category
                            category = Category(
                                name=cat_data['name'],
                                transaction_type=cat_data['transaction_type'],
                                color=cat_data.get('color', '#3498db'),
                                icon=cat_data.get('icon', '💰'),
                                is_active=cat_data.get('is_active', True),
                                metadata_json=cat_data.get('metadata_json', '{}')
                            )
                            session.add(category)
                            imported_categories += 1
                            print(f"➕ Nuova categoria importata: {cat_data['name']}")
                            
                    except Exception as e:
                        print(f"⚠️ Errore importazione categoria {cat_data.get('name', 'Unknown')}: {e}")
                        continue
                
                session.commit()
                print(f"✅ Categorie processate: {imported_categories} nuove, {len(data.get('categories', [])) - imported_categories} aggiornate")
                
                # Create mapping of old category IDs to new ones
                category_mapping = {}
                for cat_data in data.get('categories', []):
                    db_category = session.query(Category).filter_by(
                        name=cat_data['name'],
                        transaction_type=cat_data['transaction_type']
                    ).first()
                    if db_category:
                        category_mapping[cat_data['id']] = db_category.id
                
                # Import transactions with category mapping
                imported_transactions = 0
                skipped_transactions = 0
                
                for trans_data in data.get('transactions', []):
                    try:
                        if not trans_data.get('date'):
                            skipped_transactions += 1
                            continue
                        
                        # Map old category ID to new category ID
                        old_category_id = trans_data['category_id']
                        new_category_id = category_mapping.get(old_category_id)
                        
                        if not new_category_id:
                            print(f"⚠️ Categoria non trovata per transazione {trans_data.get('description', 'Unknown')}")
                            skipped_transactions += 1
                            continue
                        
                        # Check if transaction already exists
                        existing = session.query(Transaction).filter_by(id=trans_data['id']).first()
                        
                        if existing:
                            # Update existing transaction
                            existing.date = datetime.fromisoformat(trans_data['date'])
                            existing.amount = trans_data['amount']
                            existing.description = trans_data['description']
                            existing.notes = trans_data.get('notes', '')
                            existing.category_id = new_category_id
                            existing.transaction_type = trans_data['transaction_type']
                            existing.recurrence_type = trans_data.get('recurrence_type', 'Nessuna')
                            existing.tags = trans_data.get('tags', '')
                            existing.metadata_json = trans_data.get('metadata_json', '{}')
                            print(f"📝 Transazione aggiornata: {trans_data['description']}")
                        else:
                            # Create new transaction
                            transaction = Transaction(
                                id=trans_data['id'],
                                date=datetime.fromisoformat(trans_data['date']),
                                amount=trans_data['amount'],
                                description=trans_data['description'],
                                notes=trans_data.get('notes', ''),
                                category_id=new_category_id,
                                transaction_type=trans_data['transaction_type'],
                                recurrence_type=trans_data.get('recurrence_type', 'Nessuna'),
                                tags=trans_data.get('tags', ''),
                                metadata_json=trans_data.get('metadata_json', '{}')
                            )
                            session.add(transaction)
                            imported_transactions += 1
                            
                    except Exception as e:
                        print(f"⚠️ Errore importazione transazione {trans_data.get('description', 'Unknown')}: {e}")
                        skipped_transactions += 1
                        continue
                
                session.commit()
                
                print(f"✅ Transazioni: {imported_transactions} importate, {skipped_transactions} saltate")
                print("✅ Importazione dati completata con successo")
                return True
                
        except Exception as e:
            print(f"❌ Errore generale import: {e}")
            return False


class DatabaseSwitcher:
    """Utility per cambiare database"""
    
    @staticmethod
    def switch_database(from_manager: DatabaseManager, to_config: Dict) -> DatabaseManager:
        """Switch database con migrazione dati intelligente"""
        try:
            print(f"📤 Esportazione dati da {from_manager.db_type}")
            data = from_manager.export_all_data()
            
            has_data = bool(data.get('transactions') or data.get('categories'))
            if not has_data:
                print("⚠️ Nessun dato da migrare")
            else:
                print(f"📊 Trovati {len(data.get('transactions', []))} transazioni e {len(data.get('categories', []))} categorie")
            
            print(f"🔄 Creazione nuovo database {to_config['type']}")
            new_manager = DatabaseManager(to_config['type'], **to_config['params'])
            
            if not new_manager.create_tables():
                raise Exception("Errore nella creazione delle tabelle")
            
            if not new_manager.check_and_migrate_schema():
                print("⚠️ Problemi con lo schema database")
            
            # Always ensure default categories exist first
            print("🏗️ Verifica categorie di default...")
            from categories import DefaultCategories
            DefaultCategories.ensure_default_categories(new_manager)
            
            # Then import user data if any
            if has_data:
                print("📥 Importazione dati utente nel nuovo database")
                if not new_manager.import_data(data):
                    print("⚠️ Alcuni dati potrebbero non essere stati importati correttamente")
                    # Don't raise exception, continue with partial import
            
            print(f"✅ Switch completato da {from_manager.db_type} a {to_config['type']}")
            return new_manager
            
        except Exception as e:
            print(f"❌ Errore durante lo switch: {e}")
            raise

    @staticmethod
    def create_new_database(db_type: str, **params) -> DatabaseManager:
        """Crea un nuovo database da zero"""
        try:
            print(f"🆕 Creazione nuovo database {db_type}")
            
            # Test connection first
            success, message = DatabaseConfig.test_connection(db_type, **params)
            if not success:
                raise Exception(f"Test connessione fallito: {message}")
            
            # Create manager
            new_manager = DatabaseManager(db_type, **params)
            
            # Create tables
            if not new_manager.create_tables():
                raise Exception("Errore nella creazione delle tabelle")
            
            # Verify schema
            if not new_manager.check_and_migrate_schema():
                print("⚠️ Problemi con lo schema database")
            
            # Initialize default categories
            print("🏗️ Inizializzazione categorie di default...")
            from categories import DefaultCategories
            DefaultCategories.ensure_default_categories(new_manager)
            
            print(f"✅ Database {db_type} creato con successo")
            return new_manager
            
        except Exception as e:
            print(f"❌ Errore creazione database: {e}")
            raise


# Singleton per il database manager corrente
_current_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Ottiene il database manager corrente"""
    global _current_db_manager
    
    if _current_db_manager is None:
        # Initialize file structure first
        FileManager.ensure_directories()
        moved_files = FileManager.migrate_existing_files()
        
        if moved_files:
            print(f"📁 File organizzati in cartelle: {', '.join(moved_files)}")
        
        # Try to load from registry
        current_config = DatabaseRegistry.get_current_database_config()
        
        if current_config:
            try:
                _current_db_manager = DatabaseManager(
                    current_config['type'], 
                    **current_config['params']
                )
                _current_db_manager.create_tables()
                
                if not _current_db_manager.check_and_migrate_schema():
                    print("⚠️ Problemi con lo schema database")
                
            except Exception as e:
                print(f"❌ Errore caricamento database configurato: {e}")
                _current_db_manager = None
        
        # Fallback to default SQLite if no config or error
        if _current_db_manager is None:
            _current_db_manager = DatabaseManager('sqlite', db_name='budget_famiglia')
            _current_db_manager.create_tables()
            
            # Save as default config
            DatabaseRegistry.add_database_config(
                'Default SQLite',
                'sqlite',
                db_name='budget_famiglia'
            )
            DatabaseRegistry.set_current_database('Default SQLite')
        
        # Initialize default categories
        from categories import DefaultCategories
        DefaultCategories.ensure_default_categories(_current_db_manager)
    
    return _current_db_manager

def set_database_manager(new_manager: DatabaseManager):
    """Imposta nuovo database manager"""
    global _current_db_manager
    _current_db_manager = new_manager

def check_first_run() -> bool:
    """Controlla se è il primo avvio dell'applicazione"""
    # Ensure directories and migrate files first
    FileManager.ensure_directories()
    FileManager.migrate_existing_files()
    
    configs = DatabaseRegistry.load_configs()
    return len(configs.get('databases', {})) == 0