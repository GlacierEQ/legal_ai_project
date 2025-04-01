# Documentation Technique - Assistant Juridique IA

## Vue d'ensemble du projet

L'Assistant Juridique IA est une solution d'intelligence artificielle spécialisée dans le droit français, avec un focus initial sur le droit des affaires et fiscal. Cette application permet aux utilisateurs (avocats, comptables et particuliers) d'obtenir des réponses précises à leurs questions juridiques, basées sur les textes de loi officiels, la jurisprudence et la doctrine administrative française.

Le système utilise l'API Légifrance officielle pour accéder aux données juridiques, une base de données vectorielle pour la recherche sémantique, et des modèles de langage avancés pour générer des réponses adaptées au profil de l'utilisateur.

## Architecture du système

L'architecture du système est modulaire et suit une approche en couches :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                               Interface Utilisateur                         │
│                                                                             │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                                  API Backend                                │
│                                                                             │
└───────────┬─────────────────────────────┬─────────────────────────┬─────────┘
            │                             │                         │
            ▼                             ▼                         ▼
┌───────────────────┐         ┌───────────────────┐      ┌───────────────────┐
│                   │         │                   │      │                   │
│ Module Droit des  │         │  Module Droit     │      │ Module Paiement   │
│    Affaires       │         │    Fiscal         │      │ et Abonnement     │
│                   │         │                   │      │                   │
└─────────┬─────────┘         └─────────┬─────────┘      └─────────┬─────────┘
          │                             │                          │
          └─────────────────┬───────────┘                          │
                            │                                      │
                            ▼                                      ▼
          ┌─────────────────────────────┐              ┌───────────────────┐
          │                             │              │                   │
          │  Moteur de Recherche        │              │  Base de Données  │
          │  Sémantique (Pinecone)      │              │  PostgreSQL       │
          │                             │              │                   │
          └─────────────┬───────────────┘              └─────────┬─────────┘
                        │                                        │
                        ▼                                        ▼
          ┌─────────────────────────────┐              ┌───────────────────┐
          │                             │              │                   │
          │  Générateur de Réponses     │◄─────────────┤  Système de      │
          │  (LLM: Claude/GPT)          │              │  Logging/Audit   │
          │                             │              │                   │
          └─────────────────────────────┘              └───────────────────┘
```

### Composants principaux

1. **Collecteur de données juridiques** (`legifrance_collector.py`)
   - Se connecte à l'API Légifrance via PISTE
   - Extrait les textes juridiques pertinents pour le droit des affaires et fiscal
   - Stocke les données brutes dans un format structuré

2. **Processeur de textes juridiques** (`legifrance_processor.py`)
   - Nettoie et structure les textes juridiques
   - Extrait les métadonnées (dates, références, etc.)
   - Prépare les données pour l'indexation vectorielle

3. **Indexeur vectoriel** (`vector_indexer.py`)
   - Génère des embeddings pour les textes juridiques
   - Indexe les vecteurs dans Pinecone
   - Fournit des fonctionnalités de recherche sémantique spécialisées

4. **Générateur de réponses** (`response_generator.py`)
   - Utilise les résultats de recherche vectorielle
   - Génère des réponses juridiques précises via Claude ou GPT
   - Adapte les réponses selon le profil utilisateur

5. **Système d'authentification et paiement** (`auth_payment.py`)
   - Gère l'authentification des utilisateurs
   - Implémente les différents niveaux d'abonnement
   - Intègre Stripe pour la gestion des paiements

6. **Tests du système** (`test_system.py`)
   - Tests unitaires pour chaque composant
   - Tests d'intégration pour le flux complet
   - Tests de performance

## Flux de données

Le flux de données dans le système suit ces étapes :

1. **Collecte des données**
   - Extraction des codes juridiques (Commerce, Impôts)
   - Extraction des articles pertinents
   - Extraction de la jurisprudence

2. **Traitement des données**
   - Structuration des textes
   - Extraction des métadonnées
   - Création d'index pour la recherche

3. **Indexation vectorielle**
   - Découpage des textes en chunks
   - Génération d'embeddings
   - Indexation dans Pinecone

4. **Traitement des requêtes**
   - Détection du domaine juridique
   - Recherche sémantique
   - Génération de réponse avec citations

## Technologies utilisées

- **Backend**: Python 3.10 avec FastAPI
- **Base de données**: PostgreSQL pour les données structurées
- **Vectorisation**: Pinecone pour la base vectorielle
- **LLM**: API Claude/GPT avec fine-tuning sur corpus juridique français
- **Authentification**: JWT pour la gestion des tokens
- **Paiement**: Stripe pour la gestion des abonnements
- **Déploiement**: Docker et Kubernetes

## Configuration du système

Le système utilise plusieurs fichiers de configuration pour les différents composants :

- `.env.legifrance` : Configuration pour l'API Légifrance
- `.env.pinecone` : Configuration pour Pinecone
- `.env.llm` : Configuration pour les modèles de langage
- `.env.auth` : Configuration pour l'authentification et les paiements

## Installation et déploiement

### Prérequis

- Python 3.10+
- PostgreSQL
- Compte Pinecone
- Compte Stripe
- Compte PISTE (pour l'API Légifrance)
- Compte Claude ou OpenAI

### Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-organisation/assistant-juridique-ia.git
   cd assistant-juridique-ia
   ```

2. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   cp .env.legifrance.example .env.legifrance
   cp .env.pinecone.example .env.pinecone
   cp .env.llm.example .env.llm
   cp .env.auth.example .env.auth
   ```
   
   Éditer ces fichiers avec vos propres clés API et configurations.

5. Initialiser la base de données :
   ```bash
   python scripts/init_database.py
   ```

### Déploiement avec Docker

1. Construire l'image Docker :
   ```bash
   docker build -t assistant-juridique-ia .
   ```

2. Exécuter le conteneur :
   ```bash
   docker run -p 8000:8000 --env-file .env assistant-juridique-ia
   ```

### Déploiement avec Kubernetes

Des fichiers de configuration Kubernetes sont disponibles dans le répertoire `k8s/` pour un déploiement en production.

## API Reference

L'API REST expose les endpoints suivants :

### Authentification

- `POST /token` : Obtenir un token d'accès
- `POST /users/` : Créer un utilisateur
- `GET /users/me/` : Obtenir les informations de l'utilisateur actuel

### Abonnements

- `POST /subscriptions/` : Créer ou mettre à jour un abonnement
- `GET /subscriptions/me/` : Obtenir les informations de l'abonnement
- `DELETE /subscriptions/me/` : Annuler l'abonnement

### Requêtes juridiques

- `POST /queries/` : Créer une requête juridique
- `GET /queries/` : Obtenir l'historique des requêtes
- `GET /queries/stats/` : Obtenir les statistiques des requêtes

### Webhook

- `POST /webhook/stripe/` : Webhook pour les événements Stripe

## Modèle de données

### Utilisateur

```
User
- id: Integer (PK)
- email: String (unique)
- hashed_password: String
- full_name: String
- is_active: Boolean
- is_admin: Boolean
- created_at: DateTime
```

### Abonnement

```
Subscription
- id: Integer (PK)
- user_id: Integer (FK)
- stripe_customer_id: String
- stripe_subscription_id: String
- plan_type: String ("freemium", "standard", "pro")
- is_active: Boolean
- start_date: DateTime
- end_date: DateTime
- queries_limit: Integer
- queries_used: Integer
```

### Requête

```
Query
- id: Integer (PK)
- user_id: Integer (FK)
- query_text: String
- domain: String ("business", "tax")
- timestamp: DateTime
```

## Plans d'abonnement

Le système propose trois niveaux d'abonnement :

1. **Freemium**
   - Gratuit
   - 10 requêtes par mois
   - Domaines juridiques limités

2. **Standard**
   - 19,99 € par mois
   - 100 requêtes par mois
   - Tous les domaines juridiques

3. **Pro**
   - 49,99 € par mois
   - 1000 requêtes par mois
   - Tous les domaines juridiques
   - Priorité dans le traitement des requêtes

## Maintenance et mise à jour

### Mise à jour des données juridiques

Les données juridiques doivent être mises à jour régulièrement pour refléter les changements législatifs. Un script de mise à jour est disponible :

```bash
python scripts/update_legal_data.py
```

Ce script peut être programmé pour s'exécuter périodiquement via cron ou un autre planificateur.

### Surveillance du système

Le système génère des logs détaillés pour chaque composant. Ces logs peuvent être consultés pour surveiller le fonctionnement du système et diagnostiquer les problèmes.

## Limitations connues

- Le système est actuellement limité au droit des affaires et fiscal français.
- Les réponses générées doivent être vérifiées par un professionnel du droit.
- L'API Légifrance a des quotas de requêtes qui peuvent limiter la fréquence des mises à jour.

## Roadmap future

- Extension à d'autres domaines du droit français
- Intégration de sources de données supplémentaires
- Amélioration de la précision des réponses via fine-tuning spécifique
- Interface utilisateur web et mobile
- Fonctionnalités de collaboration pour les cabinets d'avocats

## Licence et mentions légales

Ce projet est soumis aux conditions de la licence spécifiée dans le fichier LICENSE.

Les données juridiques sont soumises à la licence ouverte 2.0 de Légifrance.

**Avertissement** : Les réponses générées par l'assistant juridique IA ne constituent pas un avis juridique professionnel. Pour des conseils juridiques personnalisés, veuillez consulter un avocat ou un professionnel du droit qualifié.
