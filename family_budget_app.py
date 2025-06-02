import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import json
import os
import calendar

# Import moduli personalizzati
from database_config import (
    DatabaseConfig, DatabaseManager, DatabaseSwitcher, DatabaseRegistry, FileManager,
    get_database_manager, set_database_manager, check_first_run
)
from categories import DefaultCategories, CategoryManager, IconLibrary
from models import Transaction, Category, Budget, Goal

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def hide_streamlit_ui():
    """Nasconde elementi UI di Streamlit per look professionale"""
    hide_streamlit_style = """
    <style>
        /* Nasconde il menu Deploy e altri elementi Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        
        /* Mantiene l'app più pulita */
        .stActionButton {visibility: hidden;}
        
        /* Styling per icon selector */
        .icon-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(50px, 1fr));
            gap: 5px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .icon-button {
            background: none;
            border: 2px solid transparent;
            border-radius: 8px;
            padding: 8px;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
        }
        
        .icon-button:hover {
            border-color: #1f77b4;
            background-color: #f0f8ff;
        }
        
        .icon-button.selected {
            border-color: #1f77b4;
            background-color: #e6f2ff;
        }
        
        /* Styling per report cards */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .metric-card h3 {
            margin: 0;
            font-size: 24px;
        }
        
        .metric-card p {
            margin: 5px 0 0 0;
            opacity: 0.8;
        }
        
        .comparison-positive {
            color: #2ecc71;
            font-weight: bold;
        }
        
        .comparison-negative {
            color: #e74c3c;
            font-weight: bold;
        }
        
        .report-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            border-left: 4px solid #3498db;
        }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def render_icon_selector(transaction_type: str, category_name: str = "", key_suffix: str = "", use_expander: bool = True) -> str:
    """Render advanced icon selector with suggestions and search"""
    
    # Initialize session state for selected icon
    selected_icon_key = f"selected_icon_{key_suffix}"
    if selected_icon_key not in st.session_state:
        st.session_state[selected_icon_key] = "💰"
    
    st.markdown("### 🎨 Seleziona Icona")
    
    # Auto-suggestions based on category name
    if category_name:
        suggestions = IconLibrary.get_suggested_icons(category_name, transaction_type)
        if suggestions:
            st.markdown("**💡 Suggerimenti automatici:**")
            
            cols = st.columns(len(suggestions))
            for i, icon in enumerate(suggestions):
                with cols[i]:
                    if st.button(icon, key=f"suggest_{icon}_{key_suffix}", 
                               help=f"Usa {icon}",
                               use_container_width=True):
                        st.session_state[selected_icon_key] = icon
                        st.rerun()
    
    # Search functionality
    search_term = st.text_input(
        "🔍 Cerca icone (es: casa, cibo, auto)",
        key=f"icon_search_{key_suffix}",
        help="Scrivi una parola per cercare icone correlate"
    )
    
    # Get icons based on search or show all for transaction type
    if search_term:
        available_icons = IconLibrary.search_icons(search_term, transaction_type)
        st.caption(f"🔍 Risultati per '{search_term}': {len(available_icons)} icone")
        
        # Show flat grid for search results
        if available_icons:
            st.markdown("**🎯 Risultati ricerca:**")
            cols_per_row = 10
            icon_rows = [available_icons[i:i + cols_per_row] for i in range(0, len(available_icons), cols_per_row)]
            
            for row in icon_rows:
                cols = st.columns(cols_per_row)
                for j, icon in enumerate(row):
                    with cols[j]:
                        button_style = "🔹" if icon == st.session_state[selected_icon_key] else ""
                        if st.button(f"{icon}{button_style}", 
                                   key=f"search_{icon}_{key_suffix}",
                                   help=f"Seleziona {icon}",
                                   use_container_width=True):
                            st.session_state[selected_icon_key] = icon
                            st.rerun()
    else:
        icon_categories = IconLibrary.get_icons_for_transaction_type(transaction_type)
        
        # Show icons organized by category
        st.markdown("**📂 Icone per categoria:**")
        
        # Use expander only if allowed, otherwise use collapsible sections with checkboxes
        if use_expander:
            for category, icons in icon_categories.items():
                with st.expander(f"📂 {category} ({len(icons)} icone)", expanded=category in ["Lavoro", "Casa", "Alimentari"]):
                    # Create grid of icon buttons
                    cols_per_row = 8
                    icon_rows = [icons[i:i + cols_per_row] for i in range(0, len(icons), cols_per_row)]
                    
                    for row in icon_rows:
                        cols = st.columns(cols_per_row)
                        for j, icon in enumerate(row):
                            with cols[j]:
                                button_style = "🔹" if icon == st.session_state[selected_icon_key] else ""
                                if st.button(f"{icon}{button_style}", 
                                           key=f"icon_{icon}_{category}_{key_suffix}",
                                           help=f"Seleziona {icon}",
                                           use_container_width=True):
                                    st.session_state[selected_icon_key] = icon
                                    st.rerun()
        else:
            # Alternative layout without expanders - use collapsible sections with session state
            for category, icons in icon_categories.items():
                # Use session state to track which sections are expanded
                expanded_key = f"icon_category_expanded_{category}_{key_suffix}"
                if expanded_key not in st.session_state:
                    # Default expanded categories
                    st.session_state[expanded_key] = category in ["Lavoro", "Casa", "Alimentari"]
                
                # Category header with toggle
                col_header, col_toggle = st.columns([4, 1])
                with col_header:
                    st.markdown(f"**📂 {category} ({len(icons)} icone)**")
                with col_toggle:
                    if st.button("🔽" if st.session_state[expanded_key] else "▶️", 
                               key=f"toggle_{category}_{key_suffix}",
                               help="Espandi/Chiudi"):
                        st.session_state[expanded_key] = not st.session_state[expanded_key]
                        st.rerun()
                
                # Show icons if expanded
                if st.session_state[expanded_key]:
                    cols_per_row = 8
                    icon_rows = [icons[i:i + cols_per_row] for i in range(0, len(icons), cols_per_row)]
                    
                    for row in icon_rows:
                        cols = st.columns(cols_per_row)
                        for j, icon in enumerate(row):
                            with cols[j]:
                                button_style = "🔹" if icon == st.session_state[selected_icon_key] else ""
                                if st.button(f"{icon}{button_style}", 
                                           key=f"icon_{icon}_{category}_{key_suffix}",
                                           help=f"Seleziona {icon}",
                                           use_container_width=True):
                                    st.session_state[selected_icon_key] = icon
                                    st.rerun()
                
                st.divider()
        
        # Add common icons section
        common_icons = IconLibrary.COMMON_ICONS
        
        if use_expander:
            with st.expander("⭐ Icone Comuni", expanded=True):
                cols = st.columns(len(common_icons))
                for i, icon in enumerate(common_icons):
                    with cols[i]:
                        button_style = "🔹" if icon == st.session_state[selected_icon_key] else ""
                        if st.button(f"{icon}{button_style}", 
                                   key=f"common_{icon}_{key_suffix}",
                                   help=f"Seleziona {icon}",
                                   use_container_width=True):
                            st.session_state[selected_icon_key] = icon
                            st.rerun()
        else:
            st.markdown("**⭐ Icone Comuni:**")
            cols = st.columns(len(common_icons))
            for i, icon in enumerate(common_icons):
                with cols[i]:
                    button_style = "🔹" if icon == st.session_state[selected_icon_key] else ""
                    if st.button(f"{icon}{button_style}", 
                               key=f"common_{icon}_{key_suffix}",
                               help=f"Seleziona {icon}",
                               use_container_width=True):
                        st.session_state[selected_icon_key] = icon
                        st.rerun()
    
    # Show selected icon
    st.markdown("**✅ Icona selezionata:**")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"## {st.session_state[selected_icon_key]}")
    with col2:
        st.info(f"Hai selezionato: **{st.session_state[selected_icon_key]}**")
        if st.button("🔄 Reset a 💰", key=f"reset_icon_{key_suffix}"):
            st.session_state[selected_icon_key] = "💰"
            st.rerun()
    
    return st.session_state[selected_icon_key]

def format_currency(amount: float) -> str:
    """Formatta un importo in valuta EUR"""
    return f"€{amount:,.2f}"

def get_month_name(month: int) -> str:
    """Restituisce il nome del mese in italiano"""
    months = {
        1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile",
        5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto", 
        9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"
    }
    return months.get(month, "Sconosciuto")

# =============================================================================
# DATA ACCESS LAYER (DAL)
# =============================================================================

class TransactionDAL:
    """Data Access Layer per le transazioni"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def add_transaction(self, transaction_data: Dict) -> bool:
        """Aggiunge una nuova transazione"""
        try:
            with self.db_manager.get_session() as session:
                # Convert tags list to comma-separated string
                tags_str = ','.join(transaction_data.get('tags', []))
                
                transaction = Transaction(
                    date=transaction_data['date'],
                    amount=transaction_data['amount'],
                    description=transaction_data['description'],
                    notes=transaction_data.get('notes', ''),
                    category_id=transaction_data['category_id'],
                    transaction_type=transaction_data['transaction_type'],
                    recurrence_type=transaction_data.get('recurrence_type', 'Nessuna'),
                    tags=tags_str,
                    metadata_json=json.dumps(transaction_data.get('metadata', {}))
                )
                session.add(transaction)
                session.commit()
                return True
        except Exception as e:
            st.error(f"Errore nell'aggiunta transazione: {e}")
            return False
    
    def get_transactions(self, 
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        category_id: Optional[int] = None,
                        transaction_type: Optional[str] = None) -> pd.DataFrame:
        """Recupera transazioni con filtri"""
        
        try:
            with self.db_manager.get_session() as session:
                query = session.query(
                    Transaction.id,
                    Transaction.date,
                    Transaction.amount,
                    Transaction.description,
                    Transaction.notes,
                    Transaction.transaction_type,
                    Transaction.recurrence_type,
                    Transaction.tags,
                    Category.name.label('category_name'),
                    Category.color.label('category_color'),
                    Category.icon.label('category_icon')
                ).join(Category, Transaction.category_id == Category.id)
                
                # Apply filters
                if start_date:
                    query = query.filter(Transaction.date >= start_date)
                if end_date:
                    query = query.filter(Transaction.date <= end_date)
                if category_id:
                    query = query.filter(Transaction.category_id == category_id)
                if transaction_type:
                    query = query.filter(Transaction.transaction_type == transaction_type)
                
                query = query.order_by(Transaction.date.desc())
                
                df = pd.read_sql(query.statement, session.bind)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                
                return df
                
        except Exception as e:
            st.error(f"Errore nel recupero transazioni: {e}")
            return pd.DataFrame()
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """Riepilogo mensile"""
        try:
            with self.db_manager.get_session() as session:
                from sqlalchemy.sql import func
                
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                
                entrate = session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.date >= start_date)\
                    .filter(Transaction.date <= end_date)\
                    .filter(Transaction.transaction_type == 'Entrata')\
                    .scalar() or 0
                
                uscite = session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.date >= start_date)\
                    .filter(Transaction.date <= end_date)\
                    .filter(Transaction.transaction_type == 'Uscita')\
                    .scalar() or 0
                
                count = session.query(func.count(Transaction.id))\
                    .filter(Transaction.date >= start_date)\
                    .filter(Transaction.date <= end_date)\
                    .scalar() or 0
                
                return {
                    'entrate': float(entrate),
                    'uscite': float(uscite),
                    'saldo': float(entrate - uscite),
                    'transactions_count': count,
                    'start_date': start_date,
                    'end_date': end_date
                }
                
        except Exception as e:
            st.error(f"Errore nel calcolo riepilogo: {e}")
            return {'entrate': 0, 'uscite': 0, 'saldo': 0, 'transactions_count': 0}
    
    def get_period_summary(self, days: int = None, start_date: datetime = None, end_date: datetime = None) -> Dict:
        """Riepilogo per periodo specificato"""
        try:
            with self.db_manager.get_session() as session:
                from sqlalchemy.sql import func
                
                # Calculate date range
                if days is not None:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days)
                elif start_date is None or end_date is None:
                    # Get all transactions if no period specified
                    start_date = None
                    end_date = None
                
                # Build query
                query_entrate = session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.transaction_type == 'Entrata')
                
                query_uscite = session.query(func.sum(Transaction.amount))\
                    .filter(Transaction.transaction_type == 'Uscita')
                
                query_count = session.query(func.count(Transaction.id))
                
                if start_date:
                    query_entrate = query_entrate.filter(Transaction.date >= start_date)
                    query_uscite = query_uscite.filter(Transaction.date >= start_date)
                    query_count = query_count.filter(Transaction.date >= start_date)
                
                if end_date:
                    query_entrate = query_entrate.filter(Transaction.date <= end_date)
                    query_uscite = query_uscite.filter(Transaction.date <= end_date)
                    query_count = query_count.filter(Transaction.date <= end_date)
                
                entrate = query_entrate.scalar() or 0
                uscite = query_uscite.scalar() or 0
                count = query_count.scalar() or 0
                
                # Get first and last transaction dates for the period
                if start_date or end_date:
                    date_query = session.query(
                        func.min(Transaction.date).label('first_date'),
                        func.max(Transaction.date).label('last_date')
                    )
                    
                    if start_date:
                        date_query = date_query.filter(Transaction.date >= start_date)
                    if end_date:
                        date_query = date_query.filter(Transaction.date <= end_date)
                    
                    date_result = date_query.first()
                    first_date = date_result.first_date if date_result else None
                    last_date = date_result.last_date if date_result else None
                else:
                    # Get overall first and last dates
                    date_result = session.query(
                        func.min(Transaction.date).label('first_date'),
                        func.max(Transaction.date).label('last_date')
                    ).first()
                    first_date = date_result.first_date if date_result else None
                    last_date = date_result.last_date if date_result else None
                
                return {
                    'entrate': float(entrate),
                    'uscite': float(uscite),
                    'saldo': float(entrate - uscite),
                    'transactions_count': count,
                    'period_days': days,
                    'start_date': start_date,
                    'end_date': end_date,
                    'first_transaction_date': first_date,
                    'last_transaction_date': last_date
                }
                
        except Exception as e:
            st.error(f"Errore nel calcolo riepilogo periodo: {e}")
            return {'entrate': 0, 'uscite': 0, 'saldo': 0, 'transactions_count': 0, 'period_days': days}
    
    def get_recent_summary(self, days: int = 30) -> Dict:
        """Riepilogo degli ultimi N giorni"""
        return self.get_period_summary(days=days)
    
    def get_total_summary(self) -> Dict:
        """Riepilogo totale di tutte le transazioni"""
        return self.get_period_summary()
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Elimina una transazione"""
        try:
            with self.db_manager.get_session() as session:
                transaction = session.query(Transaction).filter_by(id=transaction_id).first()
                if transaction:
                    session.delete(transaction)
                    session.commit()
                    return True
                return False
        except Exception as e:
            st.error(f"Errore nell'eliminazione transazione: {e}")
            return False
    
    def get_category_monthly_summary(self, year: int, month: int) -> pd.DataFrame:
        """Riepilogo mensile per categoria"""
        try:
            with self.db_manager.get_session() as session:
                from sqlalchemy.sql import func
                
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                
                query = session.query(
                    Category.name.label('category_name'),
                    Category.icon.label('category_icon'),
                    Category.color.label('category_color'),
                    Transaction.transaction_type,
                    func.sum(Transaction.amount).label('total_amount'),
                    func.count(Transaction.id).label('transaction_count'),
                    func.avg(Transaction.amount).label('avg_amount')
                ).join(Category, Transaction.category_id == Category.id)\
                .filter(Transaction.date >= start_date)\
                .filter(Transaction.date <= end_date)\
                .group_by(Category.name, Category.icon, Category.color, Transaction.transaction_type)\
                .order_by(func.sum(Transaction.amount).desc())
                
                df = pd.read_sql(query.statement, session.bind)
                return df
                
        except Exception as e:
            st.error(f"Errore nel riepilogo categorie: {e}")
            return pd.DataFrame()
    
    def get_daily_summary(self, year: int, month: int) -> pd.DataFrame:
        """Riepilogo giornaliero per un mese"""
        try:
            with self.db_manager.get_session() as session:
                from sqlalchemy.sql import func
                
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                
                query = session.query(
                    func.date(Transaction.date).label('day'),
                    Transaction.transaction_type,
                    func.sum(Transaction.amount).label('daily_amount'),
                    func.count(Transaction.id).label('daily_count')
                ).filter(Transaction.date >= start_date)\
                .filter(Transaction.date <= end_date)\
                .group_by(func.date(Transaction.date), Transaction.transaction_type)\
                .order_by(func.date(Transaction.date))
                
                df = pd.read_sql(query.statement, session.bind)
                if not df.empty:
                    df['day'] = pd.to_datetime(df['day'])
                
                return df
                
        except Exception as e:
            st.error(f"Errore nel riepilogo giornaliero: {e}")
            return pd.DataFrame()

class ReportManager:
    """Gestore per i report mensili avanzati"""
    
    def __init__(self, transaction_dal: TransactionDAL, category_manager: CategoryManager):
        self.transaction_dal = transaction_dal
        self.category_manager = category_manager
    
    def get_comparison_data(self, current_year: int, current_month: int, compare_months: int = 3) -> Dict:
        """Ottiene dati di confronto con i mesi precedenti"""
        comparisons = []
        
        for i in range(compare_months):
            # Calcola mese e anno precedente
            target_month = current_month - i
            target_year = current_year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            summary = self.transaction_dal.get_monthly_summary(target_year, target_month)
            summary['month'] = target_month
            summary['year'] = target_year
            summary['month_name'] = get_month_name(target_month)
            summary['is_current'] = (target_month == current_month and target_year == current_year)
            
            comparisons.append(summary)
        
        return {
            'comparisons': comparisons,
            'current_data': comparisons[0] if comparisons else {},
            'previous_data': comparisons[1] if len(comparisons) > 1 else {}
        }
    
    def calculate_trends(self, year: int, month: int) -> Dict:
        """Calcola trend e variazioni"""
        current_data = self.transaction_dal.get_monthly_summary(year, month)
        
        # Mese precedente
        prev_month = month - 1
        prev_year = year
        if prev_month <= 0:
            prev_month = 12
            prev_year -= 1
        
        prev_data = self.transaction_dal.get_monthly_summary(prev_year, prev_month)
        
        trends = {}
        
        for key in ['entrate', 'uscite', 'saldo']:
            current_val = current_data.get(key, 0)
            prev_val = prev_data.get(key, 0)
            
            if prev_val != 0:
                change_percent = ((current_val - prev_val) / abs(prev_val)) * 100
                change_amount = current_val - prev_val
            else:
                change_percent = 100 if current_val > 0 else 0
                change_amount = current_val
            
            trends[key] = {
                'current': current_val,
                'previous': prev_val,
                'change_amount': change_amount,
                'change_percent': change_percent,
                'trend': 'up' if change_amount > 0 else 'down' if change_amount < 0 else 'stable'
            }
        
        return trends
    
    def get_top_expenses(self, year: int, month: int, limit: int = 10) -> pd.DataFrame:
        """Ottiene le top spese del mese"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        df = self.transaction_dal.get_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type='Uscita'
        )
        
        if df.empty:
            return pd.DataFrame()
        
        # Ordina per importo decrescente e prendi i top
        top_df = df.nlargest(limit, 'amount')[['date', 'description', 'amount', 'category_name', 'category_icon']]
        top_df['date'] = top_df['date'].dt.strftime('%d/%m/%Y')
        
        return top_df
    
    def get_spending_patterns(self, year: int, month: int) -> Dict:
        """Analizza i pattern di spesa"""
        df = self.transaction_dal.get_daily_summary(year, month)
        
        if df.empty:
            return {}
        
        # Analisi per giorno della settimana
        uscite_df = df[df['transaction_type'] == 'Uscita'].copy()
        
        if uscite_df.empty:
            return {}
        
        uscite_df['weekday'] = uscite_df['day'].dt.day_name()
        weekday_spending = uscite_df.groupby('weekday')['daily_amount'].sum().to_dict()
        
        # Analisi per settimana del mese
        uscite_df['week'] = uscite_df['day'].dt.isocalendar().week
        weekly_spending = uscite_df.groupby('week')['daily_amount'].sum().to_dict()
        
        # Media giornaliera
        avg_daily = uscite_df['daily_amount'].mean()
        
        return {
            'weekday_spending': weekday_spending,
            'weekly_spending': weekly_spending,
            'avg_daily_spending': avg_daily,
            'total_days_with_expenses': len(uscite_df),
            'highest_spending_day': uscite_df.loc[uscite_df['daily_amount'].idxmax()] if not uscite_df.empty else None
        }
    
    def generate_monthly_insights(self, year: int, month: int) -> List[str]:
        """Genera insights automatici per il mese"""
        insights = []
        
        # Dati base
        current_data = self.transaction_dal.get_monthly_summary(year, month)
        trends = self.calculate_trends(year, month)
        patterns = self.get_spending_patterns(year, month)
        
        # Insight 1: Saldo generale
        saldo = current_data.get('saldo', 0)
        if saldo > 0:
            insights.append(f"💚 Ottimo! Hai risparmiato {format_currency(saldo)} questo mese.")
        elif saldo < 0:
            insights.append(f"🔴 Attenzione: hai speso {format_currency(abs(saldo))} in più delle entrate.")
        else:
            insights.append("⚖️ Hai raggiunto il pareggio tra entrate e uscite.")
        
        # Insight 2: Trend rispetto al mese precedente
        saldo_trend = trends.get('saldo', {})
        if saldo_trend.get('change_amount', 0) > 0:
            insights.append(f"📈 Il tuo saldo è migliorato di {format_currency(saldo_trend['change_amount'])} rispetto al mese scorso.")
        elif saldo_trend.get('change_amount', 0) < 0:
            insights.append(f"📉 Il tuo saldo è diminuito di {format_currency(abs(saldo_trend['change_amount']))} rispetto al mese scorso.")
        
        # Insight 3: Efficienza di spesa
        entrate = current_data.get('entrate', 0)
        uscite = current_data.get('uscite', 0)
        if entrate > 0:
            efficiency = (1 - (uscite / entrate)) * 100
            if efficiency > 20:
                insights.append(f"🌟 Eccellente controllo delle spese! Hai risparmiato il {efficiency:.1f}% delle tue entrate.")
            elif efficiency > 0:
                insights.append(f"👍 Buon controllo delle spese, hai risparmiato il {efficiency:.1f}% delle entrate.")
            else:
                insights.append(f"⚠️ Hai speso più delle tue entrate. Considera di rivedere il budget.")
        
        # Insight 4: Pattern di spesa
        if patterns.get('avg_daily_spending'):
            avg_daily = patterns['avg_daily_spending']
            insights.append(f"📊 Spesa media giornaliera: {format_currency(avg_daily)}")
        
        # Insight 5: Numero di transazioni
        tx_count = current_data.get('transactions_count', 0)
        if tx_count > 0:
            avg_amount = (entrate + uscite) / tx_count if tx_count > 0 else 0
            insights.append(f"📝 Hai registrato {tx_count} transazioni con un importo medio di {format_currency(avg_amount)}")
        
        return insights

# =============================================================================
# UI COMPONENTS
# =============================================================================

class Dashboard:
    """Dashboard principale"""
    
    def __init__(self, transaction_dal: TransactionDAL):
        self.transaction_dal = transaction_dal
    
    def render_overview(self):
        """Panoramica principale"""
        st.header("📊 Dashboard Budget Familiare")
        
        # Verifica se ci sono transazioni nel database
        total_summary = self.transaction_dal.get_total_summary()
        
        if total_summary['transactions_count'] == 0:
            st.info("📝 Nessuna transazione trovata. Aggiungi alcune transazioni per vedere le statistiche!")
            return
        
        # Selettore del periodo
        col_period, col_info = st.columns([1, 2])
        
        with col_period:
            period_options = {
                "30 giorni": 30,
                "60 giorni": 60, 
                "90 giorni": 90,
                "6 mesi": 180,
                "1 anno": 365,
                "Mese corrente": "current_month",
                "Tutte le transazioni": "all"
            }
            
            # Determina il default intelligente
            current_month_summary = self.transaction_dal.get_monthly_summary(datetime.now().year, datetime.now().month)
            if current_month_summary['transactions_count'] > 0:
                default_period = "Mese corrente"
            else:
                recent_30_summary = self.transaction_dal.get_recent_summary(30)
                if recent_30_summary['transactions_count'] > 0:
                    default_period = "30 giorni"
                else:
                    default_period = "Tutte le transazioni"
            
            selected_period = st.selectbox(
                "📅 Periodo di analisi",
                list(period_options.keys()),
                index=list(period_options.keys()).index(default_period),
                help="Seleziona il periodo per il calcolo delle metriche"
            )
        
        # Calcola le statistiche in base al periodo selezionato
        period_value = period_options[selected_period]
        
        if period_value == "current_month":
            summary = self.transaction_dal.get_monthly_summary(datetime.now().year, datetime.now().month)
            period_label = f"Mese Corrente ({datetime.now().strftime('%B %Y')})"
        elif period_value == "all":
            summary = self.transaction_dal.get_total_summary()
            period_label = "Tutte le Transazioni"
        else:
            summary = self.transaction_dal.get_period_summary(days=period_value)
            period_label = selected_period
        
        with col_info:
            if summary['transactions_count'] > 0:
                # Mostra informazioni sul periodo
                if 'first_transaction_date' in summary and summary['first_transaction_date']:
                    if period_value == "all":
                        date_info = f"Dal {summary['first_transaction_date'].strftime('%d/%m/%Y')} al {summary['last_transaction_date'].strftime('%d/%m/%Y')}"
                    elif period_value == "current_month":
                        date_info = f"Mese di {datetime.now().strftime('%B %Y')}"
                    else:
                        start_date = datetime.now() - timedelta(days=period_value)
                        date_info = f"Dal {start_date.strftime('%d/%m/%Y')} a oggi"
                    
                    st.info(f"📊 **{period_label}** | {date_info}")
                else:
                    st.info(f"📊 **{period_label}**")
            else:
                st.warning(f"⚠️ Nessuna transazione trovata per: **{period_label}**")
                st.info("💡 Prova a selezionare 'Tutte le transazioni' o un periodo più ampio")
        
        # Mostra le metriche principali
        if summary['transactions_count'] > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 Entrate", 
                    f"€{summary['entrate']:,.2f}"
                )
            
            with col2:
                st.metric(
                    "💸 Uscite", 
                    f"€{summary['uscite']:,.2f}"
                )
            
            with col3:
                saldo = summary['saldo']
                st.metric(
                    "💵 Saldo", 
                    f"€{saldo:,.2f}",
                    delta=f"€{saldo:,.2f}" if saldo != 0 else None
                )
            
            with col4:
                st.metric(
                    "📝 Transazioni", 
                    summary['transactions_count']
                )
            
            # Metriche aggiuntive se ci sono dati
            if summary['entrate'] > 0 or summary['uscite'] > 0:
                st.divider()
                col_a, col_b, col_c, col_d = st.columns(4)
                
                with col_a:
                    if summary['transactions_count'] > 0:
                        avg_amount = (summary['entrate'] + summary['uscite']) / summary['transactions_count']
                        st.metric("📈 Importo Medio", f"€{avg_amount:.2f}")
                
                with col_b:
                    if summary['entrate'] > 0:
                        savings_rate = (summary['saldo'] / summary['entrate']) * 100
                        st.metric("💾 Tasso Risparmio", f"{savings_rate:.1f}%")
                
                with col_c:
                    # Giorni con transazioni (stima)
                    if period_value not in ["all", "current_month"] and summary['transactions_count'] > 0:
                        days_with_transactions = min(period_value, summary['transactions_count'])
                        avg_daily = summary['uscite'] / days_with_transactions if days_with_transactions > 0 else 0
                        st.metric("📊 Spesa Media/Giorno", f"€{avg_daily:.2f}")
                
                with col_d:
                    if summary['entrate'] > 0 and summary['uscite'] > 0:
                        expense_ratio = (summary['uscite'] / summary['entrate']) * 100
                        st.metric("⚖️ Rapporto Spese", f"{expense_ratio:.1f}%")
        
        else:
            # Mostra suggerimento se non ci sono transazioni nel periodo
            st.info(f"📝 Nessuna transazione trovata per il periodo: **{period_label}**")
            
            # Suggerisci periodo alternativo
            if period_value != "all":
                total_count = total_summary['transactions_count']
                st.info(f"💡 Hai {total_count} transazioni totali. Prova a selezionare 'Tutte le transazioni' o un periodo più ampio.")
    
    def render_charts(self):
        """Grafici principali"""
        st.subheader("📈 Analisi Grafiche")
        
        # Usa periodo più ampio per i grafici (6 mesi)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        df = self.transaction_dal.get_transactions(start_date=start_date, end_date=end_date)
        
        if df.empty:
            # Se non ci sono dati negli ultimi 6 mesi, prova con tutte le transazioni
            df = self.transaction_dal.get_transactions()
            if df.empty:
                st.info("📝 Aggiungi alcune transazioni per vedere i grafici")
                return
            else:
                st.info("📊 Mostrando tutti i dati disponibili (nessuna transazione negli ultimi 6 mesi)")
        
        # Monthly trend
        df['year_month'] = df['date'].dt.to_period('M')
        monthly_data = df.groupby(['year_month', 'transaction_type'])['amount'].sum().reset_index()
        monthly_data['year_month'] = monthly_data['year_month'].astype(str)
        
        # Determina il titolo del grafico in base ai dati
        months_span = len(monthly_data['year_month'].unique())
        if months_span <= 6:
            chart_title = f"Trend Entrate vs Uscite ({months_span} mes{'e' if months_span == 1 else 'i'})"
        else:
            chart_title = "Trend Entrate vs Uscite"
        
        fig_trend = px.line(
            monthly_data,
            x='year_month',
            y='amount',
            color='transaction_type',
            title=chart_title,
            color_discrete_map={'Entrata': '#2ecc71', 'Uscita': '#e74c3c'}
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Category analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥧 Uscite per Categoria")
            uscite_df = df[df['transaction_type'] == 'Uscita']
            if not uscite_df.empty:
                category_expenses = uscite_df.groupby(['category_name', 'category_color'])['amount'].sum().reset_index()
                
                fig_pie = px.pie(
                    category_expenses,
                    values='amount',
                    names='category_name',
                    title="Distribuzione Spese",
                    color='category_name',
                    color_discrete_map={row['category_name']: row['category_color'] 
                                      for _, row in category_expenses.iterrows()}
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("📝 Nessuna uscita trovata nel periodo analizzato")
        
        with col2:
            st.subheader("📊 Top 5 Categorie")
            if not uscite_df.empty:
                top_categories = uscite_df.groupby('category_name')['amount'].sum().nlargest(5)
                
                fig_bar = px.bar(
                    x=top_categories.values,
                    y=top_categories.index,
                    orientation='h',
                    title="Top 5 Spese",
                    labels={'x': 'Importo (€)', 'y': 'Categoria'},
                    color_discrete_sequence=['#3498db']
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("📝 Nessuna uscita trovata per creare la classifica")

class MonthlyReportManager:
    """Gestore completo per i report mensili avanzati"""
    
    def __init__(self, transaction_dal: TransactionDAL, category_manager: CategoryManager):
        self.transaction_dal = transaction_dal
        self.category_manager = category_manager
        self.report_manager = ReportManager(transaction_dal, category_manager)
    
    def render_monthly_reports(self):
        """Interfaccia principale per i report mensili"""
        st.header("📊 Report Mensili")
        
        # Initialize navigation state
        if 'report_navigate_to_year' not in st.session_state:
            st.session_state.report_navigate_to_year = None
        if 'report_navigate_to_month' not in st.session_state:
            st.session_state.report_navigate_to_month = None
        
        # Selettore mese/anno
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            # Default al mese corrente o al mese navigato
            current_year = datetime.now().year
            default_year = st.session_state.report_navigate_to_year or current_year
            
            # Calculate index for default year
            year_range = list(range(current_year - 5, current_year + 2))
            try:
                year_index = year_range.index(default_year)
            except ValueError:
                year_index = 5  # Default to current year
            
            selected_year = st.selectbox(
                "📅 Anno",
                year_range,
                index=year_index,
                key="report_year"
            )
        
        with col2:
            current_month = datetime.now().month
            default_month = st.session_state.report_navigate_to_month or current_month
            
            selected_month = st.selectbox(
                "📅 Mese",
                range(1, 13),
                format_func=lambda x: get_month_name(x),
                index=default_month - 1,
                key="report_month"
            )
        
        # Clear navigation state after using it
        if st.session_state.report_navigate_to_year is not None:
            st.session_state.report_navigate_to_year = None
            st.session_state.report_navigate_to_month = None
        
        with col3:
            # Info periodo selezionato
            month_name = get_month_name(selected_month)
            is_current = (selected_year == current_year and selected_month == current_month)
            is_future = (selected_year > current_year or 
                        (selected_year == current_year and selected_month > current_month))
            
            if is_current:
                st.info(f"📊 **{month_name} {selected_year}** (Mese Corrente)")
            elif is_future:
                st.warning(f"⏭️ **{month_name} {selected_year}** (Futuro)")
            else:
                st.success(f"📈 **{month_name} {selected_year}**")
        
        # Se è un mese futuro, mostra messaggio
        if is_future:
            st.warning("⚠️ Non ci sono dati per un mese futuro")
            return
        
        # Ottieni dati del mese
        monthly_data = self.transaction_dal.get_monthly_summary(selected_year, selected_month)
        
        if monthly_data['transactions_count'] == 0:
            st.info(f"📝 Nessuna transazione trovata per {month_name} {selected_year}")
            self._render_empty_month_suggestions(selected_year, selected_month)
            return
        
        # Layout principale del report
        self._render_executive_summary(selected_year, selected_month, monthly_data)
        
        # Tabs per diverse sezioni del report
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Panoramica", 
            "📈 Trend & Confronti", 
            "🏷️ Analisi Categorie",
            "💡 Insights",
            "📤 Export"
        ])
        
        with tab1:
            self._render_overview_tab(selected_year, selected_month, monthly_data)
        
        with tab2:
            self._render_trends_tab(selected_year, selected_month)
        
        with tab3:
            self._render_categories_tab(selected_year, selected_month)
        
        with tab4:
            self._render_insights_tab(selected_year, selected_month)
        
        with tab5:
            self._render_export_tab(selected_year, selected_month, monthly_data)
    
    def _render_executive_summary(self, year: int, month: int, data: Dict):
        """Riepilogo esecutivo con metriche chiave"""
        st.markdown("### 📋 Riepilogo Esecutivo")
        
        # Calcola trend
        trends = self.report_manager.calculate_trends(year, month)
        
        # Card metriche principali
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            entrate_trend = trends.get('entrate', {})
            delta_entrate = entrate_trend.get('change_amount', 0)
            st.metric(
                "💰 Entrate Totali",
                format_currency(data['entrate']),
                delta=format_currency(delta_entrate) if delta_entrate != 0 else None
            )
        
        with col2:
            uscite_trend = trends.get('uscite', {})
            delta_uscite = uscite_trend.get('change_amount', 0)
            st.metric(
                "💸 Uscite Totali",
                format_currency(data['uscite']),
                delta=format_currency(delta_uscite) if delta_uscite != 0 else None,
                delta_color="inverse"  # Rosso per aumento uscite
            )
        
        with col3:
            saldo_trend = trends.get('saldo', {})
            delta_saldo = saldo_trend.get('change_amount', 0)
            st.metric(
                "💵 Saldo Netto",
                format_currency(data['saldo']),
                delta=format_currency(delta_saldo) if delta_saldo != 0 else None
            )
        
        with col4:
            if data['entrate'] > 0:
                savings_rate = (data['saldo'] / data['entrate']) * 100
                prev_rate = 0
                if 'entrate' in trends and trends['entrate']['previous'] > 0:
                    prev_saldo = trends['saldo']['previous']
                    prev_entrate = trends['entrate']['previous']
                    prev_rate = (prev_saldo / prev_entrate) * 100
                
                delta_rate = savings_rate - prev_rate
                st.metric(
                    "💾 Tasso Risparmio",
                    f"{savings_rate:.1f}%",
                    delta=f"{delta_rate:+.1f}%" if prev_rate != 0 else None
                )
            else:
                st.metric("💾 Tasso Risparmio", "N/A")
        
        # Status bar colorato
        if data['saldo'] > 0:
            st.success(f"✅ Mese positivo con {format_currency(data['saldo'])} di surplus")
        elif data['saldo'] < 0:
            st.error(f"⚠️ Mese in deficit di {format_currency(abs(data['saldo']))}")
        else:
            st.info("⚖️ Pareggio perfetto tra entrate e uscite")
    
    def _render_overview_tab(self, year: int, month: int, data: Dict):
        """Tab panoramica con grafici principali"""
        st.subheader("📊 Panoramica Mensile")
        
        # Grafici affiancati
        col1, col2 = st.columns(2)
        
        with col1:
            # Grafico a torta entrate vs uscite
            if data['entrate'] > 0 or data['uscite'] > 0:
                fig_balance = go.Figure(data=[go.Pie(
                    labels=['Entrate', 'Uscite'],
                    values=[data['entrate'], data['uscite']],
                    marker_colors=['#2ecc71', '#e74c3c'],
                    hole=0.4
                )])
                fig_balance.update_layout(
                    title="💰 Bilancio Mensile",
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig_balance, use_container_width=True)
        
        with col2:
            # Grafico giornaliero
            daily_df = self.transaction_dal.get_daily_summary(year, month)
            if not daily_df.empty:
                # Pivot per avere entrate e uscite separate
                daily_pivot = daily_df.pivot_table(
                    index='day', 
                    columns='transaction_type', 
                    values='daily_amount', 
                    fill_value=0
                ).reset_index()
                
                fig_daily = go.Figure()
                
                if 'Entrata' in daily_pivot.columns:
                    fig_daily.add_trace(go.Scatter(
                        x=daily_pivot['day'],
                        y=daily_pivot['Entrata'],
                        mode='lines+markers',
                        name='Entrate',
                        line=dict(color='#2ecc71', width=3),
                        marker=dict(size=6)
                    ))
                
                if 'Uscita' in daily_pivot.columns:
                    fig_daily.add_trace(go.Scatter(
                        x=daily_pivot['day'],
                        y=daily_pivot['Uscita'],
                        mode='lines+markers',
                        name='Uscite',
                        line=dict(color='#e74c3c', width=3),
                        marker=dict(size=6)
                    ))
                
                fig_daily.update_layout(
                    title="📈 Trend Giornaliero",
                    xaxis_title="Giorno",
                    yaxis_title="Importo (€)",
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig_daily, use_container_width=True)
        
        # Statistiche aggiuntive
        st.divider()
        st.subheader("📊 Statistiche Dettagliate")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Totale Transazioni", data['transactions_count'])
        
        with col2:
            if data['transactions_count'] > 0:
                avg_transaction = (data['entrate'] + data['uscite']) / data['transactions_count']
                st.metric("📈 Importo Medio", format_currency(avg_transaction))
        
        with col3:
            # Giorni con transazioni
            days_in_month = calendar.monthrange(year, month)[1]
            daily_df = self.transaction_dal.get_daily_summary(year, month)
            active_days = len(daily_df['day'].unique()) if not daily_df.empty else 0
            st.metric("📅 Giorni Attivi", f"{active_days}/{days_in_month}")
        
        with col4:
            if data['uscite'] > 0:
                avg_daily_spend = data['uscite'] / days_in_month
                st.metric("💸 Spesa Media/Giorno", format_currency(avg_daily_spend))
    
    def _render_trends_tab(self, year: int, month: int):
        """Tab per trend e confronti"""
        st.subheader("📈 Trend e Confronti")
        
        # Confronto con mesi precedenti
        comparison_data = self.report_manager.get_comparison_data(year, month, 6)
        comparisons = comparison_data['comparisons']
        
        if len(comparisons) > 1:
            # Grafico trend ultimi 6 mesi
            df_trend = pd.DataFrame(comparisons)
            df_trend['month_year'] = df_trend.apply(lambda x: f"{get_month_name(x['month'])} {x['year']}", axis=1)
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend['month_year'],
                y=df_trend['entrate'],
                mode='lines+markers',
                name='Entrate',
                line=dict(color='#2ecc71', width=3),
                marker=dict(size=8)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend['month_year'],
                y=df_trend['uscite'],
                mode='lines+markers',
                name='Uscite',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend['month_year'],
                y=df_trend['saldo'],
                mode='lines+markers',
                name='Saldo',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            ))
            
            fig_trend.update_layout(
                title="📊 Trend Ultimi 6 Mesi",
                xaxis_title="Mese",
                yaxis_title="Importo (€)",
                hovermode='x unified',
                height=500
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Tabella confronti
            st.subheader("📋 Confronto Dettagliato")
            df_display = df_trend[['month_year', 'entrate', 'uscite', 'saldo', 'transactions_count']].copy()
            df_display.columns = ['Mese', 'Entrate', 'Uscite', 'Saldo', 'Transazioni']
            df_display['Entrate'] = df_display['Entrate'].apply(format_currency)
            df_display['Uscite'] = df_display['Uscite'].apply(format_currency)
            df_display['Saldo'] = df_display['Saldo'].apply(format_currency)
            
            st.dataframe(df_display, hide_index=True, use_container_width=True)
        
        else:
            st.info("📊 Servono almeno 2 mesi di dati per mostrare i trend")
    
    def _render_categories_tab(self, year: int, month: int):
        """Tab analisi per categoria"""
        st.subheader("🏷️ Analisi per Categoria")
        
        # Dati categorie
        category_df = self.transaction_dal.get_category_monthly_summary(year, month)
        
        if category_df.empty:
            st.info("📊 Nessun dato categoria per questo mese")
            return
        
        # Grafici per tipo di transazione
        col1, col2 = st.columns(2)
        
        with col1:
            # Uscite per categoria
            uscite_df = category_df[category_df['transaction_type'] == 'Uscita']
            if not uscite_df.empty:
                fig_uscite = px.pie(
                    uscite_df,
                    values='total_amount',
                    names='category_name',
                    title="💸 Distribuzione Uscite",
                    color='category_name',
                    color_discrete_map={row['category_name']: row['category_color'] 
                                      for _, row in uscite_df.iterrows()},
                    height=500
                )
                st.plotly_chart(fig_uscite, use_container_width=True)
        
        with col2:
            # Entrate per categoria
            entrate_df = category_df[category_df['transaction_type'] == 'Entrata']
            if not entrate_df.empty:
                fig_entrate = px.pie(
                    entrate_df,
                    values='total_amount',
                    names='category_name',
                    title="💰 Distribuzione Entrate",
                    color='category_name',
                    color_discrete_map={row['category_name']: row['category_color'] 
                                      for _, row in entrate_df.iterrows()},
                    height=500
                )
                st.plotly_chart(fig_entrate, use_container_width=True)
        
        # Top spese del mese
        st.subheader("🔝 Top Spese del Mese")
        top_expenses = self.report_manager.get_top_expenses(year, month, 10)
        
        if not top_expenses.empty:
            # Aggiungi numero progressivo
            top_expenses_display = top_expenses.copy()
            top_expenses_display.index = range(1, len(top_expenses_display) + 1)
            top_expenses_display['amount'] = top_expenses_display['amount'].apply(format_currency)
            top_expenses_display.columns = ['Data', 'Descrizione', 'Importo', 'Categoria', 'Icona']
            
            st.dataframe(top_expenses_display, use_container_width=True)
        else:
            st.info("📝 Nessuna spesa registrata per questo mese")
        
        # Grafico a barre categorie
        st.subheader("📊 Confronto Categorie")
        
        if not category_df.empty:
            # Ordina per importo totale
            category_sorted = category_df.sort_values('total_amount', ascending=True)
            
            fig_bar = px.bar(
                category_sorted,
                x='total_amount',
                y='category_name',
                color='transaction_type',
                orientation='h',
                title="Importi per Categoria",
                color_discrete_map={'Entrata': '#2ecc71', 'Uscita': '#e74c3c'},
                height=max(400, len(category_sorted) * 25)
            )
            fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
    
    def _render_insights_tab(self, year: int, month: int):
        """Tab insights e suggerimenti"""
        st.subheader("💡 Insights e Suggerimenti")
        
        # Genera insights automatici
        insights = self.report_manager.generate_monthly_insights(year, month)
        
        # Mostra insights in card colorate
        for i, insight in enumerate(insights):
            if insight.startswith("💚") or insight.startswith("🌟") or insight.startswith("📈"):
                st.success(insight)
            elif insight.startswith("🔴") or insight.startswith("⚠️") or insight.startswith("📉"):
                st.error(insight)
            elif insight.startswith("👍") or insight.startswith("📊"):
                st.info(insight)
            else:
                st.markdown(f"ℹ️ {insight}")
        
        # Pattern di spesa
        st.divider()
        st.subheader("🔍 Pattern di Spesa")
        
        patterns = self.report_manager.get_spending_patterns(year, month)
        
        if patterns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Spesa per giorno della settimana
                weekday_data = patterns.get('weekday_spending', {})
                if weekday_data:
                    # Ordina i giorni della settimana
                    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekday_names = {
                        'Monday': 'Lunedì', 'Tuesday': 'Martedì', 'Wednesday': 'Mercoledì',
                        'Thursday': 'Giovedì', 'Friday': 'Venerdì', 'Saturday': 'Sabato', 'Sunday': 'Domenica'
                    }
                    
                    ordered_data = [(weekday_names[day], weekday_data.get(day, 0)) for day in weekday_order if day in weekday_data]
                    
                    if ordered_data:
                        days, amounts = zip(*ordered_data)
                        
                        fig_weekday = px.bar(
                            x=days,
                            y=amounts,
                            title="💳 Spese per Giorno Settimana",
                            color_discrete_sequence=['#3498db']
                        )
                        fig_weekday.update_layout(xaxis_title="Giorno", yaxis_title="Importo (€)")
                        st.plotly_chart(fig_weekday, use_container_width=True)
            
            with col2:
                # Statistiche pattern
                st.markdown("**📊 Statistiche Pattern**")
                
                avg_daily = patterns.get('avg_daily_spending', 0)
                if avg_daily > 0:
                    st.metric("💸 Spesa Media Giornaliera", format_currency(avg_daily))
                
                active_days = patterns.get('total_days_with_expenses', 0)
                if active_days > 0:
                    st.metric("📅 Giorni con Spese", active_days)
                
                # Giorno con spesa massima
                highest_day = patterns.get('highest_spending_day')
                if highest_day is not None:
                    max_day = highest_day['day'].strftime('%d/%m/%Y')
                    max_amount = highest_day['daily_amount']
                    st.metric("📈 Giorno Spesa Massima", max_day)
                    st.metric("💰 Importo Massimo", format_currency(max_amount))
        
        # Raccomandazioni personalizzate
        st.divider()
        st.subheader("💭 Raccomandazioni")
        
        monthly_data = self.transaction_dal.get_monthly_summary(year, month)
        self._generate_recommendations(monthly_data, patterns)
    
    def _generate_recommendations(self, monthly_data: Dict, patterns: Dict):
        """Genera raccomandazioni personalizzate"""
        recommendations = []
        
        # Analisi saldo
        saldo = monthly_data.get('saldo', 0)
        entrate = monthly_data.get('entrate', 0)
        uscite = monthly_data.get('uscite', 0)
        
        if saldo < 0:
            recommendations.append({
                'type': 'warning',
                'title': '⚠️ Saldo Negativo',
                'text': 'Hai speso più delle tue entrate. Considera di rivedere le spese non essenziali o aumentare le entrate.'
            })
        
        if entrate > 0:
            savings_rate = (saldo / entrate) * 100
            if savings_rate < 10:
                recommendations.append({
                    'type': 'info',
                    'title': '💾 Basso Tasso di Risparmio',
                    'text': f'Il tuo tasso di risparmio è del {savings_rate:.1f}%. Prova a puntare almeno al 20% per una maggiore sicurezza finanziaria.'
                })
            elif savings_rate > 30:
                recommendations.append({
                    'type': 'success',
                    'title': '🌟 Ottimo Risparmio!',
                    'text': f'Complimenti! Il tuo tasso di risparmio del {savings_rate:.1f}% è eccellente. Continua così!'
                })
        
        # Analisi pattern di spesa
        if patterns:
            avg_daily = patterns.get('avg_daily_spending', 0)
            if avg_daily > 0:
                monthly_projection = avg_daily * 30
                if monthly_projection > uscite * 1.2:  # 20% sopra la spesa effettiva
                    recommendations.append({
                        'type': 'info',
                        'title': '📊 Pattern di Spesa',
                        'text': f'La tua spesa media giornaliera suggerisce un budget mensile di {format_currency(monthly_projection)}. Monitora questo trend.'
                    })
        
        # Analisi numero transazioni
        tx_count = monthly_data.get('transactions_count', 0)
        if tx_count > 0:
            avg_tx = (entrate + uscite) / tx_count
            if avg_tx < 10:
                recommendations.append({
                    'type': 'info',
                    'title': '📝 Molte Micro-Transazioni',
                    'text': f'Hai molte transazioni piccole (media: {format_currency(avg_tx)}). Considera di raggruppare spese simili per una migliore gestione.'
                })
            elif avg_tx > 200:
                recommendations.append({
                    'type': 'info',
                    'title': '💰 Transazioni di Alto Valore',
                    'text': f'Le tue transazioni hanno un valore medio alto ({format_currency(avg_tx)}). Assicurati di pianificare bene le spese importanti.'
                })
        
        # Mostra raccomandazioni
        if recommendations:
            for rec in recommendations:
                if rec['type'] == 'success':
                    st.success(f"**{rec['title']}**\n\n{rec['text']}")
                elif rec['type'] == 'warning':
                    st.error(f"**{rec['title']}**\n\n{rec['text']}")
                else:
                    st.info(f"**{rec['title']}**\n\n{rec['text']}")
        else:
            st.info("👍 Il tuo comportamento finanziario sembra equilibrato per questo mese!")
    
    def _render_export_tab(self, year: int, month: int, data: Dict):
        """Tab per export report"""
        st.subheader("📤 Export Report")
        
        month_name = get_month_name(month)
        
        # Informazioni export
        st.info(f"📋 Esporta il report completo di **{month_name} {year}**")
        
        # Opzioni di export
        export_options = st.multiselect(
            "Sezioni da includere:",
            [
                "📊 Riepilogo Esecutivo",
                "📈 Dati e Trend",
                "🏷️ Analisi Categorie",
                "💡 Insights e Raccomandazioni",
                "📋 Lista Transazioni"
            ],
            default=[
                "📊 Riepilogo Esecutivo",
                "📈 Dati e Trend",
                "🏷️ Analisi Categorie"
            ]
        )
        
        # Formato export
        col1, col2 = st.columns(2)
        
        with col1:
            # Export JSON
            if st.button("📄 Export JSON", use_container_width=True):
                report_data = self._generate_report_data(year, month, export_options)
                
                json_data = json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
                filename = f"report_{month_name.lower()}_{year}.json"
                
                st.download_button(
                    label="💾 Download Report JSON",
                    data=json_data,
                    file_name=filename,
                    mime="application/json"
                )
        
        with col2:
            # Export CSV (solo transazioni)
            if st.button("📊 Export CSV Transazioni", use_container_width=True):
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                
                df = self.transaction_dal.get_transactions(start_date=start_date, end_date=end_date)
                
                if not df.empty:
                    csv_data = df.to_csv(index=False)
                    filename = f"transazioni_{month_name.lower()}_{year}.csv"
                    
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv"
                    )
                else:
                    st.error("❌ Nessuna transazione da esportare")
        
        # Preview del report
        st.divider()
        st.subheader("👀 Anteprima Report")
        
        if export_options:
            with st.expander("📋 Anteprima Contenuto", expanded=False):
                preview_data = self._generate_report_data(year, month, export_options)
                st.json(preview_data)
    
    def _generate_report_data(self, year: int, month: int, sections: List[str]) -> Dict:
        """Genera i dati del report completo"""
        month_name = get_month_name(month)
        report_data = {
            'report_info': {
                'title': f"Report Mensile {month_name} {year}",
                'generated_at': datetime.now().isoformat(),
                'period': {
                    'year': year,
                    'month': month,
                    'month_name': month_name
                },
                'sections_included': sections
            }
        }
        
        # Dati base sempre inclusi
        monthly_data = self.transaction_dal.get_monthly_summary(year, month)
        report_data['summary'] = monthly_data
        
        # Sezioni condizionali
        if "📊 Riepilogo Esecutivo" in sections:
            trends = self.report_manager.calculate_trends(year, month)
            report_data['executive_summary'] = {
                'monthly_data': monthly_data,
                'trends': trends
            }
        
        if "📈 Dati e Trend" in sections:
            comparison_data = self.report_manager.get_comparison_data(year, month, 6)
            daily_data = self.transaction_dal.get_daily_summary(year, month)
            
            report_data['trends_data'] = {
                'comparisons': comparison_data['comparisons'],
                'daily_summary': daily_data.to_dict('records') if not daily_data.empty else []
            }
        
        if "🏷️ Analisi Categorie" in sections:
            category_data = self.transaction_dal.get_category_monthly_summary(year, month)
            top_expenses = self.report_manager.get_top_expenses(year, month, 10)
            
            report_data['categories_analysis'] = {
                'category_summary': category_data.to_dict('records') if not category_data.empty else [],
                'top_expenses': top_expenses.to_dict('records') if not top_expenses.empty else []
            }
        
        if "💡 Insights e Raccomandazioni" in sections:
            insights = self.report_manager.generate_monthly_insights(year, month)
            patterns = self.report_manager.get_spending_patterns(year, month)
            
            report_data['insights'] = {
                'automatic_insights': insights,
                'spending_patterns': patterns
            }
        
        if "📋 Lista Transazioni" in sections:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            
            transactions_df = self.transaction_dal.get_transactions(start_date=start_date, end_date=end_date)
            report_data['transactions'] = transactions_df.to_dict('records') if not transactions_df.empty else []
        
        return report_data
    
    def _render_empty_month_suggestions(self, year: int, month: int):
        """Suggerimenti per mesi vuoti"""
        st.subheader("💡 Suggerimenti")
        
        # Controlla mesi vicini
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Mese precedente
        prev_month = month - 1
        prev_year = year
        if prev_month <= 0:
            prev_month = 12
            prev_year -= 1
        
        prev_data = self.transaction_dal.get_monthly_summary(prev_year, prev_month)
        
        # Mese successivo (se non futuro)
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        is_next_future = (next_year > current_year or 
                         (next_year == current_year and next_month > current_month))
        
        if not is_next_future:
            next_data = self.transaction_dal.get_monthly_summary(next_year, next_month)
        else:
            next_data = {'transactions_count': 0}
        
        col1, col2 = st.columns(2)
        
        with col1:
            if prev_data['transactions_count'] > 0:
                st.info(f"📅 **{get_month_name(prev_month)} {prev_year}** ha {prev_data['transactions_count']} transazioni")
                if st.button(f"👀 Vedi {get_month_name(prev_month)} {prev_year}", key=f"nav_prev_{prev_year}_{prev_month}"):
                    # Set navigation state
                    st.session_state.report_navigate_to_year = prev_year
                    st.session_state.report_navigate_to_month = prev_month
                    st.rerun()
        
        with col2:
            if not is_next_future and next_data['transactions_count'] > 0:
                st.info(f"📅 **{get_month_name(next_month)} {next_year}** ha {next_data['transactions_count']} transazioni")
                if st.button(f"👀 Vedi {get_month_name(next_month)} {next_year}", key=f"nav_next_{next_year}_{next_month}"):
                    # Set navigation state
                    st.session_state.report_navigate_to_year = next_year
                    st.session_state.report_navigate_to_month = next_month
                    st.rerun()
        
        # Link per aggiungere transazioni
        st.markdown("---")
        st.info("💡 **Suggerimento**: Vai alla sezione 'Nuova Transazione' per aggiungere dati a questo mese")

class TransactionManager:
    """Gestione transazioni"""
    
    def __init__(self, transaction_dal: TransactionDAL, category_manager: CategoryManager):
        self.transaction_dal = transaction_dal
        self.category_manager = category_manager
    
    def render_add_transaction(self):
        """Form aggiunta transazione"""
        st.header("💳 Nuova Transazione")
        
        # Initialize session state for form reset
        if 'form_reset_key' not in st.session_state:
            st.session_state.form_reset_key = 0
        
        # Selezione tipo transazione FUORI dal form per aggiornamento dinamico
        transaction_type = st.selectbox(
            "Tipo Transazione", 
            ["Entrata", "Uscita"],
            key=f"transaction_type_selector_{st.session_state.form_reset_key}"
        )
        
        # Carica categorie in base al tipo selezionato
        categories = self.category_manager.get_categories(transaction_type)
        if not categories:
            st.error(f"❌ Nessuna categoria disponibile per {transaction_type}")
            st.info("💡 Vai in 'Gestione Categorie' per aggiungerne")
            return
        
        # Mostra categorie disponibili
        st.success(f"📋 Categorie disponibili per **{transaction_type}**: {len(categories)}")
        
        # Form con key unico per il reset
        form_key = f"new_transaction_{st.session_state.form_reset_key}"
        
        with st.form(form_key):
            col1, col2 = st.columns(2)
            
            with col1:
                # Categorie filtrate dinamicamente
                category_options = {cat['name']: cat['id'] for cat in categories}
                selected_category = st.selectbox(
                    "Categoria",
                    list(category_options.keys()),
                    help=f"Categorie per {transaction_type}",
                    key=f"category_{st.session_state.form_reset_key}"
                )
                category_id = category_options[selected_category]
                
                amount = st.number_input(
                    "Importo (€)", 
                    min_value=0.01, 
                    step=0.01,
                    format="%.2f",
                    key=f"amount_{st.session_state.form_reset_key}"
                )
                
                transaction_date = st.date_input(
                    "Data", 
                    value=date.today(),
                    key=f"date_{st.session_state.form_reset_key}"
                )
            
            with col2:
                description = st.text_input(
                    "Descrizione", 
                    max_chars=200,
                    key=f"description_{st.session_state.form_reset_key}"
                )
                
                recurrence = st.selectbox(
                    "Ricorrenza",
                    ["Nessuna", "Mensile", "Settimanale", "Annuale"],
                    key=f"recurrence_{st.session_state.form_reset_key}"
                )
                
                tags_input = st.text_input(
                    "Tag (separati da virgola)",
                    key=f"tags_{st.session_state.form_reset_key}"
                )
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                
                notes = st.text_area(
                    "Note",
                    key=f"notes_{st.session_state.form_reset_key}"
                )
            
            # Buttons row
            col_submit, col_reset = st.columns([3, 1])
            
            with col_submit:
                submitted = st.form_submit_button("💾 Aggiungi Transazione", use_container_width=True, type="primary")
            
            with col_reset:
                reset_clicked = st.form_submit_button("🔄 Reset", use_container_width=True)
            
            # Handle form submission
            if submitted:
                if description.strip():
                    transaction_data = {
                        'date': datetime.combine(transaction_date, datetime.min.time()),
                        'amount': amount,
                        'description': description,
                        'notes': notes,
                        'category_id': category_id,
                        'transaction_type': transaction_type,
                        'recurrence_type': recurrence,
                        'tags': tags
                    }
                    
                    if self.transaction_dal.add_transaction(transaction_data):
                        st.success("✅ Transazione aggiunta con successo!")
                        
                        # Reset the form by incrementing the key
                        st.session_state.form_reset_key += 1
                        
                        # Small delay and rerun
                        st.rerun()
                else:
                    st.error("❌ La descrizione è obbligatoria!")
            
            # Handle reset button
            if reset_clicked:
                st.session_state.form_reset_key += 1
                st.success("🔄 Form resettato!")
                st.rerun()
    
    def render_transaction_list(self):
        """Lista transazioni"""
        st.header("📋 Lista Transazioni")
        
        # Filtri
        col1, col2, col3 = st.columns(3)
        
        with col1:
            type_filter = st.selectbox("Tipo", ["Tutti", "Entrata", "Uscita"])
        
        with col2:
            # Opzioni per il filtro data
            date_filter_options = ["Tutte le date", "Ultimi 30 giorni", "Ultimi 90 giorni", "Personalizzato"]
            date_filter = st.selectbox("Periodo", date_filter_options)
            
            # Imposta le date in base alla selezione
            if date_filter == "Tutte le date":
                start_date = None
                end_date = None
            elif date_filter == "Ultimi 30 giorni":
                end_date = datetime.combine(date.today(), datetime.max.time())
                start_date = datetime.combine(date.today() - timedelta(days=30), datetime.min.time())
            elif date_filter == "Ultimi 90 giorni":
                end_date = datetime.combine(date.today(), datetime.max.time())
                start_date = datetime.combine(date.today() - timedelta(days=90), datetime.min.time())
            else:  # Personalizzato
                date_range = st.date_input(
                    "Seleziona periodo",
                    value=[date.today() - timedelta(days=30), date.today()],
                    max_value=date.today(),
                    key="custom_date_range"
                )
                
                if len(date_range) == 2:
                    start_date = datetime.combine(date_range[0], datetime.min.time())
                    end_date = datetime.combine(date_range[1], datetime.max.time())
                else:
                    start_date = None
                    end_date = None
        
        with col3:
            categories = self.category_manager.get_categories()
            category_names = ["Tutte"] + [cat['name'] for cat in categories]
            category_filter = st.selectbox("Categoria", category_names)
        
        # Apply filters
        df = self.transaction_dal.get_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type=None if type_filter == "Tutti" else type_filter
        )
        
        if category_filter != "Tutte":
            df = df[df['category_name'] == category_filter]
        
        if df.empty:
            if date_filter == "Tutte le date":
                st.info("📝 Nessuna transazione trovata nel database")
            else:
                st.info(f"📝 Nessuna transazione trovata per il periodo selezionato ({date_filter})")
                st.info("💡 Prova a selezionare 'Tutte le date' per vedere tutte le transazioni")
            return
        
        # Enhanced Statistics based on filter type
        if type_filter == "Tutti":
            # Detailed stats when showing all transactions
            entrate_df = df[df['transaction_type'] == 'Entrata']
            uscite_df = df[df['transaction_type'] == 'Uscita']
            
            somma_entrate = entrate_df['amount'].sum() if not entrate_df.empty else 0
            somma_uscite = uscite_df['amount'].sum() if not uscite_df.empty else 0
            saldo_netto = somma_entrate - somma_uscite
            importo_medio = df['amount'].mean() if not df.empty else 0
            
            # Display enhanced stats
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("📊 Totale Transazioni", len(df))
            
            with col2:
                st.metric("💰 Somma Entrate", f"€{somma_entrate:,.2f}")
            
            with col3:
                st.metric("💸 Somma Uscite", f"€{somma_uscite:,.2f}")
            
            with col4:
                color = "normal" if saldo_netto >= 0 else "inverse"
                st.metric(
                    "💵 Saldo Netto", 
                    f"€{saldo_netto:,.2f}",
                    delta=f"€{saldo_netto:,.2f}"
                )
            
            with col5:
                st.metric("📈 Importo Medio", f"€{importo_medio:,.2f}")
            
            # Additional breakdown
            if not entrate_df.empty and not uscite_df.empty:
                st.markdown("---")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    ratio_entrate = (len(entrate_df) / len(df)) * 100
                    st.metric("📈 % Entrate", f"{ratio_entrate:.1f}%")
                
                with col_b:
                    ratio_uscite = (len(uscite_df) / len(df)) * 100
                    st.metric("📉 % Uscite", f"{ratio_uscite:.1f}%")
                
                with col_c:
                    if somma_entrate > 0:
                        efficienza = (saldo_netto / somma_entrate) * 100
                        st.metric("⚡ Efficienza Risparmio", f"{efficienza:.1f}%")
        
        else:
            # Simple stats for filtered view
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Totale Transazioni", len(df))
            with col2:
                st.metric("💰 Somma Importi", f"€{df['amount'].sum():,.2f}")
            with col3:
                if len(df) > 0:
                    st.metric("📈 Media Importo", f"€{df['amount'].mean():,.2f}")
        
        # Mostra il periodo attivo
        if start_date and end_date:
            st.caption(f"📅 Periodo: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
        elif date_filter != "Tutte le date":
            st.caption(f"📅 Periodo: {date_filter}")
        else:
            st.caption("📅 Periodo: Tutte le transazioni")
        
        # Display table
        display_df = df[['date', 'category_name', 'description', 'amount', 'transaction_type']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%d/%m/%Y')
        display_df['amount'] = display_df['amount'].apply(lambda x: f"€{x:,.2f}")
        
        display_df.columns = ['Data', 'Categoria', 'Descrizione', 'Importo', 'Tipo']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Export
        if st.button("📥 Esporta CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"transazioni_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

class DatabaseManagementUI:
    """UI per gestione database avanzata"""
    
    def __init__(self, current_db_manager: DatabaseManager):
        self.current_db_manager = current_db_manager
    
    def render_first_run_setup(self):
        """Setup iniziale per primo avvio"""
        st.title("🚀 Benvenuto in Budget Familiare!")
        st.markdown("### Configurazione Database Iniziale")
        
        st.info("👋 Sembra essere il tuo primo avvio! Configura il tuo database per iniziare.")
        
        return self.render_create_database_form("setup")
    
    def render_create_database_form(self, form_key_suffix: str = ""):
        """Form per creare nuovo database"""
        st.subheader("🆕 Crea Nuovo Database")
        
        # Database type selection
        available_dbs = DatabaseConfig.get_available_databases()
        available_types = [db for db in available_dbs if db['available']]
        
        if not available_types:
            st.error("❌ Nessun database disponibile!")
            return False
        
        form_key = f"create_db_form_{form_key_suffix}"
        
        with st.form(form_key):
            # Database name
            db_name = st.text_input(
                "📝 Nome Configurazione",
                value="Il Mio Budget",
                help="Nome identificativo per questa configurazione database"
            )
            
            # Database type
            db_type_names = {db['type']: f"{db['icon']} {db['name']}" for db in available_types}
            selected_display = st.selectbox(
                "🗄️ Tipo Database",
                list(db_type_names.values()),
                help="Scegli il tipo di database da utilizzare"
            )
            
            # Find selected db_type
            db_type = next(k for k, v in db_type_names.items() if v == selected_display)
            db_config = DatabaseConfig.SUPPORTED_DATABASES[db_type]
            
            # Show description
            st.info(f"ℹ️ {db_config['description']}")
            
            # Dynamic fields based on database type
            params = {}
            for field in db_config.get('fields', []):
                field_key = f"{field['name']}_{form_key_suffix}"
                
                if field['type'] == 'text':
                    params[field['name']] = st.text_input(
                        field['label'],
                        value=str(field['default']),
                        key=field_key
                    )
                elif field['type'] == 'password':
                    params[field['name']] = st.text_input(
                        field['label'],
                        type='password',
                        key=field_key
                    )
                elif field['type'] == 'number':
                    params[field['name']] = st.number_input(
                        field['label'],
                        value=int(field['default']),
                        key=field_key
                    )
            
            # Submit buttons
            col1, col2 = st.columns(2)
            
            with col1:
                test_connection = st.form_submit_button("🔍 Testa Connessione")
            
            with col2:
                create_database = st.form_submit_button("🚀 Crea Database", type="primary")
            
            # Handle form actions
            if test_connection:
                success, message = DatabaseConfig.test_connection(db_type, **params)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ Connessione fallita: {message}")
            
            if create_database:
                if not db_name.strip():
                    st.error("❌ Il nome della configurazione è obbligatorio!")
                    return False
                
                # Test connection first
                success, message = DatabaseConfig.test_connection(db_type, **params)
                if not success:
                    st.error(f"❌ Impossibile connettersi al database: {message}")
                    return False
                
                # Add to registry
                if not DatabaseRegistry.add_database_config(db_name.strip(), db_type, **params):
                    st.error("❌ Nome configurazione già esistente!")
                    return False
                
                # Create and switch to new database
                try:
                    new_manager = DatabaseSwitcher.create_new_database(db_type, **params)
                    
                    # Set as current
                    DatabaseRegistry.set_current_database(db_name.strip())
                    set_database_manager(new_manager)
                    
                    st.success(f"✅ Database '{db_name}' creato e configurato!")
                    return True
                    
                except Exception as e:
                    st.error(f"❌ Errore nella creazione del database: {e}")
                    # Remove from registry if creation failed
                    DatabaseRegistry.remove_database_config(db_name.strip())
                    return False
        
        return False
    
    def render_database_list(self):
        """Lista database configurati"""
        st.subheader("📚 Database Configurati")
        
        configs = DatabaseRegistry.list_database_configs()
        
        if not configs:
            st.info("📝 Nessun database configurato. Crea il primo database!")
            return
        
        for config in configs:
            with st.expander(
                f"{'🟢' if config['is_current'] else '⚫'} {config['name']}", 
                expanded=config['is_current']
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    db_info = DatabaseConfig.SUPPORTED_DATABASES[config['type']]
                    st.markdown(f"**{db_info['icon']} {db_info['name']}**")
                    st.caption(db_info['description'])
                    
                    # Show connection details (without sensitive info)
                    if config['type'] != 'sqlite':
                        params = config['params']
                        st.markdown(f"**Host:** {params.get('host', 'N/A')}")
                        st.markdown(f"**Database:** {params.get('db_name', 'N/A')}")
                        st.markdown(f"**User:** {params.get('user', 'N/A')}")
                    else:
                        st.markdown(f"**File:** {config['params'].get('db_name', 'N/A')}.db")
                    
                    # Timestamps
                    if config.get('last_used'):
                        last_used = datetime.fromisoformat(config['last_used'])
                        st.caption(f"Ultimo uso: {last_used.strftime('%d/%m/%Y %H:%M')}")
                
                with col2:
                    # Action buttons
                    if config['is_current']:
                        st.success("✅ Attivo")
                        
                        # Add disconnect button for active database
                        if st.button(f"🔌 Disconnetti", key=f"disconnect_{config['name']}"):
                            self._disconnect_database()
                            
                    else:
                        if st.button(f"🔄 Passa a {config['name']}", key=f"switch_{config['name']}"):
                            self._switch_to_database(config)
                    
                    # Edit button
                    if st.button(f"✏️ Modifica", key=f"edit_{config['name']}"):
                        st.session_state[f"editing_{config['name']}"] = True
                        st.rerun()
                    
                    # Delete button - now available for all databases
                    confirm_key = f"confirm_delete_{config['name']}"
                    
                    if not st.session_state.get(confirm_key, False):
                        # First click - show delete button
                        if st.button(f"🗑️ Elimina", key=f"delete_{config['name']}"):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        # Confirmation mode - show warning and yes/no buttons
                        if config['is_current']:
                            st.error("⚠️ Eliminerai il database attivo!")
                        else:
                            st.error("⚠️ Confermi eliminazione?")
                        
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button("✅ Sì", key=f"confirm_yes_{config['name']}"):
                                # Actually delete the database
                                if DatabaseRegistry.remove_database_config(config['name']):
                                    st.success(f"✅ Database '{config['name']}' eliminato!")
                                    # Reset confirmation state
                                    st.session_state[confirm_key] = False
                                    
                                    # If we deleted the current database, we need to handle no active database
                                    if config['is_current']:
                                        st.warning("🔄 Database attivo eliminato. Seleziona o crea un nuovo database.")
                                        # Force rerun to update the UI
                                    
                                    st.rerun()
                                else:
                                    st.error(f"❌ Errore nell'eliminazione di '{config['name']}'")
                        
                        with col_b:
                            if st.button("❌ No", key=f"confirm_no_{config['name']}"):
                                # Cancel deletion
                                st.session_state[confirm_key] = False
                                st.rerun()
                
                # Edit form
                if st.session_state.get(f"editing_{config['name']}", False):
                    st.divider()
                    self._render_edit_database_form(config)
    
    def _disconnect_database(self):
        """Disconnette il database corrente"""
        try:
            # Clear the current database in registry
            configs = DatabaseRegistry.load_configs()
            configs['current_database'] = None
            DatabaseRegistry.save_configs(configs)
            
            st.success("🔌 Database disconnesso! Seleziona o crea un nuovo database per continuare.")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Errore nella disconnessione: {e}")
    
    def _render_edit_database_form(self, config: Dict):
        """Form per modificare configurazione database"""
        st.markdown("### ✏️ Modifica Configurazione")
        
        db_type = config['type']
        db_config = DatabaseConfig.SUPPORTED_DATABASES[db_type]
        
        with st.form(f"edit_form_{config['name']}"):
            # Current parameters
            current_params = config['params'].copy()
            new_params = {}
            
            for field in db_config.get('fields', []):
                current_value = current_params.get(field['name'], field['default'])
                
                if field['type'] == 'password':
                    new_params[field['name']] = st.text_input(
                        f"{field['label']} (lascia vuoto per non modificare)",
                        type='password',
                        key=f"edit_{field['name']}_{config['name']}"
                    )
                    # Keep old value if empty
                    if not new_params[field['name']]:
                        new_params[field['name']] = current_value
                else:
                    if field['type'] == 'text':
                        new_params[field['name']] = st.text_input(
                            field['label'],
                            value=str(current_value),
                            key=f"edit_{field['name']}_{config['name']}"
                        )
                    elif field['type'] == 'number':
                        new_params[field['name']] = st.number_input(
                            field['label'],
                            value=int(current_value),
                            key=f"edit_{field['name']}_{config['name']}"
                        )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                test_btn = st.form_submit_button("🔍 Testa")
            
            with col2:
                save_btn = st.form_submit_button("💾 Salva", type="primary")
            
            with col3:
                cancel_btn = st.form_submit_button("❌ Annulla")
            
            if test_btn:
                success, message = DatabaseConfig.test_connection(db_type, **new_params)
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            
            if save_btn:
                # Test connection before saving
                success, message = DatabaseConfig.test_connection(db_type, **new_params)
                if success:
                    DatabaseRegistry.update_database_config(config['name'], params=new_params)
                    st.success("✅ Configurazione aggiornata!")
                    st.session_state[f"editing_{config['name']}"] = False
                    st.rerun()
                else:
                    st.error(f"❌ Connessione fallita: {message}")
            
            if cancel_btn:
                st.session_state[f"editing_{config['name']}"] = False
                st.rerun()
    
    def _switch_to_database(self, config: Dict):
        """Cambia al database selezionato"""
        try:
            with st.spinner(f"🔄 Cambio a database '{config['name']}'..."):
                # Create new manager
                new_manager = DatabaseManager(config['type'], **config['params'])
                
                # Switch with data migration
                new_manager = DatabaseSwitcher.switch_database(
                    self.current_db_manager,
                    config
                )
                
                # Update registry and global manager
                DatabaseRegistry.set_current_database(config['name'])
                set_database_manager(new_manager)
                
                st.success(f"✅ Database cambiato a '{config['name']}'!")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Errore nel cambio database: {e}")
    
    def render_database_info(self):
        """Informazioni database corrente"""
        st.subheader("🗄️ Database Corrente")
        
        current_config = DatabaseRegistry.get_current_database_config()
        if not current_config:
            st.warning("⚠️ Nessun database attivo")
            st.info("💡 Vai nella tab 'Database Lista' per selezionare un database o crearne uno nuovo")
            return
        
        db_info = self.current_db_manager.get_database_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Nome:** {current_config['name']}")
            st.info(f"**Tipo:** {db_info['type'].upper()}")
            if 'config' in db_info:
                config = db_info['config']
                st.markdown(f"**{config['icon']} {config['name']}**")
                st.caption(config['description'])
                
                # Features
                features = config.get('features', [])
                if features:
                    st.markdown("**Funzionalità:**")
                    for feature in features:
                        st.markdown(f"• {feature}")
        
        with col2:
            if 'stats' in db_info:
                stats = db_info['stats']
                for key, value in stats.items():
                    st.metric(key.replace('_', ' ').title(), value)
            
            # Additional info based on database type
            if db_info['type'] == 'sqlite' and 'file_size' in db_info:
                st.metric("Dimensione File", db_info['file_size'])
            elif 'database_size' in db_info:
                st.metric("Dimensione Database", db_info['database_size'])
    
    def render_database_operations(self):
        """Operazioni database"""
        st.subheader("🛠️ Operazioni Database")
        
        current_config = DatabaseRegistry.get_current_database_config()
        if not current_config:
            st.warning("⚠️ Nessun database attivo per eseguire operazioni")
            st.info("💡 Seleziona prima un database dalla tab 'Database Lista'")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔄 Reset Database**")
            st.caption("Elimina tutti i dati e ricrea le tabelle")
            
            if st.button("🗑️ Reset Database", type="secondary"):
                if st.session_state.get('confirm_reset', False):
                    try:
                        self.current_db_manager.reset_database()
                        DefaultCategories.ensure_default_categories(self.current_db_manager)
                        st.success("✅ Database resettato!")
                        st.session_state['confirm_reset'] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Errore reset: {e}")
                else:
                    st.session_state['confirm_reset'] = True
                    st.rerun()
            
            if st.session_state.get('confirm_reset', False):
                st.error("⚠️ Confermi di voler eliminare TUTTI i dati?")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Sì, Elimina"):
                        st.session_state['confirm_reset'] = True
                        st.rerun()
                with col_b:
                    if st.button("❌ Annulla"):
                        st.session_state['confirm_reset'] = False
                        st.rerun()
        
        with col2:
            st.markdown("**📤 Export Dati**")
            st.caption("Esporta tutti i dati in JSON")
            
            if st.button("📊 Export JSON"):
                try:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    export_name = f"budget_export_{timestamp}"
                    
                    data = self.current_db_manager.export_all_data(export_name)
                    if data:
                        json_data = json.dumps(data, indent=2, ensure_ascii=False, default=str)
                        
                        st.download_button(
                            label="💾 Download JSON",
                            data=json_data,
                            file_name=f"{export_name}.json",
                            mime="application/json"
                        )
                        
                        st.success(f"✅ Dati esportati in exports/{export_name}.json!")
                    else:
                        st.warning("⚠️ Nessun dato da esportare")
                except Exception as e:
                    st.error(f"❌ Errore export: {e}")
        
        with col3:
            st.markdown("**📥 Import Dati**")
            st.caption("Importa dati da file JSON")
            
            uploaded_file = st.file_uploader(
                "Carica file JSON",
                type=['json'],
                key="import_json"
            )
            
            if uploaded_file and st.button("📥 Importa"):
                try:
                    data = json.load(uploaded_file)
                    if self.current_db_manager.import_data(data):
                        st.success("✅ Dati importati con successo!")
                        st.rerun()
                    else:
                        st.error("❌ Errore nell'importazione")
                except Exception as e:
                    st.error(f"❌ Errore lettura file: {e}")
    
    def render_file_management(self):
        """Gestione file organizzata"""
        st.subheader("📁 Gestione File")
        
        # File organization overview
        files_by_type = FileManager.list_files_by_type()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📁 Database", len(files_by_type['databases']))
        with col2:
            st.metric("⚙️ Config", len(files_by_type['configs']))
        with col3:
            st.metric("💾 Backup", len(files_by_type['backups']))
        with col4:
            st.metric("📤 Export", len(files_by_type['exports']))
        
        # Detailed file listing
        for file_type, files in files_by_type.items():
            if files:
                st.subheader(f"📂 {file_type.title()}")
                
                for file_name in files:
                    with st.expander(f"📄 {file_name}"):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            # Get file path based on type
                            if file_type == 'databases':
                                file_path = FileManager.DATA_DIR / file_name
                            elif file_type == 'configs':
                                file_path = FileManager.CONFIG_DIR / file_name
                            elif file_type == 'backups':
                                file_path = FileManager.BACKUPS_DIR / file_name
                            elif file_type == 'exports':
                                file_path = FileManager.EXPORTS_DIR / file_name
                            
                            if file_path.exists():
                                stat = file_path.stat()
                                st.write(f"**Dimensione:** {stat.st_size / 1024:.1f} KB")
                                st.write(f"**Modificato:** {datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M')}")
                                st.write(f"**Percorso:** `{file_path}`")
                        
                        with col_b:
                            # Download button for exports and configs
                            if file_type in ['exports', 'configs', 'backups'] and file_name.endswith('.json'):
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    
                                    st.download_button(
                                        label="📥 Download",
                                        data=content,
                                        file_name=file_name,
                                        mime="application/json",
                                        key=f"download_{file_type}_{file_name}"
                                    )
                                except Exception as e:
                                    st.error(f"Errore lettura: {e}")
                            
                            # Delete button (except for current database)
                            if not (file_type == 'databases' and self._is_current_database_file(file_name)):
                                if st.button(f"🗑️ Elimina", key=f"delete_{file_type}_{file_name}"):
                                    try:
                                        file_path.unlink()
                                        st.success(f"File {file_name} eliminato!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Errore eliminazione: {e}")
        
        # Cleanup tools
        st.divider()
        st.subheader("🧹 Pulizia File")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🗑️ Pulizia Automatica**")
            days_old = st.number_input("Elimina file più vecchi di (giorni):", min_value=1, value=30)
            
            if st.button("🧹 Pulisci File Vecchi"):
                try:
                    cleaned = FileManager.cleanup_old_files(days_old)
                    if cleaned:
                        st.success(f"✅ File puliti: {', '.join(cleaned)}")
                    else:
                        st.info("ℹ️ Nessun file da pulire")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Errore pulizia: {e}")
        
        with col2:
            st.markdown("**📊 Statistiche Spazio**")
            try:
                total_size = 0
                for file_type, files in files_by_type.items():
                    for file_name in files:
                        if file_type == 'databases':
                            file_path = FileManager.DATA_DIR / file_name
                        elif file_type == 'configs':
                            file_path = FileManager.CONFIG_DIR / file_name
                        elif file_type == 'backups':
                            file_path = FileManager.BACKUPS_DIR / file_name
                        elif file_type == 'exports':
                            file_path = FileManager.EXPORTS_DIR / file_name
                        
                        if file_path.exists():
                            total_size += file_path.stat().st_size
                
                st.metric("Spazio Totale", f"{total_size / 1024:.1f} KB")
                
            except Exception as e:
                st.error(f"Errore calcolo spazio: {e}")
    
    def _is_current_database_file(self, file_name: str) -> bool:
        """Verifica se il file è il database corrente"""
        try:
            current_config = DatabaseRegistry.get_current_database_config()
            if current_config and current_config['type'] == 'sqlite':
                current_db_name = current_config['params'].get('db_name', 'budget_famiglia')
                return file_name == f"{current_db_name}.db"
        except:
            pass
        return False

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    st.set_page_config(
        page_title="Budget Familiare Pro",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply professional styling
    hide_streamlit_ui()
    
    # Check for first run
    if check_first_run():
        db_ui = DatabaseManagementUI(None)
        
        if db_ui.render_first_run_setup():
            st.success("🎉 Configurazione completata! Ricarica la pagina per continuare.")
            st.stop()
        else:
            st.stop()
    
    # Check if we have a current database
    current_config = DatabaseRegistry.get_current_database_config()
    if not current_config:
        st.title("💰 Budget Familiare Professional")
        st.warning("🔌 Nessun database attivo")
        st.info("🏗️ Seleziona o crea un database per continuare")
        
        # Show database management directly
        db_ui = DatabaseManagementUI(None)
        
        # Simplified interface with just create/select options
        tab1, tab2 = st.tabs(["📚 Seleziona Database", "🆕 Crea Nuovo"])
        
        with tab1:
            db_ui.render_database_list()
        
        with tab2:
            db_ui.render_create_database_form("main")
        
        st.stop()
    
    # Initialize database
    try:
        db_manager = get_database_manager()
        db_info = db_manager.get_database_info()
    except Exception as e:
        st.error(f"🔴 Errore database: {e}")
        st.stop()
    
    # Initialize DAL and managers
    transaction_dal = TransactionDAL(db_manager)
    category_manager = CategoryManager(db_manager)
    
    # Header
    st.title("💰 Budget Familiare Professional")
    
    # Show current database info
    if current_config:
        st.markdown(f"*Database: **{current_config['name']}** ({db_info['type'].upper()}) | "
                    f"Transazioni: {db_info.get('stats', {}).get('transactions', 0)}*")
    else:
        st.markdown(f"*Database: {db_info['type'].upper()} | "
                    f"Transazioni: {db_info.get('stats', {}).get('transactions', 0)}*")
    
    # Sidebar
    with st.sidebar:
        st.header("🧭 Navigazione")
        
        page = st.radio(
            "Sezioni:",
            [
                "📊 Dashboard",
                "💳 Nuova Transazione", 
                "📋 Lista Transazioni",
                "📈 Report Mensili",
                "🏷️ Gestione Categorie",
                "🗄️ Gestione Database",
                "⚙️ Impostazioni"
            ]
        )
        
        st.divider()
        
        # Quick stats - now intelligent
        st.subheader("ℹ️ Info Rapide")
        
        # Use the smart summary that shows relevant data
        total_summary = transaction_dal.get_total_summary()
        if total_summary['transactions_count'] > 0:
            recent_summary = transaction_dal.get_recent_summary(30)
            
            if recent_summary['transactions_count'] > 0:
                # Show recent data
                st.metric("💰 Saldo (30gg)", f"€{recent_summary['saldo']:,.2f}")
                st.metric("📝 Transazioni (30gg)", recent_summary['transactions_count'])
            else:
                # Show total data
                st.metric("💰 Saldo Totale", f"€{total_summary['saldo']:,.2f}")
                st.metric("📝 Transazioni Totali", total_summary['transactions_count'])
        else:
            st.metric("💰 Saldo", "€0.00")
            st.metric("📝 Transazioni", "0")
        
        # Current database info
        st.divider()
        if current_config:
            db_config = DatabaseConfig.SUPPORTED_DATABASES.get(db_info['type'], {})
            st.markdown(f"**{db_config.get('icon', '🗄️')} {current_config['name']}**")
            st.caption(f"Tipo: {db_info['type'].upper()}")
            
            # Show file location for SQLite
            if db_info['type'] == 'sqlite' and 'file_location' in db_info:
                st.caption(f"📂 Cartella: data/")
        
        # File structure summary
        st.subheader("📁 File")
        try:
            files_info = FileManager.list_files_by_type()
            file_summary = {
                '💾': len(files_info.get('databases', [])),
                '📦': len(files_info.get('backups', [])),
                '📤': len(files_info.get('exports', []))
            }
            
            for icon, count in file_summary.items():
                if count > 0:
                    st.caption(f"{icon} {count}")
        except:
            pass
        
        # Quick database switch
        st.subheader("🔄 Database Veloci")
        configs = DatabaseRegistry.list_database_configs()
        for config in configs[:3]:  # Show max 3 for quick access
            if not config['is_current']:
                if st.button(f"↪️ {config['name']}", key=f"quick_{config['name']}"):
                    db_ui = DatabaseManagementUI(db_manager)
                    db_ui._switch_to_database(config)
    
    # Main content routing
    if page == "📊 Dashboard":
        dashboard = Dashboard(transaction_dal)
        dashboard.render_overview()
        dashboard.render_charts()
        
    elif page == "💳 Nuova Transazione":
        transaction_manager = TransactionManager(transaction_dal, category_manager)
        transaction_manager.render_add_transaction()
        
    elif page == "📋 Lista Transazioni":
        transaction_manager = TransactionManager(transaction_dal, category_manager)
        transaction_manager.render_transaction_list()
    
    elif page == "📈 Report Mensili":
        report_manager = MonthlyReportManager(transaction_dal, category_manager)
        report_manager.render_monthly_reports()
        
    elif page == "🏷️ Gestione Categorie":
        st.header("🏷️ Gestione Categorie")
        
        # Category statistics
        stats = category_manager.get_category_stats()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Totale Categorie", stats.get('total_categories', 0))
        with col2:
            st.metric("✅ Attive", stats.get('active_categories', 0))
        with col3:
            st.metric("📈 Entrate", stats.get('income_categories', 0))
        with col4:
            st.metric("📉 Uscite", stats.get('expense_categories', 0))
        
        # Show categories by type
        for trans_type in ["Entrata", "Uscita"]:
            st.subheader(f"📂 Categorie {trans_type}")
            categories = category_manager.get_categories(trans_type)
            
            if categories:
                # Display in columns
                cols = st.columns(min(4, len(categories)))
                for i, cat in enumerate(categories):
                    with cols[i % 4]:
                        st.markdown(f"**{cat['name']}**")
                        st.color_picker(
                            "Colore categoria", 
                            value=cat['color'], 
                            key=f"color_view_{cat['id']}", 
                            disabled=True,
                            label_visibility="hidden"
                        )
            
            # Add new category with advanced icon selector (NO EXPANDER)
            st.markdown(f"### ➕ Aggiungi Nuova Categoria {trans_type}")
            
            # Initialize session state for category name to enable icon suggestions
            category_name_key = f"new_category_name_{trans_type}"
            if category_name_key not in st.session_state:
                st.session_state[category_name_key] = ""
            
            # Category name input (outside form to enable real-time icon suggestions)
            new_name = st.text_input(
                "📝 Nome categoria",
                value=st.session_state[category_name_key],
                key=f"category_name_input_{trans_type}",
                help="Inserisci il nome della categoria per vedere suggerimenti di icone",
                on_change=lambda: setattr(st.session_state, category_name_key, st.session_state[f"category_name_input_{trans_type}"])
            )
            
            # Update session state
            st.session_state[category_name_key] = new_name
            
            # Show icon selector WITHOUT expander (use_expander=False)
            selected_icon = render_icon_selector(trans_type, new_name, f"new_category_{trans_type}", use_expander=False)
            
            # Color picker
            new_color = st.color_picker(
                "🎨 Colore categoria", 
                value="#3498db",
                key=f"color_picker_{trans_type}"
            )
            
            # Add category button
            col_btn1, col_btn2 = st.columns([1, 1])
            
            with col_btn1:
                if st.button(f"✅ Aggiungi Categoria {trans_type}", key=f"add_category_btn_{trans_type}", type="primary", use_container_width=True):
                    if new_name.strip():
                        # Create full name with icon
                        full_name = f"{selected_icon} {new_name.strip()}"
                        
                        if category_manager.add_category(full_name, trans_type, new_color, selected_icon):
                            st.success(f"✅ Categoria '{new_name}' aggiunta con icona {selected_icon}!")
                            
                            # Reset form
                            st.session_state[category_name_key] = ""
                            st.session_state[f"selected_icon_new_category_{trans_type}"] = "💰"
                            
                            st.rerun()
                        else:
                            st.error(f"❌ Errore nell'aggiunta della categoria '{new_name}'")
                    else:
                        st.error("❌ Il nome della categoria è obbligatorio!")
            
            with col_btn2:
                if st.button(f"🔄 Reset Form", key=f"reset_category_form_{trans_type}", use_container_width=True):
                    # Reset all form fields
                    st.session_state[category_name_key] = ""
                    st.session_state[f"selected_icon_new_category_{trans_type}"] = "💰"
                    st.rerun()
            
            # Show preview
            if new_name.strip():
                st.markdown("**👀 Anteprima categoria:**")
                preview_name = f"{selected_icon} {new_name.strip()}"
                st.markdown(f"<div style='background-color: {new_color}; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;'>{preview_name}</div>", unsafe_allow_html=True)
            
            st.divider()
        
        # Unused categories warning
        if stats.get('unused_categories'):
            st.warning(f"⚠️ {len(stats['unused_categories'])} categorie non utilizzate")
            with st.expander("Categorie non utilizzate"):
                for cat in stats['unused_categories']:
                    st.write(f"• {cat['name']} ({cat['type']})")
    
    elif page == "🗄️ Gestione Database":
        st.header("🗄️ Gestione Database Avanzata")
        
        db_ui = DatabaseManagementUI(db_manager)
        
        # Database tabs with file management
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Info Corrente", 
            "📚 Database Lista", 
            "🆕 Crea Nuovo", 
            "🛠️ Operazioni",
            "📁 Gestione File"
        ])
        
        with tab1:
            db_ui.render_database_info()
            
            # Show current file structure
            st.divider()
            st.subheader("📂 Struttura File")
            
            files_info = FileManager.list_files_by_type()
            for file_type, count in [(k, len(v)) for k, v in files_info.items()]:
                icon_map = {
                    'databases': '💾',
                    'configs': '⚙️', 
                    'backups': '📦',
                    'exports': '📤',
                    'logs': '📋'
                }
                icon = icon_map.get(file_type, '📄')
                st.markdown(f"**{icon} {file_type.title()}:** {count} file(s)")
        
        with tab2:
            db_ui.render_database_list()
        
        with tab3:
            db_ui.render_create_database_form("main")
        
        with tab4:
            db_ui.render_database_operations()
        
        with tab5:
            db_ui.render_file_management()
    
    elif page == "⚙️ Impostazioni":
        st.header("⚙️ Impostazioni Applicazione")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎨 Interfaccia")
            st.selectbox("Tema", ["Light", "Dark"], disabled=True)
            st.selectbox("Lingua", ["Italiano", "English"], disabled=True)
            st.selectbox("Valuta", ["EUR (€)", "USD ($)", "GBP (£)"], disabled=True)
            
        with col2:
            st.subheader("🔔 Notifiche")
            st.checkbox("Avvisi budget", disabled=True)
            st.checkbox("Promemoria transazioni ricorrenti", disabled=True)
            st.checkbox("Report mensili", disabled=True)
        
        st.info("🚧 Impostazioni in sviluppo - funzionalità in arrivo!")
        
        # File structure info
        st.divider()
        st.subheader("📂 Struttura File Organizzata")
        
        st.markdown("""
        **L'applicazione organizza automaticamente i file in cartelle specifiche:**
        
        - **📁 `data/`** - Database SQLite (.db)
        - **⚙️ `config/`** - File di configurazione (.json)  
        - **📋 `logs/`** - File di log (.log)
        - **📦 `backups/`** - Backup database (.db, .json)
        - **📤 `exports/`** - Export dati (.json)
        """)
        
        # Show actual file counts
        try:
            files_info = FileManager.list_files_by_type()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**File presenti:**")
                for file_type, files in files_info.items():
                    icon_map = {
                        'databases': '💾',
                        'configs': '⚙️', 
                        'backups': '📦',
                        'exports': '📤',
                        'logs': '📋'
                    }
                    icon = icon_map.get(file_type, '📄')
                    st.write(f"{icon} {file_type.title()}: {len(files)} file(s)")
            
            with col2:
                st.markdown("**Percorsi cartelle:**")
                st.code(f"data/     - {FileManager.DATA_DIR}")
                st.code(f"config/   - {FileManager.CONFIG_DIR}")
                st.code(f"backups/  - {FileManager.BACKUPS_DIR}")
                st.code(f"exports/  - {FileManager.EXPORTS_DIR}")
                st.code(f"logs/     - {FileManager.LOGS_DIR}")
                
        except Exception as e:
            st.error(f"Errore lettura struttura file: {e}")
        
        # Migration info
        if st.button("🔄 Verifica e Organizza File"):
            try:
                moved_files = FileManager.migrate_existing_files()
                if moved_files:
                    st.success(f"✅ File organizzati: {', '.join(moved_files)}")
                else:
                    st.info("ℹ️ Tutti i file sono già organizzati correttamente")
            except Exception as e:
                st.error(f"❌ Errore organizzazione file: {e}")
        
        # Database configuration summary
        st.divider()
        st.subheader("📋 Riepilogo Configurazioni")
        
        configs = DatabaseRegistry.list_database_configs()
        if configs:
            config_data = []
            for config in configs:
                config_data.append({
                    'Nome': config['name'],
                    'Tipo': config['type'].upper(),
                    'Stato': '🟢 Attivo' if config['is_current'] else '⚫ Inattivo',
                    'Ultimo Uso': config.get('last_used', 'Mai')[:10] if config.get('last_used') else 'Mai',
                    'Creato': config.get('created_at', 'N/A')[:10] if config.get('created_at') else 'N/A'
                })
            
            st.dataframe(config_data, hide_index=True, use_container_width=True)
        else:
            st.info("Nessuna configurazione database salvata")

if __name__ == "__main__":
    main()