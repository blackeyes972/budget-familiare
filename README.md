# 💰 Budget Familiare Professional

<div align="center">

![Budget Familiare](https://img.shields.io/badge/Budget-Familiare-blue?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.13+-brightgreen?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=for-the-badge&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Una soluzione completa e moderna per la gestione intelligente delle finanze personali**

[🚀 Demo Live](#) • [📖 Documentazione](#documentazione) • [🐛 Report Bug](https://github.com/blackeyes972/budget-familiare/issues) • [💡 Feature Request](https://github.com/blackeyes972/budget-familiare/issues)

</div>

---

## 📋 Panoramica

Budget Familiare Professional è un'applicazione web avanzata sviluppata in Python che trasforma la gestione delle finanze personali in un'esperienza intuitiva e potente. Con un'interfaccia moderna e funzionalità professionali, permette di monitorare entrate, uscite e obiettivi finanziari con precisione e semplicità.

### ✨ Caratteristiche Principali

- 🎯 **Dashboard Intelligente** - Metriche adattive con selezione periodo dinamica
- 💾 **Database Multipli** - Supporto SQLite, PostgreSQL, MySQL con switch automatico
- 📊 **Analisi Avanzate** - Grafici interattivi e statistiche finanziarie dettagliate
- 🏷️ **Gestione Categorie** - Sistema di categorizzazione personalizzabile e intelligente
- 📱 **Design Responsive** - Interfaccia ottimizzata per desktop e mobile
- 🔄 **Import/Export** - Backup automatico e migrazione dati seamless
- 🎨 **UI Professionale** - Design moderno senza elementi tecnici visibili

---

## 🚀 Quick Start

### Prerequisiti

```bash
Python 3.13+
pip (Python package manager)
```

### Installazione Rapida

```bash
# Clona il repository
git clone https://github.com/blackeyes972/budget-familiare.git
cd budget-familiare

# Installa le dipendenze
pip install -r requirements.txt

# Avvia l'applicazione
streamlit run family_budget_app.py
```

### Prima Configurazione

1. **Avvia l'app** - L'interfaccia si aprirà automaticamente nel browser
2. **Configura il database** - Scegli tra SQLite (locale) o database remoto
3. **Aggiungi categorie** - Usa quelle predefinite o creane di personalizzate
4. **Inserisci transazioni** - Inizia a tracciare le tue finanze

---

## 📊 Demo e Screenshot

### Dashboard Principale
- Metriche finanziarie in tempo reale
- Selezione periodo da 30 giorni a 1 anno
- Grafici interattivi per analisi trend

### Gestione Transazioni
- Form intelligente con categorie dinamiche
- Filtri avanzati per data, tipo, categoria
- Export CSV per analisi esterne

### Database Management
- Configurazione multipli database
- Backup automatico e restore
- Migrazione dati senza perdite

---

## 🛠️ Tecnologie Utilizzate

### Core Framework
- **[Streamlit](https://streamlit.io/)** - Framework web principale
- **[SQLAlchemy](https://sqlalchemy.org/)** - ORM e gestione database
- **[Pandas](https://pandas.pydata.org/)** - Manipolazione e analisi dati

### Visualizzazione
- **[Plotly](https://plotly.com/)** - Grafici interattivi
- **CSS3** - Styling personalizzato
- **HTML5** - Struttura interfaccia

### Database Supportati
- **SQLite** - Database embedded (default)
- **PostgreSQL** - Database enterprise
- **MySQL** - Database web-oriented

### Librerie Aggiuntive
- **pathlib** - Gestione percorsi file
- **datetime** - Manipolazione date
- **json** - Serializzazione dati

---

## 📂 Struttura Progetto

```
budget-familiare/
├── 📄 family_budget_app.py     # Applicazione principale
├── 📄 database_config.py       # Gestione database multipli
├── 📄 categories.py           # Sistema categorie
├── 📄 models.py              # Modelli SQLAlchemy
├── 📄 create_demo_database.py # Script dati demo
├── 📄 requirements.txt       # Dipendenze Python
├── 📁 data/                  # Database SQLite
├── 📁 config/               # File configurazione
├── 📁 backups/              # Backup automatici
├── 📁 exports/              # Export dati
└── 📁 logs/                 # File di log
```

### Architettura Modulare

- **Data Access Layer (DAL)** - Gestione accesso dati
- **UI Components** - Componenti interfaccia riutilizzabili
- **Database Management** - Sistema multi-database
- **Category System** - Gestione categorie intelligente

---

## 💡 Funzionalità Avanzate

### 🎯 Dashboard Intelligente
```python
# Selezione periodo dinamica
- 30/60/90 giorni, 6 mesi, 1 anno
- Mese corrente, tutte le transazioni
- Metriche adattive con suggerimenti automatici
```

### 🔄 Gestione Database
```python
# Multi-database con switch automatico
- Configurazione SQLite, PostgreSQL, MySQL
- Migrazione dati senza perdite
- Backup automatico organizzato
```

### 📊 Analisi Finanziarie
```python
# Statistiche avanzate
- Tasso risparmio, rapporto spese
- Spesa media giornaliera
- Efficienza finanziaria
```

---

## 🚀 Utilizzo Avanzato

### Creazione Database Demo

```bash
# Genera database con 20 transazioni di esempio
python create_demo_database.py
```

### Configurazione Database Personalizzato

```python
# PostgreSQL
Host: localhost
Port: 5432
Database: budget_famiglia
User: budget_user
Password: your_password

# MySQL
Host: localhost  
Port: 3306
Database: budget_famiglia
User: budget_user
Password: your_password
```

### Export/Import Dati

```python
# Export automatico JSON
- Backup completo database
- Export selettivo per periodo
- Formato compatibile multi-database

# Import intelligente
- Risoluzione conflitti automatica
- Mappatura categorie
- Validazione dati
```

---

## 🤝 Contributi

I contributi sono benvenuti! Ecco come puoi aiutare:

### 🐛 Report Bug
1. Verifica che il bug non sia già segnalato
2. Apri una [nuova issue](https://github.com/blackeyes972/budget-familiare/issues)
3. Includi dettagli per riprodurre il problema

### 💡 Nuove Funzionalità
1. Apri una [feature request](https://github.com/blackeyes972/budget-familiare/issues)
2. Descrivi la funzionalità desiderata
3. Spiega il caso d'uso

### 🔧 Pull Request
1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

```
MIT License

Copyright (c) 2025 Alessandro Castaldi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 👨‍💻 Autore

<div align="center">

**Alessandro Castaldi**  
*Software Engineer & Full Stack Developer*

[![Email](https://img.shields.io/badge/Email-notifiche72@gmail.com-red?style=flat-square&logo=gmail)](mailto:notifiche72@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-blackeyes972-black?style=flat-square&logo=github)](https://github.com/blackeyes972)
[![Twitter](https://img.shields.io/badge/Twitter-@blackeyes972-blue?style=flat-square&logo=twitter)](https://x.com/blackeyes972)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Alessandro%20Castaldi-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/alessandro-castaldi-663846a5/)

</div>

---

## 🙏 Ringraziamenti

- **[Streamlit](https://streamlit.io/)** - Per il framework incredibile
- **[Plotly](https://plotly.com/)** - Per i grafici interattivi
- **[SQLAlchemy](https://sqlalchemy.org/)** - Per l'ORM potente e flessibile
- **Comunità Open Source** - Per l'ispirazione continua

---

## 📊 Statistiche Progetto

- **Linguaggio**: Python 3.13+
- **Linee di codice**: ~2000+
- **File principali**: 5
- **Database supportati**: 3
- **Grafici disponibili**: 4+
- **Categorie predefinite**: 18

---

## 🔮 Roadmap Futura

- [ ] **🔐 Autenticazione Multi-User** - Sistema login e gestione utenti
- [ ] **📱 App Mobile** - Versione React Native
- [ ] **🤖 AI Insights** - Analisi predittive con ML
- [ ] **🔔 Notifiche Smart** - Alert budget e promemoria
- [ ] **📊 Report Avanzati** - PDF e Excel export
- [ ] **🌐 API REST** - Integrazione servizi esterni
- [ ] **☁️ Cloud Sync** - Sincronizzazione multi-device

---

<div align="center">

### ⭐ Ti piace il progetto? Lascia una stella!

**Sviluppato con ❤️ da [Alessandro Castaldi](https://github.com/blackeyes972)**

[🔝 Torna su](#-budget-familiare-professional)

</div>