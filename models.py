# models.py
"""
Modelli SQLAlchemy per il database dell'applicazione Budget Familiare.
Definisce la struttura delle tabelle e le relazioni.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Category(Base):
    """Modello per le categorie delle transazioni"""
    __tablename__ = 'categories'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Basic info
    name = Column(String(100), nullable=False, unique=True)
    transaction_type = Column(String(20), nullable=False)  # 'Entrata' or 'Uscita'
    color = Column(String(7), default='#3498db')  # Hex color
    icon = Column(String(50), default='💰')  # Emoji icon
    is_active = Column(Boolean, default=True)
    
    # Metadata as JSON string (compatible with all databases)
    metadata_json = Column(Text, default='{}')
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.transaction_type}')>"


class Transaction(Base):
    """Modello per le transazioni finanziarie"""
    __tablename__ = 'transactions'
    
    # Primary key (UUID as string for compatibility)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Transaction data
    date = Column(DateTime, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=False)
    notes = Column(Text)
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False, index=True)
    
    # Transaction metadata
    transaction_type = Column(String(20), nullable=False, index=True)  # 'Entrata' or 'Uscita'
    recurrence_type = Column(String(20), default='Nessuna')  # 'Nessuna', 'Mensile', 'Settimanale', 'Annuale'
    
    # Tags as comma-separated string (compatible with all databases)
    tags = Column(String(500), default='')
    
    # Additional metadata as JSON string
    metadata_json = Column(Text, default='{}')
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", backref="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, description='{self.description[:30]}...')>"
    
    @property
    def tags_list(self):
        """Restituisce i tag come lista"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    @tags_list.setter
    def tags_list(self, tags):
        """Imposta i tag da una lista"""
        self.tags = ','.join(tags) if tags else ''


class Budget(Base):
    """Modello per i budget mensili per categoria"""
    __tablename__ = 'budgets'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Budget data
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    monthly_limit = Column(Float, nullable=False)
    alert_threshold = Column(Float, default=0.8)  # Percentage (0.8 = 80%)
    
    # Time period
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata for notifications and settings
    metadata_json = Column(Text, default='{}')
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", backref="budgets")
    
    def __repr__(self):
        return f"<Budget(id={self.id}, category_id={self.category_id}, limit={self.monthly_limit}, {self.year}/{self.month})>"


class Goal(Base):
    """Modello per gli obiettivi di risparmio"""
    __tablename__ = 'goals'
    
    # Primary key (UUID as string)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Goal data
    name = Column(String(200), nullable=False)
    description = Column(Text)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(DateTime)
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Goal type and priority
    goal_type = Column(String(50), default='savings')  # 'savings', 'debt_payoff', 'investment', 'purchase'
    priority = Column(Integer, default=2)  # 1=high, 2=medium, 3=low
    
    # Metadata for additional settings
    metadata_json = Column(Text, default='{}')
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Goal(id={self.id}, name='{self.name}', target={self.target_amount}, current={self.current_amount})>"
    
    @property
    def progress_percentage(self):
        """Calcola la percentuale di completamento"""
        if self.target_amount <= 0:
            return 0
        return min(100, (self.current_amount / self.target_amount) * 100)
    
    @property
    def remaining_amount(self):
        """Calcola l'importo rimanente"""
        return max(0, self.target_amount - self.current_amount)


class RecurringTransaction(Base):
    """Modello per le transazioni ricorrenti (template)"""
    __tablename__ = 'recurring_transactions'
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Template data
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    
    # Recurrence settings
    recurrence_type = Column(String(20), nullable=False)  # 'Mensile', 'Settimanale', 'Annuale'
    recurrence_day = Column(Integer)  # Day of month for monthly, day of week for weekly
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    
    # Metadata
    transaction_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Next execution
    next_execution = Column(DateTime)
    last_execution = Column(DateTime)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", backref="recurring_transactions")
    
    def __repr__(self):
        return f"<RecurringTransaction(id={self.id}, name='{self.name}', type='{self.recurrence_type}')>"


class Account(Base):
    """Modello per i conti bancari/portafogli"""
    __tablename__ = 'accounts'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Account data
    name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # 'checking', 'savings', 'credit_card', 'cash', 'investment'
    currency = Column(String(3), default='EUR')
    
    # Balance
    initial_balance = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    
    # Settings
    is_active = Column(Boolean, default=True)
    include_in_totals = Column(Boolean, default=True)
    
    # Bank info (optional)
    bank_name = Column(String(100))
    account_number_last4 = Column(String(4))  # Only last 4 digits for security
    
    # Colors and icons
    color = Column(String(7), default='#3498db')
    icon = Column(String(50), default='🏦')
    
    # Metadata
    metadata_json = Column(Text, default='{}')
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', type='{self.account_type}', balance={self.current_balance})>"


# Future extensions can add:
# - TransactionAccount (linking transactions to specific accounts)
# - Tag model (for better tag management)
# - Report model (for saved custom reports)
# - Notification model (for alerts and reminders)
# - User model (for multi-user support)