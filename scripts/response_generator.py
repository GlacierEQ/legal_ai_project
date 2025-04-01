#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de génération de réponses juridiques pour l'assistant IA
Ce script utilise les résultats de recherche vectorielle et un LLM pour générer des réponses juridiques précises
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dotenv import load_dotenv
import anthropic
import openai

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("response_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("response_generator")

# Chargement des variables d'environnement
load_dotenv()

class LegalResponseGenerator:
    """Classe pour générer des réponses juridiques basées sur les résultats de recherche"""
    
    def __init__(self, model_provider: str = "claude"):
        """
        Initialisation du générateur de réponses
        
        Args:
            model_provider: Fournisseur du modèle LLM ("claude" ou "openai")
        """
        self.model_provider = model_provider
        
        # Initialiser le client LLM approprié
        if model_provider == "claude":
            self._init_claude()
        elif model_provider == "openai":
            self._init_openai()
        else:
            raise ValueError(f"Fournisseur de modèle non supporté: {model_provider}")
        
        logger.info(f"Générateur de réponses initialisé avec le modèle: {model_provider}")
    
    def _init_claude(self) -> None:
        """Initialise le client Claude"""
        claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not claude_api_key:
            logger.error("Clé API Claude manquante. Définissez ANTHROPIC_API_KEY")
            raise ValueError("Clé API Claude manquante")
        
        self.client = anthropic.Anthropic(api_key=claude_api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
        logger.info(f"Client Claude initialisé avec le modèle: {self.model}")
    
    def _init_openai(self) -> None:
        """Initialise le client OpenAI"""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            logger.error("Clé API OpenAI manquante. Définissez OPENAI_API_KEY")
            raise ValueError("Clé API OpenAI manquante")
        
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        logger.info(f"Client OpenAI initialisé avec le modèle: {self.model}")
    
    def _format_search_results(self, results: List[Dict]) -> str:
        """
        Formate les résultats de recherche pour inclusion dans le prompt
        
        Args:
            results: Liste des résultats de recherche
            
        Returns:
            str: Résultats formatés
        """
        formatted_results = []
        
        for i, result in enumerate(results):
            metadata = result.get('metadata', {})
            text = metadata.get('text', '')
            
            # Déterminer le type de document
            doc_type = metadata.get('type', 'TEXTE')
            
            # Extraire les informations spécifiques selon le type
            if doc_type == 'ARTICLE':
                code_name = metadata.get('article_code_name', 'Code non spécifié')
                article_num = metadata.get('article_num', 'Numéro non spécifié')
                formatted_results.append(f"[Document {i+1} - Article {article_num} du {code_name}]\n{text}\n")
            
            elif doc_type == 'JURISPRUDENCE':
                jurisdiction = metadata.get('jurisprudence_jurisdiction', 'Juridiction non spécifiée')
                decision_date = metadata.get('jurisprudence_decision_date', 'Date non spécifiée')
                formatted_results.append(f"[Document {i+1} - Jurisprudence {jurisdiction} du {decision_date}]\n{text}\n")
            
            else:
                formatted_results.append(f"[Document {i+1}]\n{text}\n")
        
        return "\n".join(formatted_results)
    
    def _create_business_law_prompt(self, query: str, search_results: List[Dict], user_profile: str) -> str:
        """
        Crée un prompt spécialisé pour le droit des affaires
        
        Args:
            query: Question de l'utilisateur
            search_results: Résultats de la recherche vectorielle
            user_profile: Profil de l'utilisateur ("professionnel" ou "particulier")
            
        Returns:
            str: Prompt formaté
        """
        formatted_results = self._format_search_results(search_results)
        
        # Adapter le niveau de détail selon le profil utilisateur
        detail_level = "détaillé et technique" if user_profile == "professionnel" else "clair et accessible"
        
        prompt = f"""En tant qu'assistant juridique spécialisé en droit des affaires français, réponds à la question suivante:

Question: {query}

Contexte juridique:
{formatted_results}

Format de réponse:
1. Introduction: Présente le cadre général de la question.
2. Cadre légal: Cite les articles pertinents du Code de commerce et autres textes applicables.
3. Application pratique: Explique les démarches concrètes à suivre.
4. Exceptions: Mentionne les cas particuliers ou régimes dérogatoires.
5. Recommandations: Suggère les meilleures pratiques à suivre.
6. Sources: Liste les références précises des textes cités.

Ton niveau de détail doit être {detail_level}, car l'utilisateur est un {user_profile}.
Cite précisément les articles et textes juridiques pertinents.
Si les informations fournies sont insuffisantes pour répondre complètement, indique-le clairement.
"""
        
        return prompt
    
    def _create_tax_law_prompt(self, query: str, search_results: List[Dict], user_profile: str) -> str:
        """
        Crée un prompt spécialisé pour le droit fiscal
        
        Args:
            query: Question de l'utilisateur
            search_results: Résultats de la recherche vectorielle
            user_profile: Profil de l'utilisateur ("professionnel" ou "particulier")
            
        Returns:
            str: Prompt formaté
        """
        formatted_results = self._format_search_results(search_results)
        
        # Adapter le niveau de détail selon le profil utilisateur
        detail_level = "détaillé et technique" if user_profile == "professionnel" else "clair et accessible"
        
        prompt = f"""En tant qu'assistant juridique spécialisé en droit fiscal français, réponds à la question suivante:

Question: {query}

Contexte juridique:
{formatted_results}

Format de réponse:
1. Introduction: Présente le cadre général de la question fiscale.
2. Cadre légal: Cite les articles pertinents du Code général des impôts et instructions fiscales.
3. Application au cas d'espèce: Explique comment les règles s'appliquent à la situation.
4. Exceptions et optimisations légales: Mentionne les dispositifs fiscaux avantageux applicables.
5. Points de vigilance: Indique les risques fiscaux à surveiller.
6. Sources: Liste les références précises des textes et instructions cités.

Ton niveau de détail doit être {detail_level}, car l'utilisateur est un {user_profile}.
Cite précisément les articles et textes juridiques pertinents.
Si les informations fournies sont insuffisantes pour répondre complètement, indique-le clairement.
"""
        
        return prompt
    
    def generate_response_claude(self, prompt: str) -> str:
        """
        Génère une réponse en utilisant Claude
        
        Args:
            prompt: Prompt formaté
            
        Returns:
            str: Réponse générée
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse avec Claude: {str(e)}")
            return "Une erreur est survenue lors de la génération de la réponse."
    
    def generate_response_openai(self, prompt: str) -> str:
        """
        Génère une réponse en utilisant OpenAI
        
        Args:
            prompt: Prompt formaté
            
        Returns:
            str: Réponse générée
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "system", "content": "Tu es un assistant juridique spécialisé en droit français, particulièrement en droit des affaires et fiscal."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse avec OpenAI: {str(e)}")
            return "Une erreur est survenue lors de la génération de la réponse."
    
    def generate_response(self, query: str, search_results: List[Dict], domain: str, user_profile: str) -> str:
        """
        Génère une réponse juridique basée sur les résultats de recherche
        
        Args:
            query: Question de l'utilisateur
            search_results: Résultats de la recherche vectorielle
            domain: Domaine juridique ("business" ou "tax")
            user_profile: Profil de l'utilisateur ("professionnel" ou "particulier")
            
        Returns:
            str: Réponse juridique générée
        """
        logger.info(f"Génération de réponse pour la question: {query}")
        
        # Créer le prompt approprié selon le domaine
        if domain == "business":
            prompt = self._create_business_law_prompt(query, search_results, user_profile)
        elif domain == "tax":
            prompt = self._create_tax_law_prompt(query, search_results, user_profile)
        else:
            logger.error(f"Domaine non supporté: {domain}")
            return "Domaine juridique non supporté."
        
        # Générer la réponse avec le modèle approprié
        if self.model_provider == "claude":
            response = self.generate_response_claude(prompt)
        else:  # openai
            response = self.generate_response_openai(prompt)
        
        # Ajouter un avertissement standard
        disclaimer = "\n\n---\n*Avertissement: Cette réponse est générée par une IA et ne constitue pas un avis juridique professionnel. Pour des conseils juridiques personnalisés, veuillez consulter un avocat ou un professionnel du droit qualifié.*"
        
        return response + disclaimer
    
    def detect_domain(self, query: str) -> str:
        """
        Détecte automatiquement le domaine juridique de la question
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            str: Domaine détecté ("business" ou "tax")
        """
        # Mots-clés associés au droit des affaires
        business_keywords = [
            "société", "entreprise", "commercial", "fonds de commerce",
            "SARL", "SAS", "SA", "EURL", "statuts", "associé", "gérant",
            "capital social", "immatriculation", "registre du commerce"
        ]
        
        # Mots-clés associés au droit fiscal
        tax_keywords = [
            "impôt", "fiscal", "TVA", "taxe", "imposition", "IS", "IR",
            "crédit d'impôt", "déduction", "exonération", "BIC", "BNC",
            "plus-value", "amortissement", "provision"
        ]
        
        # Compter les occurrences de mots-clés
        business_count = sum(1 for keyword in business_keywords if keyword.lower() in query.lower())
        tax_count = sum(1 for keyword in tax_keywords if keyword.lower() in query.lower())
        
        # Déterminer le domaine en fonction du nombre d'occurrences
        if business_count > tax_count:
            return "business"
        elif tax_count > business_count:
            return "tax"
        else:
            # En cas d'égalité ou d'absence de mots-clés, utiliser une approche plus sophistiquée
            # Pour l'instant, on retourne "business" par défaut
            return "business"


class LegalAssistantAPI:
    """Classe pour intégrer la recherche vectorielle et la génération de réponses"""
    
    def __init__(self, searcher, response_generator):
        """
        Initialisation de l'API de l'assistant juridique
        
        Args:
            searcher: Instance de BusinessTaxLawSearcher
            response_generator: Instance de LegalResponseGenerator
        """
        self.searcher = searcher
        self.response_generator = response_generator
        logger.info("API de l'assistant juridique initialisée")
    
    def process_query(self, query: str, user_profile: str = "particulier") -> Dict:
        """
        Traite une requête utilisateur et génère une réponse juridique
        
        Args:
            query: Question de l'utilisateur
            user_profile: Profil de l'utilisateur ("professionnel" ou "particulier")
            
        Returns:
            Dict: Réponse formatée avec métadonnées
        """
        logger.info(f"Traitement de la requête: {query}")
        
        try:
            # Détecter le domaine juridique
            domain = self.response_generator.detect_domain(query)
            logger.info(f"Domaine détecté: {domain}")
            
            # Effectuer la recherche appropriée
            if domain == "business":
                search_results = self.searcher.search_business_law(query, top_k=5)
            else:  # tax
                search_results = self.searcher.search_tax_law(query, top_k=5)
            
            # Générer la réponse
            response_text = self.response_generator.generate_response(
                query, search_results, domain, user_profile
            )
            
            # Extraire les sources citées
            sources = self._extract_sources(search_results)
            
            # Créer la réponse formatée
            response = {
                "query": query,
                "domain": "Droit des affaires" if domain == "business" else "Droit fiscal",
                "response": response_text,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la requête: {str(e)}")
            return {
                "query": query,
                "error": str(e),
                "response": "Une erreur est survenue lors du traitement de votre question.",
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_sources(self, search_results: List[Dict]) -> List[Dict]:
        """
        Extrait les sources des résultats de recherche
        
        Args:
            search_results: Résultats de la recherche vectorielle
            
        Returns:
            List[Dict]: Liste des sources formatées
        """
        sources = []
        
        for result in search_results:
            metadata = result.get('metadata', {})
            
            # Déterminer le type de document
            doc_type = metadata.get('type', 'TEXTE')
            
            source = {
                "type": doc_type,
                "score": result.get('score', 0)
            }
            
            # Ajouter les informations spécifiques selon le type
            if doc_type == 'ARTICLE':
                source.update({
                    "code_id": metadata.get('article_code_id', ''),
                    "code_name": metadata.get('article_code_name', ''),
                    "article_num": metadata.get('article_num', ''),
                    "creation_date": metadata.get('article_creation_date', '')
                })
            
            elif doc_type == 'JURISPRUDENCE':
                source.update({
                    "jurisdiction": metadata.get('jurisprudence_jurisdiction', ''),
                    "decision_date": metadata.get('jurisprudence_decision_date', ''),
                    "number": metadata.get('jurisprudence_number', '')
                })
            
            sources.append(source)
        
        return sources
    
    def save_interaction(self, query: str, response: Dict, user_id: Optional[str] = None) -> None:
        """
        Sauvegarde l'interaction pour analyse et amélioration
        
        Args:
            query: Question de l'utilisateur
            response: Réponse générée
            user_id: Identifiant de l'utilisateur (si disponible)
        """
        try:
            # Créer l'enregistrement de l'interaction
            interaction = {
                "user_id": user_id,
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Sauvegarder dans un fichier JSON (à remplacer par une base de données)
            log_dir = os.path.join(os.getcwd(), "logs", "interactions")
            os.makedirs(log_dir, exist_ok=True)
            
            filename = f"interaction_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            filepath = os.path.join(log_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(interaction, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Interaction sauvegardée dans {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'interaction: {str(e)}")


if __name__ == "__main__":
    try:
        # Cet import serait normalement en haut du fichier
        # Il est placé ici pour éviter les dépendances circulaires dans cet exemple
        from vector_indexer import VectorIndexer, BusinessTaxLawSearcher
        
        # Initialiser l'indexeur vectoriel
        input_dir = "/home/ubuntu/legal_ai_project/data/processed"
        indexer = VectorIndexer(input_dir)
        
        # Initialiser le chercheur spécialisé
        searcher = BusinessTaxLawSearcher(indexer)
        
        # Initialiser le générateur de réponses
        response_generator = LegalResponseGenerator(model_provider="claude")
        
        # Initialiser l'API de l'assistant juridique
        legal_assistant = LegalAssistantAPI(searcher, response_generator)
        
        # Exemple de requête
        query = "Comment créer une SAS en France et quelles sont les obligations fiscales ?"
        user_profile = "particulier"
        
        # Traiter la requête
        response = legal_assistant.process_query(query, user_profile)
        
        # Afficher la réponse
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
        # Sauvegarder l'interaction
        legal_assistant.save_interaction(query, response)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du script: {str(e)}")
