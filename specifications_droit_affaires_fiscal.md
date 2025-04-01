# Spécifications - Domaine du Droit des Affaires et Fiscal

## Introduction

Ce document détaille les spécifications techniques et fonctionnelles pour l'implémentation du domaine prioritaire de l'assistant juridique IA : le droit des affaires et fiscal français. Il définit les sous-domaines à couvrir, les sources de données spécifiques, les types de requêtes à traiter et les particularités de la génération de réponses pour ce domaine.

## Sous-domaines prioritaires

### 1. Création d'entreprise
- Choix de la forme juridique (SARL, SAS, EURL, etc.)
- Formalités de constitution
- Régimes fiscaux applicables
- Obligations comptables initiales
- Aides et subventions à la création

### 2. Fiscalité des entreprises
- Impôt sur les sociétés (IS)
- Impôt sur le revenu des entrepreneurs individuels (IR)
- TVA et taxes spécifiques
- Crédits d'impôt recherche et innovation
- Optimisation fiscale légale

### 3. Droit social et obligations employeur
- Embauche et contrats de travail
- Charges sociales et déclarations
- Obligations légales (médecine du travail, affichages, etc.)
- Rupture du contrat de travail
- Épargne salariale et intéressement

### 4. Comptabilité et obligations financières
- Plan comptable général
- Obligations déclaratives
- Établissement des comptes annuels
- Certification et audit
- Délais de conservation des documents

## Sources de données spécifiques

### Sources primaires
- **Code général des impôts** (CGI)
- **Code de commerce**
- **Code du travail** (sections relatives aux entreprises)
- **Bulletin Officiel des Finances Publiques-Impôts** (BOFiP)
- **Doctrine administrative fiscale**
- **Jurisprudence du Conseil d'État** (contentieux fiscal)
- **Jurisprudence de la Cour de cassation** (chambre commerciale)

### Sources secondaires
- **Revues spécialisées** (Revue Fiduciaire, Revue Française de Comptabilité)
- **Guides pratiques** (Mémento Fiscal, Francis Lefebvre)
- **Publications des ordres professionnels** (Ordre des Experts-Comptables, Conseil National des Barreaux)

## Stratégie de collecte des données

### Approche en l'absence d'API officielles
1. **Web scraping structuré**:
   - Légifrance: extraction des codes pertinents (commerce, impôts)
   - BOFiP: extraction des bulletins et instructions fiscales
   - Conseil d'État et Cour de cassation: extraction des décisions importantes

2. **Fréquence de mise à jour**:
   - Textes législatifs: hebdomadaire
   - Jurisprudence: bi-hebdomadaire
   - Doctrine administrative: mensuelle

3. **Prioritisation des données**:
   - Textes en vigueur > textes abrogés
   - Jurisprudence récente > jurisprudence ancienne
   - Instructions fiscales récentes > anciennes instructions

## Structure des données juridiques

### Hiérarchisation des textes
- **Niveau 1**: Codes (Commerce, Impôts)
  - **Niveau 2**: Livres
    - **Niveau 3**: Titres
      - **Niveau 4**: Chapitres
        - **Niveau 5**: Articles

### Métadonnées à extraire
- Identifiant unique
- Type de texte (loi, décret, jurisprudence, etc.)
- Date de publication
- Date d'entrée en vigueur
- Date d'abrogation (si applicable)
- Références croisées
- Mots-clés thématiques

### Enrichissement sémantique
- Classification par sous-domaine juridique
- Extraction des concepts juridiques clés
- Identification des relations entre textes (modification, abrogation, etc.)
- Détection des exceptions et cas particuliers

## Types de requêtes à traiter

### Requêtes informatives
- "Quelles sont les étapes pour créer une SAS?"
- "Quel est le taux d'IS applicable aux PME?"
- "Quelles sont les obligations comptables d'une SARL?"

### Requêtes procédurales
- "Comment déclarer la TVA pour une auto-entreprise?"
- "Comment mettre en place un accord d'intéressement?"
- "Quelle procédure suivre pour un contrôle fiscal?"

### Requêtes analytiques
- "Quelle forme juridique est la plus avantageuse fiscalement pour mon activité?"
- "Quels sont les risques juridiques de la sous-capitalisation?"
- "Comment optimiser légalement la fiscalité de mon entreprise?"

## Génération de réponses spécialisées

### Structure adaptée au droit des affaires et fiscal
1. **Introduction contextuelle**
   - Présentation du cadre général
   - Importance de la question dans le contexte entrepreneurial

2. **Cadre légal applicable**
   - Articles du Code général des impôts ou du Code de commerce
   - Références aux instructions fiscales (BOFiP)
   - Jurisprudence pertinente

3. **Application pratique**
   - Démarches concrètes à suivre
   - Formulaires et déclarations concernés
   - Délais à respecter

4. **Exceptions et cas particuliers**
   - Régimes dérogatoires
   - Seuils d'application
   - Situations spécifiques (holdings, groupes, etc.)

5. **Recommandations**
   - Bonnes pratiques
   - Points de vigilance
   - Évolutions législatives à surveiller

6. **Sources**
   - Citations précises des textes
   - Références aux bulletins officiels
   - Liens vers les formulaires officiels

### Adaptation selon le profil utilisateur

#### Pour les entrepreneurs et dirigeants (non-spécialistes)
- Langage simplifié, évitant le jargon technique
- Explications des concepts juridiques et fiscaux
- Focus sur les applications pratiques
- Recommandations d'actions concrètes

#### Pour les experts-comptables et avocats (professionnels)
- Terminologie technique précise
- Citations détaillées des textes et jurisprudences
- Analyse approfondie des implications juridiques
- Références aux débats doctrinaux et évolutions récentes

## Évaluation et amélioration continue

### Métriques de qualité
- Précision juridique des réponses
- Pertinence par rapport à la question
- Exhaustivité des sources citées
- Clarté et structure de la réponse

### Processus d'amélioration
- Révision périodique par des experts juridiques
- Analyse des retours utilisateurs
- Mise à jour des connaissances suite aux évolutions législatives
- Enrichissement continu de la base de connaissances

## Limitations et avertissements spécifiques

### Avertissements légaux
- "Les informations fournies constituent une première orientation et ne remplacent pas une consultation auprès d'un avocat fiscaliste ou d'un expert-comptable."
- "L'application des règles fiscales dépend de votre situation particulière et peut nécessiter une analyse personnalisée."
- "Les informations sont à jour au [date], mais la législation fiscale peut évoluer rapidement."

### Cas nécessitant une redirection vers un professionnel
- Montages juridiques complexes
- Opérations internationales
- Contentieux fiscal
- Restructurations d'entreprises
- Situations impliquant des risques pénaux
