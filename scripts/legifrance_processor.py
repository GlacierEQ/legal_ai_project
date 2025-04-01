#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de traitement et d'indexation des données juridiques collectées depuis l'API Légifrance
Ce script transforme les données brutes en format structuré et les prépare pour l'indexation vectorielle
"""

import os
import json
import logging
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("legifrance_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("legifrance_processor")

class LegalTextProcessor:
    """Classe pour traiter et structurer les textes juridiques"""
    
    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialisation du processeur
        
        Args:
            input_dir: Répertoire contenant les données brutes
            output_dir: Répertoire de sortie pour les données structurées
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Créer les répertoires de sortie s'ils n'existent pas
        os.makedirs(os.path.join(output_dir, "structured"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "metadata"), exist_ok=True)
        
        logger.info(f"Processeur initialisé avec répertoire d'entrée: {input_dir} et de sortie: {output_dir}")
    
    def process_code(self, code_file: str) -> Dict:
        """
        Traite un fichier de code juridique
        
        Args:
            code_file: Chemin vers le fichier JSON du code
            
        Returns:
            Dict: Métadonnées du code traité
        """
        logger.info(f"Traitement du code: {code_file}")
        
        try:
            # Charger le fichier JSON
            with open(code_file, 'r', encoding='utf-8') as f:
                code_data = json.load(f)
            
            # Extraire les informations de base
            code_id = os.path.basename(code_file).replace('.json', '')
            title = code_data.get('title', 'Code sans titre')
            
            # Extraire la structure du code (livres, titres, chapitres, etc.)
            structure = self._extract_code_structure(code_data)
            
            # Créer un dictionnaire de métadonnées
            metadata = {
                'id': code_id,
                'title': title,
                'type': 'CODE',
                'structure': structure,
                'processed_date': datetime.now().isoformat()
            }
            
            # Sauvegarder les métadonnées
            output_file = os.path.join(self.output_dir, "metadata", f"{code_id}_metadata.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Métadonnées du code {code_id} sauvegardées dans {output_file}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du code {code_file}: {str(e)}")
            return {}
    
    def _extract_code_structure(self, code_data: Dict) -> List[Dict]:
        """
        Extrait la structure hiérarchique d'un code
        
        Args:
            code_data: Données du code
            
        Returns:
            List[Dict]: Structure hiérarchique du code
        """
        structure = []
        
        # Extraction de la structure selon le format de l'API Légifrance
        # Cette méthode devra être adaptée selon le format exact des données
        
        if 'structure' in code_data:
            for item in code_data.get('structure', []):
                structure_item = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'level': item.get('level', 0)
                }
                
                # Récursion pour les sous-éléments
                if 'children' in item:
                    structure_item['children'] = self._extract_children(item.get('children', []))
                
                structure.append(structure_item)
        
        return structure
    
    def _extract_children(self, children: List[Dict]) -> List[Dict]:
        """
        Extrait récursivement les sous-éléments d'une structure
        
        Args:
            children: Liste des sous-éléments
            
        Returns:
            List[Dict]: Sous-éléments structurés
        """
        result = []
        
        for child in children:
            child_item = {
                'id': child.get('id', ''),
                'title': child.get('title', ''),
                'level': child.get('level', 0)
            }
            
            if 'children' in child:
                child_item['children'] = self._extract_children(child.get('children', []))
            
            result.append(child_item)
        
        return result
    
    def process_article(self, article_file: str) -> Dict:
        """
        Traite un fichier d'article juridique
        
        Args:
            article_file: Chemin vers le fichier JSON de l'article
            
        Returns:
            Dict: Article structuré
        """
        logger.info(f"Traitement de l'article: {article_file}")
        
        try:
            # Charger le fichier JSON
            with open(article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
            
            # Extraire les informations de base
            article_id = os.path.basename(article_file).replace('.json', '')
            
            # Extraire le contenu textuel
            content = self._extract_article_content(article_data)
            
            # Extraire les métadonnées
            metadata = self._extract_article_metadata(article_data)
            
            # Créer un article structuré
            structured_article = {
                'id': article_id,
                'content': content,
                'metadata': metadata,
                'processed_date': datetime.now().isoformat()
            }
            
            # Sauvegarder l'article structuré
            output_file = os.path.join(self.output_dir, "structured", f"{article_id}_structured.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(structured_article, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Article {article_id} structuré sauvegardé dans {output_file}")
            
            return structured_article
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'article {article_file}: {str(e)}")
            return {}
    
    def _extract_article_content(self, article_data: Dict) -> str:
        """
        Extrait le contenu textuel d'un article
        
        Args:
            article_data: Données de l'article
            
        Returns:
            str: Contenu textuel de l'article
        """
        # Cette méthode devra être adaptée selon le format exact des données
        content = ""
        
        if 'article' in article_data and 'content' in article_data['article']:
            content = article_data['article']['content']
        elif 'content' in article_data:
            content = article_data['content']
        
        # Nettoyage du contenu (suppression des balises HTML, etc.)
        # Implémentation à adapter selon le format exact
        
        return content
    
    def _extract_article_metadata(self, article_data: Dict) -> Dict:
        """
        Extrait les métadonnées d'un article
        
        Args:
            article_data: Données de l'article
            
        Returns:
            Dict: Métadonnées de l'article
        """
        metadata = {}
        
        # Extraction des métadonnées selon le format de l'API Légifrance
        if 'article' in article_data:
            article = article_data['article']
            metadata = {
                'num': article.get('num', ''),
                'title': article.get('title', ''),
                'code_id': article.get('codeId', ''),
                'code_name': article.get('codeName', ''),
                'section_title': article.get('sectionTitle', ''),
                'creation_date': article.get('creationDate', ''),
                'modification_date': article.get('modificationDate', ''),
                'abrogation_date': article.get('abrogationDate', ''),
                'is_active': article.get('isActive', True)
            }
        
        return metadata
    
    def process_jurisprudence(self, jurisprudence_file: str) -> Dict:
        """
        Traite un fichier de jurisprudence
        
        Args:
            jurisprudence_file: Chemin vers le fichier JSON de la jurisprudence
            
        Returns:
            Dict: Jurisprudence structurée
        """
        logger.info(f"Traitement de la jurisprudence: {jurisprudence_file}")
        
        try:
            # Charger le fichier JSON
            with open(jurisprudence_file, 'r', encoding='utf-8') as f:
                jurisprudence_data = json.load(f)
            
            # Extraire les informations de base
            jurisprudence_id = os.path.basename(jurisprudence_file).replace('.json', '')
            
            # Extraire le contenu textuel
            content = self._extract_jurisprudence_content(jurisprudence_data)
            
            # Extraire les métadonnées
            metadata = self._extract_jurisprudence_metadata(jurisprudence_data)
            
            # Créer une jurisprudence structurée
            structured_jurisprudence = {
                'id': jurisprudence_id,
                'content': content,
                'metadata': metadata,
                'processed_date': datetime.now().isoformat()
            }
            
            # Sauvegarder la jurisprudence structurée
            output_file = os.path.join(self.output_dir, "structured", f"{jurisprudence_id}_structured.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(structured_jurisprudence, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Jurisprudence {jurisprudence_id} structurée sauvegardée dans {output_file}")
            
            return structured_jurisprudence
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la jurisprudence {jurisprudence_file}: {str(e)}")
            return {}
    
    def _extract_jurisprudence_content(self, jurisprudence_data: Dict) -> str:
        """
        Extrait le contenu textuel d'une jurisprudence
        
        Args:
            jurisprudence_data: Données de la jurisprudence
            
        Returns:
            str: Contenu textuel de la jurisprudence
        """
        # Cette méthode devra être adaptée selon le format exact des données
        content = ""
        
        if 'decision' in jurisprudence_data and 'text' in jurisprudence_data['decision']:
            content = jurisprudence_data['decision']['text']
        elif 'text' in jurisprudence_data:
            content = jurisprudence_data['text']
        
        return content
    
    def _extract_jurisprudence_metadata(self, jurisprudence_data: Dict) -> Dict:
        """
        Extrait les métadonnées d'une jurisprudence
        
        Args:
            jurisprudence_data: Données de la jurisprudence
            
        Returns:
            Dict: Métadonnées de la jurisprudence
        """
        metadata = {}
        
        # Extraction des métadonnées selon le format de l'API Légifrance
        if 'decision' in jurisprudence_data:
            decision = jurisprudence_data['decision']
            metadata = {
                'jurisdiction': decision.get('jurisdiction', ''),
                'decision_date': decision.get('decisionDate', ''),
                'publication_date': decision.get('publicationDate', ''),
                'number': decision.get('number', ''),
                'solution': decision.get('solution', ''),
                'formation': decision.get('formation', '')
            }
        
        return metadata
    
    def create_metadata_index(self) -> None:
        """Crée un index des métadonnées pour faciliter la recherche"""
        logger.info("Création de l'index des métadonnées")
        
        try:
            metadata_dir = os.path.join(self.output_dir, "metadata")
            metadata_files = [f for f in os.listdir(metadata_dir) if f.endswith('_metadata.json')]
            
            all_metadata = []
            
            for metadata_file in metadata_files:
                file_path = os.path.join(metadata_dir, metadata_file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    all_metadata.append(metadata)
            
            # Créer un DataFrame pandas pour faciliter les opérations
            df = pd.DataFrame(all_metadata)
            
            # Sauvegarder l'index au format CSV et JSON
            csv_path = os.path.join(self.output_dir, "metadata_index.csv")
            json_path = os.path.join(self.output_dir, "metadata_index.json")
            
            df.to_csv(csv_path, index=False)
            df.to_json(json_path, orient='records', force_ascii=False, indent=2)
            
            logger.info(f"Index des métadonnées créé: {csv_path} et {json_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'index des métadonnées: {str(e)}")
    
    def process_all(self) -> None:
        """Traite tous les fichiers dans le répertoire d'entrée"""
        logger.info("Début du traitement de tous les fichiers")
        
        try:
            # Traiter les codes
            codes_dir = os.path.join(self.input_dir, "codes")
            if os.path.exists(codes_dir):
                code_files = [os.path.join(codes_dir, f) for f in os.listdir(codes_dir) if f.endswith('.json')]
                for code_file in code_files:
                    self.process_code(code_file)
            
            # Traiter les articles
            articles_dir = os.path.join(self.input_dir, "articles")
            if os.path.exists(articles_dir):
                article_files = [os.path.join(articles_dir, f) for f in os.listdir(articles_dir) if f.endswith('.json')]
                for article_file in article_files:
                    self.process_article(article_file)
            
            # Traiter la jurisprudence
            jurisprudence_dir = os.path.join(self.input_dir, "jurisprudence")
            if os.path.exists(jurisprudence_dir):
                jurisprudence_files = [os.path.join(jurisprudence_dir, f) for f in os.listdir(jurisprudence_dir) if f.endswith('.json')]
                for jurisprudence_file in jurisprudence_files:
                    self.process_jurisprudence(jurisprudence_file)
            
            # Créer l'index des métadonnées
            self.create_metadata_index()
            
            logger.info("Traitement de tous les fichiers terminé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des fichiers: {str(e)}")


if __name__ == "__main__":
    try:
        # Définir les répertoires d'entrée et de sortie
        input_dir = "/home/ubuntu/legal_ai_project/data/legifrance"
        output_dir = "/home/ubuntu/legal_ai_project/data/processed"
        
        # Initialiser le processeur
        processor = LegalTextProcessor(input_dir, output_dir)
        
        # Exécuter le traitement
        processor.process_all()
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du script: {str(e)}")
