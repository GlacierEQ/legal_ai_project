# Recherche sur l'API Légifrance

## Informations générales

- **Source officielle** : API Légifrance via le portail PISTE (Plateforme d'Intermédiation des Services pour la Transformation de l'État)
- **Fournisseur** : DILA (Direction de l'Information Légale et Administrative)
- **Version actuelle** : 2.4.2
- **Type** : REST
- **Format de données** : JSON
- **Accès** : Gratuit mais nécessite une inscription et une authentification
- **URL d'inscription** : https://piste.gouv.fr/registration

## Fonctionnalités principales

- Mise à disposition de l'ensemble des jeux de données de Légifrance
- Téléchargement des données et métadonnées
- Nombreuses possibilités de filtrage
- Recherche avec mots-clés, filtres et critères
- Suggestions de résultats pertinents à partir de mots-clés

## Contenu disponible

Les données juridiques disponibles via l'API sont celles du site Légifrance, notamment :
- Codes (Code de commerce, Code général des impôts, etc.)
- Lois et règlements
- Jurisprudence
- Doctrine administrative
- Bulletins officiels

## Conditions d'utilisation

L'utilisation de ces données est soumise à :
- La licence ouverte 2.0
- Aux conditions générales d'utilisation de PISTE
- Aux conditions générales d'utilisation de l'API Légifrance
- À des quotas détaillés sur le portail PISTE

## Documentation

- Documentation technique sur chaque méthode de l'API disponible sur le portail PISTE (Swagger)
- Documentation complémentaire sur les tris et filtres disponibles
- Exemples pratiques d'utilisation
- Définitions des termes utilisés dans l'API (LEGI, NOR, CID, etc.)

## Intégration dans notre projet

Pour intégrer l'API Légifrance dans notre assistant juridique IA, nous devrons :

1. **Créer un compte sur PISTE** : S'inscrire sur https://piste.gouv.fr/registration
2. **Obtenir les identifiants d'API** : Après inscription, obtenir les clés d'API nécessaires
3. **Développer un module d'authentification** : Gérer l'authentification OAuth ou par clé API
4. **Créer un pipeline ETL** : Développer des scripts pour extraire, transformer et charger les données juridiques
5. **Mettre en place un système de mise à jour** : Automatiser les mises à jour pour maintenir la base de connaissances à jour
6. **Implémenter un système de cache** : Optimiser les performances et respecter les quotas d'API

## Avantages par rapport au web scraping

- Données officielles et structurées
- Mise à jour régulière et fiable
- Format JSON standardisé
- Meilleure performance et stabilité
- Respect des conditions d'utilisation légales
- Documentation complète

## Prochaines étapes

1. Créer un compte sur le portail PISTE
2. Explorer la documentation détaillée de l'API
3. Tester les endpoints spécifiques au droit des affaires et fiscal
4. Concevoir l'architecture de collecte et de stockage des données
5. Développer un prototype d'intégration
