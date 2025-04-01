# Guide de Déploiement Local - Assistant Juridique IA

Ce guide vous explique comment déployer et exécuter l'Assistant Juridique IA sur votre machine locale en utilisant Docker Compose.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants sur votre système :

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads) (optionnel, pour cloner le dépôt)

## Étape 1 : Préparation de l'environnement

1. Clonez le dépôt (ou utilisez les fichiers que vous avez déjà) :
   ```bash
   git clone https://github.com/votre-organisation/assistant-juridique-ia.git
   cd assistant-juridique-ia
   ```

2. Créez un fichier `.env` à la racine du projet pour configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   ```

3. Modifiez le fichier `.env` avec vos propres clés API et configurations :
   ```
   # Configuration JWT
   JWT_SECRET_KEY=votre_cle_secrete_jwt
   
   # Configuration API Légifrance (optionnel pour le développement initial)
   LEGIFRANCE_API_KEY=votre_api_key_legifrance
   LEGIFRANCE_API_SECRET=votre_api_secret_legifrance
   
   # Configuration Pinecone
   PINECONE_API_KEY=votre_api_key_pinecone
   PINECONE_ENVIRONMENT=gcp-starter
   PINECONE_INDEX_NAME=legal-assistant
   
   # Configuration LLM
   ANTHROPIC_API_KEY=votre_api_key_anthropic
   # OU
   OPENAI_API_KEY=votre_api_key_openai
   
   # Configuration Stripe
   STRIPE_API_KEY=votre_cle_api_stripe
   STRIPE_WEBHOOK_SECRET=votre_cle_secrete_webhook_stripe
   ```

## Étape 2 : Création des dossiers de données

Créez les dossiers nécessaires pour stocker les données :

```bash
mkdir -p data/raw data/processed data/logs
```

## Étape 3 : Démarrage des services

Lancez l'application avec Docker Compose :

```bash
docker-compose up -d
```

Cette commande va :
1. Construire les images Docker pour l'API et le frontend
2. Démarrer la base de données PostgreSQL
3. Démarrer l'API backend
4. Démarrer le frontend React

## Étape 4 : Initialisation des données (optionnel)

Si vous souhaitez initialiser la base de données avec des données juridiques, exécutez :

```bash
docker-compose --profile data_collection up data_collector
```

Puis, pour indexer ces données dans Pinecone :

```bash
docker-compose --profile data_collection up vector_indexer
```

**Note** : Cette étape nécessite des clés API valides pour Légifrance et Pinecone.

## Étape 5 : Accès à l'application

Une fois tous les services démarrés, vous pouvez accéder à l'application :

- **Frontend** : http://localhost:3000
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## Structure des services

Le déploiement comprend les services suivants :

1. **postgres** : Base de données PostgreSQL pour stocker les utilisateurs, abonnements et historique des requêtes
2. **api** : Backend FastAPI qui expose les endpoints REST
3. **frontend** : Interface utilisateur React
4. **data_collector** : Service pour collecter les données juridiques (exécution ponctuelle)
5. **vector_indexer** : Service pour indexer les données dans Pinecone (exécution ponctuelle)

## Commandes utiles

### Voir les logs des services

```bash
# Tous les services
docker-compose logs

# Un service spécifique
docker-compose logs api
docker-compose logs frontend
```

### Redémarrer un service

```bash
docker-compose restart api
```

### Arrêter tous les services

```bash
docker-compose down
```

### Reconstruire les images après modifications

```bash
docker-compose build
```

## Développement sans Docker

Si vous préférez développer sans Docker, vous pouvez suivre ces étapes :

### Backend (FastAPI)

1. Créez un environnement virtuel Python :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez les variables d'environnement (voir le fichier `.env.example`)

4. Lancez l'API :
   ```bash
   cd app
   uvicorn main:app --reload
   ```

### Frontend (React)

1. Installez les dépendances :
   ```bash
   cd frontend
   npm install
   ```

2. Créez un fichier `.env.local` avec :
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

3. Lancez le serveur de développement :
   ```bash
   npm start
   ```

## Dépannage

### Problème de connexion à la base de données

Si l'API ne peut pas se connecter à PostgreSQL, vérifiez que :
- Le service PostgreSQL est bien démarré
- Les variables d'environnement de connexion sont correctes
- Le réseau Docker fonctionne correctement

### Problème d'accès à l'API depuis le frontend

Si le frontend ne peut pas communiquer avec l'API, vérifiez :
- Que l'API est bien démarrée et accessible
- Que la configuration CORS dans l'API autorise les requêtes du frontend
- Que l'URL de l'API est correctement configurée dans le frontend

### Problème avec les services de données

Si les services de collecte ou d'indexation échouent :
- Vérifiez que les clés API sont valides et correctement configurées
- Consultez les logs pour plus de détails sur l'erreur

## Remarques importantes

1. **Données juridiques** : Le dossier `data` est initialement vide car il est destiné à être rempli par le script de collecte de données. Vous pouvez soit exécuter ce script avec une clé API Légifrance valide, soit utiliser vos propres données de test.

2. **Clés API** : Pour un fonctionnement complet, vous aurez besoin de clés API pour :
   - Légifrance (via PISTE)
   - Pinecone
   - Claude (Anthropic) ou GPT (OpenAI)
   - Stripe (pour les paiements)

3. **Mode développement** : En développement, vous pouvez utiliser des mocks ou des données de test pour éviter de dépendre des API externes.

## Prochaines étapes

Une fois le déploiement local réussi, vous pourriez envisager :

1. Obtenir des clés API officielles pour Légifrance
2. Configurer un environnement de production
3. Mettre en place un pipeline CI/CD
4. Étendre les fonctionnalités à d'autres domaines juridiques
