#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'indexation vectorielle des textes juridiques pour l'assistant juridique IA
Ce script génère des embeddings pour les textes juridiques et les indexe dans Pinecone
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import pinecone

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vector_indexer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vector_indexer")

# Chargement des variables d'environnement
load_dotenv()

class VectorIndexer:
    """Classe pour générer des embeddings et indexer les textes juridiques dans Pinecone"""
    
    def __init__(self, input_dir: str, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        """
        Initialisation de l'indexeur vectoriel
        
        Args:
            input_dir: Répertoire contenant les données structurées
            model_name: Nom du modèle SentenceTransformer à utiliser
        """
        self.input_dir = input_dir
        self.model_name = model_name
        
        # Initialiser le modèle de génération d'embeddings
        logger.info(f"Chargement du modèle d'embeddings: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Initialiser Pinecone
        self._init_pinecone()
        
        logger.info(f"Indexeur vectoriel initialisé avec répertoire d'entrée: {input_dir}")
    
    def _init_pinecone(self) -> None:
        """Initialise la connexion à Pinecone"""
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
        
        if not pinecone_api_key:
            logger.error("Clé API Pinecone manquante. Définissez PINECONE_API_KEY")
            raise ValueError("Clé API Pinecone manquante")
        
        logger.info(f"Initialisation de Pinecone dans l'environnement: {pinecone_environment}")
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
        
        # Vérifier si l'index existe, sinon le créer
        index_name = os.getenv("PINECONE_INDEX_NAME", "legal-assistant")
        dimension = self.model.get_sentence_embedding_dimension()
        
        if index_name not in pinecone.list_indexes():
            logger.info(f"Création de l'index Pinecone: {index_name} avec dimension: {dimension}")
            pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine"
            )
        
        self.index = pinecone.Index(index_name)
        logger.info(f"Connexion à l'index Pinecone: {index_name} établie")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding pour un texte
        
        Args:
            text: Texte à encoder
            
        Returns:
            List[float]: Vecteur d'embedding
        """
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 128) -> List[str]:
        """
        Découpe un texte en chunks pour l'indexation
        
        Args:
            text: Texte à découper
            chunk_size: Taille des chunks en caractères
            overlap: Chevauchement entre les chunks
            
        Returns:
            List[str]: Liste des chunks de texte
        """
        chunks = []
        
        if len(text) <= chunk_size:
            chunks.append(text)
        else:
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                # Ajuster la fin pour ne pas couper un mot
                if end < len(text):
                    # Trouver le dernier espace avant la fin
                    while end > start and text[end] != ' ':
                        end -= 1
                    if end == start:  # Si aucun espace n'est trouvé, utiliser la taille maximale
                        end = start + chunk_size
                
                chunks.append(text[start:end])
                start = end - overlap
        
        return chunks
    
    def index_article(self, article_file: str) -> None:
        """
        Indexe un article juridique dans Pinecone
        
        Args:
            article_file: Chemin vers le fichier JSON de l'article structuré
        """
        logger.info(f"Indexation de l'article: {article_file}")
        
        try:
            # Charger le fichier JSON
            with open(article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
            
            article_id = article_data.get('id', '')
            content = article_data.get('content', '')
            metadata = article_data.get('metadata', {})
            
            # Découper le contenu en chunks
            chunks = self.chunk_text(content)
            
            # Générer et indexer les embeddings pour chaque chunk
            vectors = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{article_id}_chunk_{i}"
                embedding = self.generate_embedding(chunk)
                
                # Préparer les métadonnées
                chunk_metadata = {
                    "original_id": article_id,
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "text": chunk[:1000],  # Limiter la taille du texte dans les métadonnées
                    "type": "ARTICLE",
                }
                
                # Ajouter les métadonnées de l'article
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        chunk_metadata[f"article_{key}"] = value
                
                vectors.append((chunk_id, embedding, chunk_metadata))
            
            # Indexer les vecteurs par lots
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                ids = [item[0] for item in batch]
                embeddings = [item[1] for item in batch]
                metadatas = [item[2] for item in batch]
                
                self.index.upsert(vectors=zip(ids, embeddings, metadatas))
            
            logger.info(f"Article {article_id} indexé avec {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation de l'article {article_file}: {str(e)}")
    
    def index_jurisprudence(self, jurisprudence_file: str) -> None:
        """
        Indexe une décision de jurisprudence dans Pinecone
        
        Args:
            jurisprudence_file: Chemin vers le fichier JSON de la jurisprudence structurée
        """
        logger.info(f"Indexation de la jurisprudence: {jurisprudence_file}")
        
        try:
            # Charger le fichier JSON
            with open(jurisprudence_file, 'r', encoding='utf-8') as f:
                jurisprudence_data = json.load(f)
            
            jurisprudence_id = jurisprudence_data.get('id', '')
            content = jurisprudence_data.get('content', '')
            metadata = jurisprudence_data.get('metadata', {})
            
            # Découper le contenu en chunks
            chunks = self.chunk_text(content)
            
            # Générer et indexer les embeddings pour chaque chunk
            vectors = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{jurisprudence_id}_chunk_{i}"
                embedding = self.generate_embedding(chunk)
                
                # Préparer les métadonnées
                chunk_metadata = {
                    "original_id": jurisprudence_id,
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "text": chunk[:1000],  # Limiter la taille du texte dans les métadonnées
                    "type": "JURISPRUDENCE",
                }
                
                # Ajouter les métadonnées de la jurisprudence
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        chunk_metadata[f"jurisprudence_{key}"] = value
                
                vectors.append((chunk_id, embedding, chunk_metadata))
            
            # Indexer les vecteurs par lots
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i+batch_size]
                ids = [item[0] for item in batch]
                embeddings = [item[1] for item in batch]
                metadatas = [item[2] for item in batch]
                
                self.index.upsert(vectors=zip(ids, embeddings, metadatas))
            
            logger.info(f"Jurisprudence {jurisprudence_id} indexée avec {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation de la jurisprudence {jurisprudence_file}: {str(e)}")
    
    def search_similar(self, query: str, top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict]:
        """
        Recherche des textes similaires à une requête
        
        Args:
            query: Texte de la requête
            top_k: Nombre de résultats à retourner
            filter: Filtre à appliquer sur les métadonnées
            
        Returns:
            List[Dict]: Liste des résultats similaires
        """
        logger.info(f"Recherche de textes similaires à: {query}")
        
        try:
            # Générer l'embedding de la requête
            query_embedding = self.generate_embedding(query)
            
            # Effectuer la recherche
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            return results.get('matches', [])
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            return []
    
    def index_all(self) -> None:
        """Indexe tous les fichiers structurés dans le répertoire d'entrée"""
        logger.info("Début de l'indexation de tous les fichiers")
        
        try:
            structured_dir = os.path.join(self.input_dir, "structured")
            if not os.path.exists(structured_dir):
                logger.error(f"Le répertoire {structured_dir} n'existe pas")
                return
            
            # Lister tous les fichiers structurés
            files = [f for f in os.listdir(structured_dir) if f.endswith('_structured.json')]
            
            for file in files:
                file_path = os.path.join(structured_dir, file)
                
                # Déterminer le type de fichier
                if "JURI" in file:
                    self.index_jurisprudence(file_path)
                else:
                    self.index_article(file_path)
            
            logger.info(f"Indexation terminée pour {len(files)} fichiers")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation des fichiers: {str(e)}")


class BusinessTaxLawSearcher:
    """Classe spécialisée pour la recherche dans le domaine du droit des affaires et fiscal"""
    
    def __init__(self, indexer: VectorIndexer):
        """
        Initialisation du chercheur spécialisé
        
        Args:
            indexer: Instance de VectorIndexer
        """
        self.indexer = indexer
        logger.info("Chercheur spécialisé en droit des affaires et fiscal initialisé")
    
    def search_business_law(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Recherche dans le domaine du droit des affaires
        
        Args:
            query: Texte de la requête
            top_k: Nombre de résultats à retourner
            
        Returns:
            List[Dict]: Liste des résultats pertinents
        """
        logger.info(f"Recherche en droit des affaires: {query}")
        
        # Filtre pour le droit des affaires (Code de commerce, etc.)
        filter = {
            "$or": [
                {"article_code_id": "LEGITEXT000005634379"},  # Code de commerce
                {"article_code_id": "LEGITEXT000006072026"},  # Code monétaire et financier
                {"jurisprudence_jurisdiction": "COUR_CASSATION"}
            ]
        }
        
        return self.indexer.search_similar(query, top_k, filter)
    
    def search_tax_law(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Recherche dans le domaine du droit fiscal
        
        Args:
            query: Texte de la requête
            top_k: Nombre de résultats à retourner
            
        Returns:
            List[Dict]: Liste des résultats pertinents
        """
        logger.info(f"Recherche en droit fiscal: {query}")
        
        # Filtre pour le droit fiscal (Code général des impôts, etc.)
        filter = {
            "$or": [
                {"article_code_id": "LEGITEXT000006069577"},  # Code général des impôts
                {"jurisprudence_jurisdiction": "CONSEIL_ETAT"}
            ]
        }
        
        return self.indexer.search_similar(query, top_k, filter)
    
    def search_combined(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Recherche combinée dans les domaines du droit des affaires et fiscal
        
        Args:
            query: Texte de la requête
            top_k: Nombre de résultats à retourner
            
        Returns:
            List[Dict]: Liste des résultats pertinents
        """
        logger.info(f"Recherche combinée en droit des affaires et fiscal: {query}")
        
        # Obtenir les résultats des deux domaines
        business_results = self.search_business_law(query, top_k // 2)
        tax_results = self.search_tax_law(query, top_k // 2)
        
        # Combiner et trier les résultats par score
        combined_results = business_results + tax_results
        combined_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return combined_results[:top_k]


if __name__ == "__main__":
    try:
        # Définir le répertoire d'entrée
        input_dir = "/home/ubuntu/legal_ai_project/data/processed"
        
        # Initialiser l'indexeur vectoriel
        indexer = VectorIndexer(input_dir)
        
        # Indexer tous les fichiers
        indexer.index_all()
        
        # Tester la recherche
        searcher = BusinessTaxLawSearcher(indexer)
        
        # Exemple de recherche en droit des affaires
        business_query = "Quelles sont les étapes pour créer une SAS ?"
        business_results = searcher.search_business_law(business_query)
        logger.info(f"Résultats pour la recherche en droit des affaires: {len(business_results)}")
        
        # Exemple de recherche en droit fiscal
        tax_query = "Quel est le taux d'imposition pour une PME ?"
        tax_results = searcher.search_tax_law(tax_query)
        logger.info(f"Résultats pour la recherche en droit fiscal: {len(tax_results)}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du script: {str(e)}")
