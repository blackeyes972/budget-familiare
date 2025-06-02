# 📖 Manuale d'Uso - Budget Familiare Professional

<div align="center">

**Guida completa per utilizzare al meglio la tua app di gestione finanziaria**

*Versione 2.0 - Giugno 2025*

</div>

---

## 🚀 Primi Passi

### 📥 Installazione e Avvio

1. **Scarica l'applicazione**
   ```bash
   git clone https://github.com/blackeyes972/budget-familiare.git
   cd budget-familiare
   ```

2. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

3. **Avvia l'app**
   ```bash
   streamlit run family_budget_app.py
   ```

4. **Apri nel browser**
   - L'app si aprirà automaticamente su `http://localhost:8501`
   - Se non si apre, copia l'indirizzo dalla console

### 🏗️ Prima Configurazione

**Al primo avvio vedrai la schermata di setup:**

1. **Scegli il tipo di database**
   - 📁 **SQLite** (raccomandato per iniziare): Database locale, zero configurazione
   - 🐘 **PostgreSQL**: Per uso avanzato con analytics
   - 🐬 **MySQL**: Per deployment cloud

2. **Configurazione SQLite** (opzione più semplice)
   - Nome configurazione: `Il Mio Budget`
   - Nome file database: `budget_famiglia` (viene creato automaticamente)
   - Clicca **"🚀 Crea Database"**

3. **Conferma setup**
   - L'app creerà automaticamente la struttura cartelle
   - Verranno installate 18 categorie predefinite
   - Sarai pronto per iniziare!

---

## 🧭 Navigazione Principale

### 📱 Layout Interfaccia

L'app è organizzata in **3 sezioni principali** nel menu laterale:

#### 📊 **Analisi e Dati**
- **📊 Dashboard**: Panoramica generale con metriche e grafici
- **📈 Report Mensili**: Analisi dettagliate per mese

#### 💼 **Gestione Operativa**  
- **💳 Nuova Transazione**: Aggiungi entrate e uscite
- **📋 Lista Transazioni**: Visualizza e filtra tutte le transazioni
- **🏷️ Gestione Categorie**: Personalizza categorie e icone

#### ⚙️ **Sistema e Configurazione**
- **🗄️ Gestione Database**: Configura e gestisci database
- **⚙️ Impostazioni**: Opzioni applicazione
- **🏆 Credits**: Informazioni sviluppatore

### 🎯 Quick Stats (Sidebar)

Nel menu laterale trovi sempre:
- **💰 Saldo attuale** (ultimi 30 giorni o totale)
- **📝 Numero transazioni** nel periodo
- **🗄️ Database attivo** con informazioni
- **📁 File system** con contatori
- **🔄 Switch rapido** tra database configurati

---

## 💳 Gestire le Transazioni

### ➕ Aggiungere una Nuova Transazione

1. **Vai su "💳 Nuova Transazione"**

2. **Scegli il tipo**
   - **Entrata**: Stipendi, freelance, investimenti, bonus
   - **Uscita**: Spese di ogni tipo

3. **Compila il form**
   - **Categoria**: Scegli dalla lista (si aggiorna automaticamente per tipo)
   - **Importo**: In euro (es. 25.50)
   - **Data**: Default oggi, modificabile
   - **Descrizione**: Obbligatoria (es. "Spesa supermercato")
   - **Ricorrenza**: Nessuna, Mensile, Settimanale, Annuale
   - **Tag**: Opzionali, separati da virgola (es. "urgente, casa")
   - **Note**: Campo libero per dettagli

4. **Salva**
   - Clicca **"💾 Aggiungi Transazione"**
   - Vedrai conferma di successo
   - Il form si resetterà automaticamente

### 📋 Visualizzare le Transazioni

1. **Vai su "📋 Lista Transazioni"**

2. **Usa i filtri**
   - **Tipo**: Tutti, Entrata, Uscita
   - **Periodo**: Tutte le date, Ultimi 30/90 giorni, Personalizzato
   - **Categoria**: Filtra per categoria specifica

3. **Analizza le statistiche**
   - **Metriche automatiche** mostrate sopra la tabella
   - **Totali per tipo** se visualizzi "Tutti"
   - **Saldo netto** e percentuali

4. **Esporta i dati**
   - Clicca **"📥 Esporta CSV"**
   - Scarica il file per analisi esterne

---

## 📊 Dashboard Intelligente

### 🎯 Panoramica Principale

1. **Vai su "📊 Dashboard"**

2. **Seleziona il periodo**
   - L'app suggerisce automaticamente il periodo più significativo
   - Opzioni: 30/60/90 giorni, 6 mesi, 1 anno, mese corrente, tutte

3. **Analizza le metriche**
   - **💰 Entrate**: Totale entrate periodo
   - **💸 Uscite**: Totale uscite periodo  
   - **💵 Saldo**: Differenza (verde = positivo, rosso = negativo)
   - **📝 Transazioni**: Numero totale

4. **Metriche avanzate** (se disponibili)
   - **📈 Importo Medio**: Per transazione
   - **💾 Tasso Risparmio**: Percentuale risparmiata
   - **📊 Spesa Media/Giorno**: Stima giornaliera
   - **⚖️ Rapporto Spese**: Uscite su entrate

### 📈 Grafici Interattivi

1. **Trend Mensile**
   - Grafico linee entrate vs uscite
   - Mostra evoluzione negli ultimi 6 mesi
   - Interattivo: passa il mouse per dettagli

2. **Analisi Categorie**
   - **Torta uscite**: Distribuzione spese per categoria
   - **Top 5 categorie**: Classifica spese maggiori
   - Colori personalizzati per categoria

---

## 📈 Report Mensili Avanzati

### 🔍 Analisi Dettagliata

1. **Vai su "📈 Report Mensili"**

2. **Seleziona mese e anno**
   - Default: mese corrente
   - Indicazioni: corrente, passato, futuro
   - Info transazioni disponibili

3. **Esplora le 5 sezioni**

#### 📊 **Panoramica**
- **Riepilogo esecutivo** con trend vs mese precedente
- **Grafico bilancio** entrate/uscite (torta)
- **Trend giornaliero** del mese (linee)
- **Statistiche dettagliate** con giorni attivi

#### 📈 **Trend & Confronti**
- **Grafico 6 mesi** con trend entrate/uscite/saldo
- **Tabella confronti** con variazioni percentuali
- **Analisi comparative** automatiche

#### 🏷️ **Analisi Categorie**
- **Distribuzione uscite** per categoria (torta)
- **Distribuzione entrate** per categoria (torta)
- **Top 10 spese** del mese con dettagli
- **Grafico barre** confronto categorie

#### 💡 **Insights**
- **Suggerimenti automatici** generati dall'AI
- **Pattern di spesa** per giorno settimana
- **Raccomandazioni personalizzate** per ottimizzazione
- **Analisi comportamenti** finanziari

#### 📤 **Export**
- **Selezione sezioni** da includere nel report
- **Export JSON** completo con metadata
- **Export CSV** transazioni del mese
- **Anteprima** contenuto prima del download

### 🧠 Comprendere gli Insights

L'app genera automaticamente insights come:
- **💚 Saldo positivo**: "Ottimo! Hai risparmiato €500 questo mese"
- **📈 Miglioramento**: "Il tuo saldo è migliorato di €200 rispetto al mese scorso"
- **🌟 Efficienza**: "Eccellente controllo delle spese! Hai risparmiato il 25% delle entrate"
- **⚠️ Alert**: "Attenzione: hai speso più delle tue entrate"

---

## 🏷️ Gestione Categorie

### 👀 Visualizzare Categorie

1. **Vai su "🏷️ Gestione Categorie"**

2. **Statistiche overview**
   - Totale categorie, attive, per entrate/uscite
   - Warning su categorie non utilizzate

3. **Categorie per tipo**
   - **Entrate**: Es. 💼 Stipendio, 💻 Freelance
   - **Uscite**: Es. 🏠 Casa, 🛒 Alimentari

### ➕ Aggiungere Nuove Categorie

1. **Scegli il tipo** (Entrata o Uscita)

2. **Inserisci nome categoria**
   - Es. "Palestra", "Consulenze", "Benzina"
   - Il sistema suggerirà automaticamente icone correlate

3. **Seleziona icona**
   - **💡 Suggerimenti automatici** basati sul nome
   - **🔍 Ricerca per parola chiave** (es. "casa", "cibo")
   - **📂 Sfoglia per categoria** (1000+ icone disponibili)
   - **⭐ Icone comuni** sempre disponibili

4. **Scegli colore**
   - Color picker per personalizzazione
   - Default blu #3498db

5. **Anteprima e salva**
   - Vedi anteprima categoria prima di salvare
   - Clicca **"✅ Aggiungi Categoria"**

### 🎨 Tips per Icone

- **Usa parole chiave**: "auto" suggerisce 🚗, "casa" suggerisce 🏠
- **Cerca per attività**: "sport" → ⚽🏃‍♂️🏋️‍♀️
- **Pensa al contesto**: "shopping" → 🛒🛍️👕
- **Usa emoji semplici**: Più riconoscibili e universali

---

## 🗄️ Gestione Database

### 📊 Informazioni Database Corrente

1. **Vai su "🗄️ Gestione Database"**

2. **Tab "📊 Info Corrente"**
   - Nome e tipo database attivo
   - Statistiche: transazioni, categorie, budget, goals
   - Dimensione file (per SQLite)
   - Funzionalità disponibili

### 🆕 Creare Nuovo Database

1. **Tab "🆕 Crea Nuovo"**

2. **Configura database**
   - **Nome**: Es. "Budget Lavoro", "Finanze Casa"
   - **Tipo**: SQLite, PostgreSQL, MySQL
   - **Parametri**: Dipendono dal tipo scelto

3. **Testa connessione**
   - Clicca **"🔍 Testa Connessione"**
   - Verifica che tutto funzioni

4. **Crea e attiva**
   - Clicca **"🚀 Crea Database"**
   - Il nuovo database diventerà attivo automaticamente

### 🔄 Cambiare Database

1. **Tab "📚 Database Lista"**

2. **Seleziona database**
   - Vedi tutti i database configurati
   - **🟢 Attivo** = database corrente
   - **⚫ Inattivo** = disponibile per switch

3. **Switch automatico**
   - Clicca **"🔄 Passa a [Nome]"**
   - L'app migrerà automaticamente i dati
   - Il nuovo database diventerà attivo

### 🛠️ Operazioni Avanzate

1. **Tab "🛠️ Operazioni"**

2. **Reset Database**
   - ⚠️ **ATTENZIONE**: Elimina tutti i dati!
   - Utile per ricominciare da capo
   - Conferma richiesta per sicurezza

3. **Export Completo**
   - Esporta tutti i dati in JSON
   - Include transazioni, categorie, configurazioni
   - File salvato in cartella `exports/`

4. **Import Dati**
   - Carica file JSON precedentemente esportato
   - Risoluzione automatica conflitti
   - Merge intelligente dati esistenti

---

## 📁 Gestione File

### 🗂️ Struttura File Automatica

L'app organizza automaticamente i file in cartelle:

- **📁 data/**: Database SQLite
- **⚙️ config/**: Configurazioni database
- **📦 backups/**: Backup automatici
- **📤 exports/**: Report ed export dati
- **📋 logs/**: File di log sistema

### 📦 Backup e Pulizia

1. **Tab "📁 Gestione File"**

2. **Visualizza file**
   - Tutti i file organizzati per tipo
   - Dimensioni e date modifiche
   - Azioni disponibili per tipo

3. **Download file**
   - **📥 Download** per JSON/config
   - File vengono scaricati dal browser

4. **Pulizia automatica**
   - **🧹 Pulisci File Vecchi**: Elimina file più vecchi di X giorni
   - **📊 Statistiche Spazio**: Mostra spazio utilizzato totale

### 💾 Backup Manuale

**Per backup completo:**
1. Vai su **"🗄️ Gestione Database"** → **"🛠️ Operazioni"**
2. Clicca **"📊 Export JSON"**
3. Salva il file in luogo sicuro
4. Per ripristinare: usa **"📥 Import Dati"**

---

## 💡 Tips e Best Practices

### 🎯 Uso Efficace

**📝 Inserimento Transazioni**
- Inserisci transazioni regolarmente (giornalmente o settimanalmente)
- Usa descrizioni chiare: "Spesa Esselunga" invece di "Spesa"
- Sfrutta i tag per raggruppamenti: "casa", "urgente", "deducibile"

**🏷️ Categorie Smart**
- Inizia con le categorie predefinite
- Aggiungi nuove categorie solo quando necessario
- Usa icone riconoscibili e colori coerenti

**📊 Analisi Periodica**
- Controlla la dashboard settimanalmente
- Usa i report mensili per analisi approfondite
- Segui i suggerimenti degli insights automatici

### ⚡ Scorciatoie Utili

**🚀 Navigazione Rapida**
- Usa i pulsanti **"Switch Rapido"** nella sidebar
- Il **"Dashboard Rapido"** mostra sempre info essenziali
- I separatori nel menu aiutano l'orientamento

**📊 Filtri Smart**
- Dashboard: L'app sceglie automaticamente il periodo più significativo
- Transazioni: Inizia con "Ultimi 30 giorni" per panoramica recente
- Report: Usa il mese corrente per monitoraggio continuo

**🎨 Personalizzazione**
- Colori categorie: Usa schema coerente (es. rosso=spese obbligatorie, blu=discrezionali)
- Icone: Preferisci emoji universali a simboli complessi
- Nomi: Brevi ma descrittivi

### 🔧 Risoluzione Problemi

**❓ L'app non si avvia?**
```bash
# Verifica dipendenze
pip install -r requirements.txt

# Riavvia
streamlit run family_budget_app.py
```

**❓ Database non trovato?**
- Vai su "🗄️ Gestione Database"
- Controlla database attivo in sidebar
- Se necessario, crea nuovo database

**❓ Dati non visualizzati?**
- Verifica filtri data nelle sezioni
- Prova "Tutte le transazioni" come periodo
- Controlla di aver inserito transazioni nel periodo

**❓ Errori export/import?**
- Verifica formato file JSON
- Usa file esportati dall'app stessa
- Controlla permessi cartelle

---

## 🎓 Esempi Pratici

### 📋 Scenario 1: Famiglia con Budget Mensile

**Setup Iniziale:**
1. Crea database "Budget Famiglia"
2. Categorie personalizzate: 🧒 "Bambini", 🐕 "Animali", 🏥 "Assicurazioni"

**Uso Quotidiano:**
- Mattina: Inserisci spese giorno precedente
- Fine settimana: Controlla dashboard
- Fine mese: Analizza report mensile

**Insights Tipici:**
- "Hai speso il 15% in più per 🛒 Alimentari questo mese"
- "La tua spesa media giornaliera è €45"
- "Excellent! Hai risparmiato il 20% delle entrate"

### 💼 Scenario 2: Freelancer Multi-Progetto

**Setup Avanzato:**
1. Database PostgreSQL per analytics avanzate
2. Categorie entrate: 💻 "Cliente A", 🎨 "Cliente B", 📝 "Copywriting"
3. Tag per progetti: "progetto-x", "urgente", "ricorrente"

**Workflow:**
- Ad ogni pagamento: inserisci entrata con tag progetto
- Settimanale: usa filtri per analizzare per cliente
- Mensile: export CSV per commercialista

**Analytics Utili:**
- Report mensili per vedere trend clienti
- Filtri per tag per analisi progetto
- Export per gestione fiscale

### 🎯 Scenario 3: Pianificazione Obiettivi

**Obiettivo: Risparmiare €5000 per vacanza**

**Strategy:**
1. Monitora tasso risparmio mensile
2. Usa insights per identificare aree ottimizzazione
3. Confronta mesi per vedere progressi

**Tracking:**
- Dashboard: Verifica saldo positivo costante
- Report: Analizza trend risparmio
- Insights: "Tasso risparmio attuale: 25% - Obiettivo raggiungibile!"

---

## 🆘 Supporto

### 📞 Quando Hai Bisogno di Aiuto

**🐛 Bug o Errori:**
- [GitHub Issues](https://github.com/blackeyes972/budget-familiare/issues)
- Includi: passi per riprodurre, screenshot, versione Python

**💡 Richieste Funzionalità:**
- [GitHub Discussions](https://github.com/blackeyes972/budget-familiare/discussions)
- Descrivi caso d'uso e benefici

**📧 Contatto Diretto:**
- Email: [notifiche72@gmail.com](mailto:notifiche72@gmail.com)
- Per supporto personalizzato e consulenze

### 📚 Risorse Aggiuntive

- **📖 README**: Documentazione tecnica completa
- **🏆 Credits**: Informazioni sviluppatore e tecnologie
- **🔮 Roadmap**: Funzionalità future in sviluppo

---

<div align="center">

**🎯 Ora sei pronto per gestire le tue finanze come un professionista!**

*Se questo manuale ti è stato utile, lascia una ⭐ su GitHub!*

**📅 Versione Manuale**: 2.0 | **🗓️ Ultimo Aggiornamento**: Dicembre 2024

[🔝 Torna all'inizio](#-manuale-duso---budget-familiare-professional)

</div>