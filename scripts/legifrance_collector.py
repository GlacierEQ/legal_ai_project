#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de collecte de données juridiques depuis l'API Légifrance via PISTE
Ce script permet de se connecter à l'API Légifrance, d'extraire les textes juridiques
et de les stocker dans une base de données structurée.
"""

import os
import json
import time
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("legifrance_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("legifrance_collector")

# Chargement des variables d'environnement
load_dotenv()

class LegifranceAPI:
    """Classe pour interagir avec l'API Légifrance via PISTE"""
    
    # URL de base de l'API
    BASE_URL = "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app"
    
    # Endpoints principaux
    ENDPOINTS = {
        "token": "/oauth/token",
        "consult": "/consult",
        "search": "/search"
    }
    
    def __init__(self):
        """Initialisation de la connexion à l'API Légifrance"""
        self.client_id = os.getenv("LEGIFRANCE_CLIENT_ID")
        self.client_secret = os.getenv("LEGIFRANCE_CLIENT_SECRET")
        self.token = None
        self.token_expiry = None
        
        if not self.client_id or not self.client_secret:
            logger.error("Identifiants API manquants. Définissez LEGIFRANCE_CLIENT_ID et LEGIFRANCE_CLIENT_SECRET")
            raise ValueError("Identifiants API manquants")
        
        logger.info("Initialisation de l'API Légifrance")
    
    def get_token(self) -> str:
        """
        Obtient un token d'authentification OAuth2
        
        Returns:
            str: Token d'accès
        """
        # Vérifier si le token existe et est encore valide
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token
        
        logger.info("Demande d'un nouveau token d'authentification")
        
        url = f"{self.BASE_URL}{self.ENDPOINTS['token']}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "openid"
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.token = token_data["access_token"]
            # Définir l'expiration avec une marge de sécurité (10 minutes)
            expires_in = token_data.get("expires_in", 3600) - 600
            self.token_expiry = datetime.now().timestamp() + expires_in
            
            logger.info("Token d'authentification obtenu avec succès")
            return self.token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de l'obtention du token: {str(e)}")
            raise
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """
        Effectue une requête à l'API Légifrance
        
        Args:
            endpoint: Endpoint de l'API
            method: Méthode HTTP (GET, POST)
            data: Données à envoyer (pour les requêtes POST)
            
        Returns:
            Dict: Réponse JSON de l'API
        """
        token = self.get_token()
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête à {endpoint}: {str(e)}")
            # Si erreur d'authentification, essayer de renouveler le token
            if response.status_code == 401:
                self.token = None
                self.token_expiry = None
                logger.info("Tentative de renouvellement du token")
                return self._make_request(endpoint, method, data)
            raise
    
    def search_codes(self, keywords: Optional[str] = None) -> List[Dict]:
        """
        Recherche des codes juridiques
        
        Args:
            keywords: Mots-clés pour filtrer les résultats
            
        Returns:
            List[Dict]: Liste des codes trouvés
        """
        logger.info(f"Recherche de codes avec les mots-clés: {keywords}")
        
        data = {
            "recherche": {
                "champs": [
                    {
                        "typeChamp": "TITLE",
                        "critere": keywords or "",
                        "operateur": "ET"
                    }
                ],
                "filtres": [
                    {
                        "facette": "NATURE",
                        "valeurs": ["CODE"]
                    }
                ],
                "pageNumber": 1,
                "pageSize": 20,
                "sort": "PERTINENCE",
                "typePagination": "STANDARD"
            }
        }
        
        response = self._make_request(self.ENDPOINTS["search"], "POST", data)
        return response.get("results", [])
    
    def get_code_content(self, code_id: str) -> Dict:
        """
        Récupère le contenu d'un code juridique
        
        Args:
            code_id: Identifiant du code
            
        Returns:
            Dict: Contenu du code
        """
        logger.info(f"Récupération du contenu du code: {code_id}")
        
        data = {
            "textId": code_id
        }
        
        return self._make_request(self.ENDPOINTS["consult"], "POST", data)
    
    def search_articles(self, code_id: str, keywords: Optional[str] = None) -> List[Dict]:
        """
        Recherche des articles dans un code spécifique
        
        Args:
            code_id: Identifiant du code
            keywords: Mots-clés pour filtrer les résultats
            
        Returns:
            List[Dict]: Liste des articles trouvés
        """
        logger.info(f"Recherche d'articles dans le code {code_id} avec les mots-clés: {keywords}")
        
        data = {
            "recherche": {
                "champs": [
                    {
                        "typeChamp": "ALL",
                        "critere": keywords or "",
                        "operateur": "ET"
                    }
                ],
                "filtres": [
                    {
                        "facette": "NATURE",
                        "valeurs": ["ARTICLE_CODE"]
                    },
                    {
                        "facette": "CODE",
                        "valeurs": [code_id]
                    }
                ],
                "pageNumber": 1,
                "pageSize": 50,
                "sort": "PERTINENCE",
                "typePagination": "STANDARD"
            }
        }
        
        response = self._make_request(self.ENDPOINTS["search"], "POST", data)
        return response.get("results", [])
    
    def get_article_content(self, article_id: str) -> Dict:
        """
        Récupère le contenu d'un article juridique
        
        Args:
            article_id: Identifiant de l'article
            
        Returns:
            Dict: Contenu de l'article
        """
        logger.info(f"Récupération du contenu de l'article: {article_id}")
        
        data = {
            "textId": article_id
        }
        
        return self._make_request(self.ENDPOINTS["consult"], "POST", data)
    
    def search_jurisprudence(self, keywords: str, jurisdiction: Optional[str] = None) -> List[Dict]:
        """
        Recherche de jurisprudence
        
        Args:
            keywords: Mots-clés pour la recherche
            jurisdiction: Juridiction (CONSEIL_ETAT, COUR_CASSATION, etc.)
            
        Returns:
            List[Dict]: Liste des décisions trouvées
        """
        logger.info(f"Recherche de jurisprudence avec les mots-clés: {keywords}")
        
        filtres = [
            {
                "facette": "NATURE",
                "valeurs": ["JURISPRUDENCE"]
            }
        ]
        
        if jurisdiction:
            filtres.append({
                "facette": "JURIDICTION",
                "valeurs": [jurisdiction]
            })
        
        data = {
            "recherche": {
                "champs": [
                    {
                        "typeChamp": "ALL",
                        "critere": keywords,
                        "operateur": "ET"
                    }
                ],
                "filtres": filtres,
                "pageNumber": 1,
                "pageSize": 20,
                "sort": "DATE_DESC",
                "typePagination": "STANDARD"
            }
        }
        
        response = self._make_request(self.ENDPOINTS["search"], "POST", data)
        return response.get("results", [])


class BusinessTaxLawCollector:
    """Collecteur spécialisé pour le droit des affaires et fiscal"""
    
    # Codes juridiques pertinents pour le droit des affaires et fiscal
    RELEVANT_CODES = {
        "Code de commerce": "LEGITEXT000005634379",
        "Code général des impôts": "LEGITEXT000006069577",
        "Code monétaire et financier": "LEGITEXT000006072026",
        "Code de la consommation": "LEGITEXT000006069565",
        "Code du travail": "LEGITEXT000006072050"
    }
    
    # Mots-clés pertinents pour le droit des affaires
    BUSINESS_LAW_KEYWORDS = [
        "société", "entreprise", "commercial", "fonds de commerce",
        "SARL", "SAS", "SA", "EURL", "statuts", "associé", "gérant",
        "capital social", "immatriculation", "registre du commerce"
    ]
    
    # Mots-clés pertinents pour le droit fiscal
    TAX_LAW_KEYWORDS = [
        "impôt", "fiscal", "TVA", "taxe", "imposition", "IS", "IR",
        "crédit d'impôt", "déduction", "exonération", "BIC", "BNC",
        "plus-value", "amortissement", "provision"
    ]
    
    def __init__(self, api: LegifranceAPI, output_dir: str = "./data"):
        """
        Initialisation du collecteur
        
        Args:
            api: Instance de LegifranceAPI
            output_dir: Répertoire de sortie pour les données collectées
        """
        self.api = api
        self.output_dir = output_dir
        
        # Créer les répertoires de sortie s'ils n'existent pas
        os.makedirs(os.path.join(output_dir, "codes"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "articles"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "jurisprudence"), exist_ok=True)
        
        logger.info(f"Collecteur initialisé avec répertoire de sortie: {output_dir}")
    
    def collect_codes(self) -> None:
        """Collecte les codes juridiques pertinents"""
        logger.info("Début de la collecte des codes juridiques")
        
        for code_name, code_id in self.RELEVANT_CODES.items():
            try:
                logger.info(f"Collecte du code: {code_name}")
                code_content = self.api.get_code_content(code_id)
                
                # Sauvegarder le contenu du code
                output_file = os.path.join(self.output_dir, "codes", f"{code_id}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(code_content, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Code {code_name} sauvegardé dans {output_file}")
                
                # Respecter les limites de l'API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erreur lors de la collecte du code {code_name}: {str(e)}")
    
    def collect_business_law_articles(self) -> None:
        """Collecte les articles relatifs au droit des affaires"""
        logger.info("Début de la collecte des articles de droit des affaires")
        
        relevant_codes = ["LEGITEXT000005634379", "LEGITEXT000006072026"]  # Commerce et Monétaire
        
        for keyword in self.BUSINESS_LAW_KEYWORDS:
            for code_id in relevant_codes:
                try:
                    logger.info(f"Recherche d'articles avec le mot-clé '{keyword}' dans le code {code_id}")
                    articles = self.api.search_articles(code_id, keyword)
                    
                    for article in articles:
                        article_id = article.get("id")
                        if not article_id:
                            continue
                        
                        # Récupérer le contenu complet de l'article
                        article_content = self.api.get_article_content(article_id)
                        
                        # Sauvegarder le contenu de l'article
                        output_file = os.path.join(self.output_dir, "articles", f"{article_id}.json")
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(article_content, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f"Article {article_id} sauvegardé dans {output_file}")
                        
                        # Respecter les limites de l'API
                        time.sleep(1)
                
                except Exception as e:
                    logger.error(f"Erreur lors de la collecte des articles avec le mot-clé '{keyword}': {str(e)}")
    
    def collect_tax_law_articles(self) -> None:
        """Collecte les articles relatifs au droit fiscal"""
        logger.info("Début de la collecte des articles de droit fiscal")
        
        relevant_codes = ["LEGITEXT000006069577"]  # Code général des impôts
        
        for keyword in self.TAX_LAW_KEYWORDS:
            for code_id in relevant_codes:
                try:
                    logger.info(f"Recherche d'articles avec le mot-clé '{keyword}' dans le code {code_id}")
                    articles = self.api.search_articles(code_id, keyword)
                    
                    for article in articles:
                        article_id = article.get("id")
                        if not article_id:
                            continue
                        
                        # Récupérer le contenu complet de l'article
                        article_content = self.api.get_article_content(article_id)
                        
                        # Sauvegarder le contenu de l'article
                        output_file = os.path.join(self.output_dir, "articles", f"{article_id}.json")
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(article_content, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f"Article {article_id} sauvegardé dans {output_file}")
                        
                        # Respecter les limites de l'API
                        time.sleep(1)
                
                except Exception as e:
                    logger.error(f"Erreur lors de la collecte des articles avec le mot-clé '{keyword}': {str(e)}")
    
    def collect_relevant_jurisprudence(self) -> None:
        """Collecte la jurisprudence pertinente pour le droit des affaires et fiscal"""
        logger.info("Début de la collecte de la jurisprudence")
        
        # Combiner les mots-clés des deux domaines
        all_keywords = self.BUSINESS_LAW_KEYWORDS + self.TAX_LAW_KEYWORDS
        
        # Juridictions pertinentes
        jurisdictions = ["CONSEIL_ETAT", "COUR_CASSATION"]
        
        for keyword in all_keywords:
            for jurisdiction in jurisdictions:
                try:
                    logger.info(f"Recherche de jurisprudence avec le mot-clé '{keyword}' pour {jurisdiction}")
                    decisions = self.api.search_jurisprudence(keyword, jurisdiction)
                    
                    for decision in decisions:
                        decision_id = decision.get("id")
                        if not decision_id:
                            continue
                        
                        # Récupérer le contenu complet de la décision
                        decision_content = self.api.get_article_content(decision_id)
                        
                        # Sauvegarder le contenu de la décision
                        output_file = os.path.join(self.output_dir, "jurisprudence", f"{decision_id}.json")
                        with open(output_file, "w", encoding="utf-8") as f:
                            json.dump(decision_content, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f"Décision {decision_id} sauvegardée dans {output_file}")
                        
                        # Respecter les limites de l'API
                        time.sleep(1)
                
                except Exception as e:
                    logger.error(f"Erreur lors de la collecte de jurisprudence avec le mot-clé '{keyword}': {str(e)}")
    
    def run_collection(self) -> None:
        """Exécute le processus complet de collecte"""
        logger.info("Début du processus complet de collecte")
        
        try:
            # Étape 1: Collecter les codes
            self.collect_codes()
            
            # Étape 2: Collecter les articles de droit des affaires
            self.collect_business_law_articles()
            
            # Étape 3: Collecter les articles de droit fiscal
            self.collect_tax_law_articles()
            
            # Étape 4: Collecter la jurisprudence pertinente
            self.collect_relevant_jurisprudence()
            
            logger.info("Processus de collecte terminé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du processus de collecte: {str(e)}")


if __name__ == "__main__":
    try:
        # Initialiser l'API Légifrance
        api = LegifranceAPI()
        
        # Initialiser le collecteur
        collector = BusinessTaxLawCollector(api, output_dir="/home/ubuntu/legal_ai_project/data/legifrance")
        
        # Exécuter la collecte
        collector.run_collection()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du script: {str(e)}")
