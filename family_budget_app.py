import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import json
import os

# Import moduli personalizzati
from database_config import (
    DatabaseConfig, DatabaseManager, DatabaseSwitcher, DatabaseRegistry, FileManager,
    get_database_manager, set_database_manager, check_first_run
)
from categories import DefaultCategories, CategoryManager
from models import Transaction, Category, Budget, Goal

# =============================================================================
# UI CUSTOMIZATION & BRANDING
# =============================================================================

def apply_custom_styling():
    """Applica styling personalizzato per un look professionale"""
    custom_css = """
    <style>
        /* Nasconde elementi Streamlit per look professionale */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        .stDecoration {display: none;}
        
        /* Mantiene il menu hamburger per funzionalità fullscreen */
        [data-testid="collapsedControl"] {visibility: visible !important;}
        
        /* Styling per l'header personalizzato */
        .custom-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .custom-header h1 {
            color: white;
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .custom-header .subtitle {
            color: #e8f4fd;
            margin: 0;
            font-size: 1.1rem;
            font-weight: 300;
            opacity: 0.9;
        }
        
        /* Styling per metriche dashboard */
        .metric-container {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        
        /* Footer autore personalizzato */
        .author-footer {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-top: 3rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .author-footer h3 {
            margin-bottom: 1rem;
            color: white;
            font-size: 1.5rem;
        }
        
        .author-links {
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        
        .author-link {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            padding: 0.5rem 1rem;
            text-decoration: none;
            color: white;
            font-weight: 500;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .author-link:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .custom-header h1 {
                font-size: 2rem;
            }
            .author-links {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_custom_header():
    """Renderizza header personalizzato con branding"""
    header_html = """
    <div class="custom-header">
        <h1>💰 Budget Familiare Professional</h1>
        <p class="subtitle">Gestione Intelligente delle Finanze Personali | Sviluppato da Alessandro Castaldi</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_author_info():
    """Renderizza informazioni sull'autore nella sezione impostazioni"""
    st.subheader("👨‍💻 Informazioni Sviluppatore")
    
    # CSS semplificato compatibile con Streamlit
    st.markdown("""
    <style>
    .author-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    .author-card h3 {
        color: white !important;
        margin-bottom: 1rem;
    }
    .author-card p {
        color: rgba(255,255,255,0.9) !important;
        margin-bottom: 1.5rem;
    }
    .social-link {
        display: inline-block;
        margin: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        color: white !important;
        text-decoration: none;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .social-link:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenuto principale con HTML semplificato
    st.markdown("""
    <div class="author-card">
        <h3>🚀 Sviluppato da Alessandro Castaldi</h3>
        <p>Software Engineer appassionato di tecnologie innovative e sviluppo di applicazioni web</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Link social con layout Streamlit nativo
    st.markdown("### 🔗 Contatti")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <a href="mailto:notifiche72@gmail.com" class="social-link" target="_blank">
            📧 Email
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <a href="https://github.com/blackeyes972" class="social-link" target="_blank">
            🐙 GitHub
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <a href="https://x.com/blackeyes972" class="social-link" target="_blank">
            🐦 Twitter
        </a>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <a href="https://www.linkedin.com/in/alessandro-castaldi-663846a5/" class="social-link" target="_blank">
            💼 LinkedIn
        </a>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("---")
    st.info("⭐ Ti piace questo progetto? Lascia una stella su GitHub!")
    
    # Informazioni aggiuntive
    with st.expander("📋 Dettagli Tecnici"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            **🛠️ Tecnologie utilizzate:**
            - Python 3.13+
            - Streamlit 
            - SQLAlchemy
            - Plotly
            - Pandas
            """)
        
        with col_b:
            st.markdown("""
            **📊 Caratteristiche:**
            - Database multipli
            - Export/Import dati
            - Grafici interattivi
            - Gestione categorie
            - Analisi finanziarie
            """)

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
                    'transactions_count': count
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
        page_title="Budget Familiare Professional",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styling immediately
    apply_custom_styling()
    
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
        render_custom_header()
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
    
    # Render custom header instead of default title
    render_custom_header()
    
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
                        st.color_picker("", value=cat['color'], key=f"color_view_{cat['id']}", disabled=True)
            
            # Add new category
            with st.expander(f"➕ Aggiungi Categoria {trans_type}"):
                with st.form(f"new_category_{trans_type}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Nome categoria")
                        new_icon = st.text_input("Icona", value="💰")
                    
                    with col2:
                        new_color = st.color_picker("Colore", value="#3498db")
                    
                    if st.form_submit_button(f"Aggiungi {trans_type}"):
                        if new_name:
                            full_name = f"{new_icon} {new_name}" if not new_name.startswith(new_icon) else new_name
                            if category_manager.add_category(full_name, trans_type, new_color, new_icon):
                                st.success(f"✅ Categoria '{new_name}' aggiunta!")
                                st.rerun()
        
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
        
        # App Settings Tab
        tab1, tab2, tab3 = st.tabs(["🎨 Interfaccia", "📂 File & Database", "👨‍💻 Info Sviluppatore"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎨 Aspetto")
                st.selectbox("Tema", ["Light", "Dark"], disabled=True)
                st.selectbox("Lingua", ["Italiano", "English"], disabled=True)
                st.selectbox("Valuta", ["EUR (€)", "USD ($)", "GBP (£)"], disabled=True)
                
            with col2:
                st.subheader("🔔 Notifiche")
                st.checkbox("Avvisi budget", disabled=True)
                st.checkbox("Promemoria transazioni ricorrenti", disabled=True)
                st.checkbox("Report mensili", disabled=True)
            
            st.info("🚧 Impostazioni interfaccia in sviluppo - funzionalità in arrivo!")
        
        with tab2:
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
            st.subheader("📋 Riepilogo Configurazioni Database")
            
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
        
        with tab3:
            render_author_info()

if __name__ == "__main__":
    main()