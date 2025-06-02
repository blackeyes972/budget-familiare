# categories.py
"""
Modulo per la gestione delle categorie di default e personalizzate.
Contiene le definizioni delle categorie standard e utility per la gestione.
"""

import json
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session


class IconLibrary:
    """Libreria di icone organizzate per categorie"""
    
    # Icone per ENTRATE
    ENTRATE_ICONS = {
        'Lavoro': ['💼', '💻', '🏢', '👨‍💼', '👩‍💼', '⚙️', '🔧', '🏭'],
        'Investimenti': ['📈', '📊', '💹', '🏦', '💰', '💎', '🪙', '📉'],
        'Freelance': ['💻', '🎨', '📝', '🎭', '📸', '🎬', '🎵', '✍️'],
        'Bonus': ['🎁', '🏆', '⭐', '💫', '🌟', '🎉', '🎊', '💝'],
        'Altro': ['💰', '💵', '💴', '💶', '💷', '🤑', '💸', '🔄']
    }
    
    # Icone per USCITE
    USCITE_ICONS = {
        'Casa': ['🏠', '🏡', '🏘️', '🏰', '🏗️', '🏢', '🔑', '🚪'],
        'Alimentari': ['🛒', '🍎', '🥖', '🥛', '🍕', '🍔', '🥗', '🍇'],
        'Trasporti': ['🚗', '🚌', '🚇', '✈️', '🚲', '🛵', '⛽', '🚊'],
        'Sanità': ['🏥', '💊', '🩺', '🦷', '👩‍⚕️', '👨‍⚕️', '💉', '🔬'],
        'Svago': ['🎉', '🎬', '🎭', '🎪', '🎨', '🎮', '🎲', '🎸'],
        'Abbigliamento': ['👕', '👔', '👗', '👠', '👟', '👜', '💍', '👓'],
        'Tecnologia': ['📱', '💻', '🖥️', '⌚', '📷', '🎧', '🖨️', '📺'],
        'Educazione': ['📚', '✏️', '🎓', '📖', '📝', '🧑‍🎓', '👩‍🏫', '🏫'],
        'Regali': ['🎁', '💝', '🎀', '🌹', '💐', '🍰', '🎂', '💌'],
        'Utility': ['💡', '⚡', '💧', '🔥', '📡', '📞', '🌐', '📶'],
        'Altro': ['🔧', '❓', '📦', '💼', '🗂️', '📋', '⚙️', '🛠️']
    }
    
    # Icone generiche comuni
    COMMON_ICONS = ['💰', '💵', '📊', '⭐', '🔄', '💎', '🎯', '📈', '📉', '💡']
    
    @classmethod
    def get_icons_for_transaction_type(cls, transaction_type: str) -> Dict[str, List[str]]:
        """Restituisce le icone organizzate per tipo di transazione"""
        if transaction_type == 'Entrata':
            return cls.ENTRATE_ICONS
        elif transaction_type == 'Uscita':
            return cls.USCITE_ICONS
        else:
            # Return all icons for unknown type
            all_icons = {}
            all_icons.update(cls.ENTRATE_ICONS)
            all_icons.update(cls.USCITE_ICONS)
            return all_icons
    
    @classmethod
    def get_all_icons_flat(cls, transaction_type: str = None) -> List[str]:
        """Restituisce tutte le icone come lista piatta"""
        icons = set(cls.COMMON_ICONS)
        
        if transaction_type:
            icon_dict = cls.get_icons_for_transaction_type(transaction_type)
            for category_icons in icon_dict.values():
                icons.update(category_icons)
        else:
            # Add all icons
            for category_icons in cls.ENTRATE_ICONS.values():
                icons.update(category_icons)
            for category_icons in cls.USCITE_ICONS.values():
                icons.update(category_icons)
        
        return sorted(list(icons))
    
    @classmethod
    def get_suggested_icons(cls, category_name: str, transaction_type: str) -> List[str]:
        """Suggerisce icone basate sul nome della categoria"""
        category_lower = category_name.lower()
        suggestions = []
        
        # Keyword-based suggestions
        keyword_mapping = {
            'stipendio': ['💼', '💰', '🏢'],
            'lavoro': ['💼', '🏢', '👨‍💼'],
            'freelance': ['💻', '🎨', '📝'],
            'investimenti': ['📈', '📊', '💹'],
            'dividendi': ['📈', '💰', '🏦'],
            'bonus': ['🎁', '🏆', '⭐'],
            'regalo': ['🎁', '💝', '🎀'],
            'rimborso': ['🔄', '💰', '↩️'],
            
            'casa': ['🏠', '🏡', '🔑'],
            'affitto': ['🏠', '🏡', '🔑'],
            'alimentari': ['🛒', '🍎', '🥖'],
            'spesa': ['🛒', '🍎', '🥛'],
            'trasporti': ['🚗', '🚌', '⛽'],
            'auto': ['🚗', '⛽', '🚙'],
            'carburante': ['⛽', '🚗', '🛵'],
            'sanità': ['🏥', '💊', '🩺'],
            'medico': ['🏥', '👩‍⚕️', '🩺'],
            'dentista': ['🦷', '🏥', '👨‍⚕️'],
            'svago': ['🎉', '🎬', '🎭'],
            'cinema': ['🎬', '🍿', '🎭'],
            'ristorante': ['🍽️', '🍕', '🍔'],
            'abbigliamento': ['👕', '👔', '👗'],
            'vestiti': ['👕', '👗', '👠'],
            'tecnologia': ['📱', '💻', '🖥️'],
            'computer': ['💻', '🖥️', '⌨️'],
            'telefono': ['📱', '📞', '☎️'],
            'educazione': ['📚', '🎓', '✏️'],
            'corso': ['📚', '🎓', '📖'],
            'utility': ['💡', '⚡', '💧'],
            'bolletta': ['💡', '⚡', '📄'],
            'luce': ['💡', '⚡', '🔆'],
            'gas': ['🔥', '⛽', '🏠'],
            'acqua': ['💧', '🚿', '🏠'],
            'internet': ['🌐', '📡', '💻']
        }
        
        # Find matching keywords
        for keyword, icons in keyword_mapping.items():
            if keyword in category_lower:
                suggestions.extend(icons)
        
        # Remove duplicates and limit to 6 suggestions
        suggestions = list(dict.fromkeys(suggestions))[:6]
        
        # If no specific suggestions, use common icons for the transaction type
        if not suggestions:
            icon_dict = cls.get_icons_for_transaction_type(transaction_type)
            if icon_dict:
                # Take first 3 icons from first category
                first_category = list(icon_dict.values())[0]
                suggestions = first_category[:3]
            
            # Add some common icons
            suggestions.extend(cls.COMMON_ICONS[:3])
        
        return suggestions[:6]  # Limit to 6 suggestions
    
    @classmethod
    def search_icons(cls, search_term: str, transaction_type: str = None) -> List[str]:
        """Cerca icone per termine di ricerca"""
        if not search_term:
            return cls.get_all_icons_flat(transaction_type)[:20]
        
        # Simple emoji name mapping for search
        emoji_names = {
            '💰': ['money', 'soldi', 'denaro', 'euro'],
            '💼': ['work', 'lavoro', 'business', 'ufficio'],
            '🏠': ['house', 'casa', 'home', 'abitazione'],
            '🛒': ['shopping', 'spesa', 'carrello', 'supermercato'],
            '🚗': ['car', 'auto', 'macchina', 'automobile'],
            '🍕': ['food', 'cibo', 'pizza', 'mangiare'],
            '📱': ['phone', 'telefono', 'mobile', 'cellulare'],
            '💡': ['light', 'luce', 'idea', 'lampadina'],
            '🎉': ['party', 'festa', 'divertimento', 'svago'],
            '📚': ['book', 'libro', 'studio', 'educazione']
        }
        
        search_lower = search_term.lower()
        matching_icons = []
        
        for icon, names in emoji_names.items():
            if any(search_lower in name for name in names):
                matching_icons.append(icon)
        
        # If no matches, return all icons
        if not matching_icons:
            return cls.get_all_icons_flat(transaction_type)[:20]
        
        return matching_icons


class DefaultCategories:
    """Gestione categorie di default del sistema"""
    
    # Definizione categorie di default con metadata
    DEFAULT_CATEGORIES = [
        # === ENTRATE ===
        {
            'name': '💼 Stipendio',
            'type': 'Entrata',
            'color': '#2ecc71',
            'icon': '💼',
            'metadata': {
                'priority': 1,
                'recurring': True,
                'essential': True,
                'description': 'Stipendio fisso mensile'
            }
        },
        {
            'name': '💻 Freelance',
            'type': 'Entrata', 
            'color': '#27ae60',
            'icon': '💻',
            'metadata': {
                'priority': 2,
                'recurring': False,
                'variable': True,
                'description': 'Lavori freelance e consulenze'
            }
        },
        {
            'name': '📈 Investimenti',
            'type': 'Entrata',
            'color': '#16a085',
            'icon': '📈',
            'metadata': {
                'priority': 3,
                'volatile': True,
                'long_term': True,
                'description': 'Rendimenti da investimenti'
            }
        },
        {
            'name': '🎁 Bonus',
            'type': 'Entrata',
            'color': '#f39c12',
            'icon': '🎁',
            'metadata': {
                'priority': 4,
                'occasional': True,
                'description': 'Bonus, premi, regali in denaro'
            }
        },
        {
            'name': '↩️ Rimborsi',
            'type': 'Entrata',
            'color': '#e67e22',
            'icon': '↩️',
            'metadata': {
                'priority': 5,
                'occasional': True,
                'description': 'Rimborsi spese, restituzioni'
            }
        },
        {
            'name': '💰 Altro Entrate',
            'type': 'Entrata',
            'color': '#95a5a6',
            'icon': '💰',
            'metadata': {
                'priority': 9,
                'catch_all': True,
                'description': 'Altre entrate non categorizzate'
            }
        },
        
        # === USCITE ===
        {
            'name': '🏠 Casa',
            'type': 'Uscita',
            'color': '#e74c3c',
            'icon': '🏠',
            'metadata': {
                'priority': 1,
                'essential': True,
                'recurring': True,
                'description': 'Affitto, mutuo, spese condominiali'
            }
        },
        {
            'name': '🛒 Alimentari',
            'type': 'Uscita',
            'color': '#e67e22',
            'icon': '🛒',
            'metadata': {
                'priority': 1,
                'essential': True,
                'recurring': True,
                'description': 'Spesa alimentare, supermercato'
            }
        },
        {
            'name': '💡 Utility',
            'type': 'Uscita',
            'color': '#34495e',
            'icon': '💡',
            'metadata': {
                'priority': 1,
                'essential': True,
                'recurring': True,
                'description': 'Bollette luce, gas, acqua, internet'
            }
        },
        {
            'name': '🚗 Trasporti',
            'type': 'Uscita',
            'color': '#9b59b6',
            'icon': '🚗',
            'metadata': {
                'priority': 2,
                'recurring': True,
                'description': 'Carburante, mezzi pubblici, manutenzione auto'
            }
        },
        {
            'name': '🏥 Sanità',
            'type': 'Uscita',
            'color': '#1abc9c',
            'icon': '🏥',
            'metadata': {
                'priority': 1,
                'essential': True,
                'description': 'Visite mediche, farmaci, assicurazione sanitaria'
            }
        },
        {
            'name': '📚 Educazione',
            'type': 'Uscita',
            'color': '#ff9800',
            'icon': '📚',
            'metadata': {
                'priority': 2,
                'investment': True,
                'description': 'Corsi, libri, formazione'
            }
        },
        {
            'name': '🎉 Svago',
            'type': 'Uscita',
            'color': '#3498db',
            'icon': '🎉',
            'metadata': {
                'priority': 4,
                'discretionary': True,
                'description': 'Intrattenimento, cinema, ristoranti'
            }
        },
        {
            'name': '👕 Abbigliamento',
            'type': 'Uscita',
            'color': '#e91e63',
            'icon': '👕',
            'metadata': {
                'priority': 3,
                'seasonal': True,
                'description': 'Vestiti, scarpe, accessori'
            }
        },
        {
            'name': '📱 Tecnologia',
            'type': 'Uscita',
            'color': '#607d8b',
            'icon': '📱',
            'metadata': {
                'priority': 3,
                'occasional': True,
                'description': 'Dispositivi, software, abbonamenti tech'
            }
        },
        {
            'name': '🎁 Regali',
            'type': 'Uscita',
            'color': '#f06292',
            'icon': '🎁',
            'metadata': {
                'priority': 4,
                'seasonal': True,
                'social': True,
                'description': 'Regali per occasioni speciali'
            }
        },
        {
            'name': '💳 Tasse e Imposte',
            'type': 'Uscita',
            'color': '#795548',
            'icon': '💳',
            'metadata': {
                'priority': 1,
                'essential': True,
                'periodic': True,
                'description': 'Tasse, imposte, contributi'
            }
        },
        {
            'name': '🔧 Altro Uscite',
            'type': 'Uscita',
            'color': '#95a5a6',
            'icon': '🔧',
            'metadata': {
                'priority': 9,
                'catch_all': True,
                'description': 'Altre spese non categorizzate'
            }
        }
    ]
    
    @classmethod
    def get_categories_by_type(cls, transaction_type: str) -> List[Dict]:
        """Ottiene categorie filtrate per tipo"""
        return [cat for cat in cls.DEFAULT_CATEGORIES if cat['type'] == transaction_type]
    
    @classmethod
    def get_essential_categories(cls) -> List[Dict]:
        """Ottiene solo le categorie essenziali"""
        return [cat for cat in cls.DEFAULT_CATEGORIES 
                if cat['metadata'].get('essential', False)]
    
    @classmethod
    def ensure_default_categories(cls, db_manager):
        """Assicura che le categorie di default esistano nel database"""
        from models import Category
        
        try:
            with db_manager.get_session() as session:
                # Check if categories already exist
                existing_count = session.query(Category).count()
                
                if existing_count > 0:
                    print(f"✅ Categorie esistenti: {existing_count}")
                    return True
                
                # Create default categories
                print("🏗️ Creazione categorie di default...")
                
                for cat_data in cls.DEFAULT_CATEGORIES:
                    category = Category(
                        name=cat_data['name'],
                        transaction_type=cat_data['type'],
                        color=cat_data['color'],
                        icon=cat_data['icon'],
                        is_active=True,
                        metadata_json=json.dumps(cat_data['metadata'])
                    )
                    session.add(category)
                
                session.commit()
                print(f"✅ {len(cls.DEFAULT_CATEGORIES)} categorie di default create")
                return True
                
        except Exception as e:
            print(f"❌ Errore creazione categorie: {e}")
            return False
    
    @classmethod
    def get_category_suggestions(cls, description: str, transaction_type: str) -> List[str]:
        """Suggerisce categorie basate sulla descrizione"""
        description_lower = description.lower()
        suggestions = []
        
        # Keywords mapping for auto-categorization
        keywords_mapping = {
            'Entrata': {
                '💼 Stipendio': ['stipendio', 'salario', 'paga', 'lavoro'],
                '💻 Freelance': ['freelance', 'consulenza', 'progetto', 'contratto'],
                '📈 Investimenti': ['dividendo', 'interesse', 'rendimento', 'investimento'],
                '🎁 Bonus': ['bonus', 'premio', 'gratifica', 'extra'],
                '↩️ Rimborsi': ['rimborso', 'restituzione', 'refund']
            },
            'Uscita': {
                '🏠 Casa': ['affitto', 'mutuo', 'condominio', 'casa', 'immobiliare'],
                '🛒 Alimentari': ['supermercato', 'spesa', 'alimentari', 'cibo', 'esselunga', 'conad'],
                '💡 Utility': ['bolletta', 'luce', 'gas', 'acqua', 'internet', 'telefono'],
                '🚗 Trasporti': ['benzina', 'treno', 'bus', 'metro', 'taxi', 'carburante'],
                '🏥 Sanità': ['medico', 'farmacia', 'ospedale', 'salute', 'visita'],
                '🎉 Svago': ['cinema', 'ristorante', 'bar', 'teatro', 'concerto'],
                '👕 Abbigliamento': ['vestiti', 'scarpe', 'abbigliamento', 'negozio'],
                '📱 Tecnologia': ['amazon', 'mediaworld', 'tecnologia', 'computer', 'phone']
            }
        }
        
        if transaction_type in keywords_mapping:
            for category, keywords in keywords_mapping[transaction_type].items():
                if any(keyword in description_lower for keyword in keywords):
                    suggestions.append(category)
        
        return suggestions


class CategoryManager:
    """Manager per operazioni sulle categorie"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_categories(self, transaction_type: str = None, active_only: bool = True) -> List[Dict]:
        """Ottiene categorie dal database"""
        from models import Category
        
        try:
            with self.db_manager.get_session() as session:
                query = session.query(Category)
                
                if active_only:
                    query = query.filter(Category.is_active == True)
                
                if transaction_type:
                    query = query.filter(Category.transaction_type == transaction_type)
                
                categories = query.order_by(Category.name).all()
                
                return [
                    {
                        'id': cat.id,
                        'name': cat.name,
                        'transaction_type': cat.transaction_type,
                        'color': cat.color,
                        'icon': cat.icon,
                        'is_active': cat.is_active,
                        'metadata': json.loads(cat.metadata_json) if cat.metadata_json else {}
                    }
                    for cat in categories
                ]
                
        except Exception as e:
            print(f"❌ Errore recupero categorie: {e}")
            return []
    
    def add_category(self, name: str, transaction_type: str, color: str = '#3498db', 
                    icon: str = '💰', metadata: Dict = None) -> bool:
        """Aggiunge nuova categoria"""
        from models import Category
        
        try:
            with self.db_manager.get_session() as session:
                # Check if category already exists
                existing = session.query(Category).filter_by(
                    name=name, transaction_type=transaction_type
                ).first()
                
                if existing:
                    print(f"⚠️ Categoria '{name}' già esistente")
                    return False
                
                category = Category(
                    name=name,
                    transaction_type=transaction_type,
                    color=color,
                    icon=icon,
                    is_active=True,
                    metadata_json=json.dumps(metadata or {'user_created': True})
                )
                
                session.add(category)
                session.commit()
                print(f"✅ Categoria '{name}' aggiunta")
                return True
                
        except Exception as e:
            print(f"❌ Errore aggiunta categoria: {e}")
            return False
    
    def update_category(self, category_id: int, **updates) -> bool:
        """Aggiorna categoria esistente"""
        from models import Category
        
        try:
            with self.db_manager.get_session() as session:
                category = session.query(Category).filter_by(id=category_id).first()
                
                if not category:
                    print(f"❌ Categoria con ID {category_id} non trovata")
                    return False
                
                for key, value in updates.items():
                    if hasattr(category, key):
                        setattr(category, key, value)
                
                session.commit()
                print(f"✅ Categoria '{category.name}' aggiornata")
                return True
                
        except Exception as e:
            print(f"❌ Errore aggiornamento categoria: {e}")
            return False
    
    def delete_category(self, category_id: int, soft_delete: bool = True) -> bool:
        """Elimina categoria (soft delete di default)"""
        from models import Category, Transaction
        
        try:
            with self.db_manager.get_session() as session:
                category = session.query(Category).filter_by(id=category_id).first()
                
                if not category:
                    print(f"❌ Categoria con ID {category_id} non trovata")
                    return False
                
                # Check if category has transactions
                transaction_count = session.query(Transaction).filter_by(category_id=category_id).count()
                
                if transaction_count > 0 and not soft_delete:
                    print(f"❌ Impossibile eliminare categoria con {transaction_count} transazioni")
                    return False
                
                if soft_delete:
                    category.is_active = False
                    session.commit()
                    print(f"✅ Categoria '{category.name}' disattivata")
                else:
                    session.delete(category)
                    session.commit()
                    print(f"✅ Categoria '{category.name}' eliminata definitivamente")
                
                return True
                
        except Exception as e:
            print(f"❌ Errore eliminazione categoria: {e}")
            return False
    
    def get_category_stats(self) -> Dict:
        """Statistiche sulle categorie"""
        from models import Category, Transaction
        
        try:
            with self.db_manager.get_session() as session:
                stats = {
                    'total_categories': session.query(Category).count(),
                    'active_categories': session.query(Category).filter_by(is_active=True).count(),
                    'income_categories': session.query(Category).filter_by(transaction_type='Entrata', is_active=True).count(),
                    'expense_categories': session.query(Category).filter_by(transaction_type='Uscita', is_active=True).count(),
                    'unused_categories': []
                }
                
                # Find unused categories
                all_categories = session.query(Category).filter_by(is_active=True).all()
                for cat in all_categories:
                    transaction_count = session.query(Transaction).filter_by(category_id=cat.id).count()
                    if transaction_count == 0:
                        stats['unused_categories'].append({
                            'id': cat.id,
                            'name': cat.name,
                            'type': cat.transaction_type
                        })
                
                return stats
                
        except Exception as e:
            print(f"❌ Errore statistiche categorie: {e}")
            return {}
    
    def get_icon_suggestions(self, category_name: str, transaction_type: str) -> List[str]:
        """Ottiene suggerimenti di icone per una categoria"""
        return IconLibrary.get_suggested_icons(category_name, transaction_type)
    
    def get_available_icons(self, transaction_type: str) -> Dict[str, List[str]]:
        """Ottiene tutte le icone disponibili organizzate per tipo"""
        return IconLibrary.get_icons_for_transaction_type(transaction_type)
    
    def search_icons(self, search_term: str, transaction_type: str = None) -> List[str]:
        """Cerca icone per termine"""
        return IconLibrary.search_icons(search_term, transaction_type)