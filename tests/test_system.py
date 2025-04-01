#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de tests pour l'assistant juridique IA
Ce script teste les différents composants du système
"""

import os
import json
import logging
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import requests
from dotenv import load_dotenv

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tests.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("tests")

# Chargement des variables d'environnement
load_dotenv()
load_dotenv('.env.legifrance')
load_dotenv('.env.pinecone')
load_dotenv('.env.llm')
load_dotenv('.env.auth')


class TestLegifranceCollector(unittest.TestCase):
    """Tests pour le collecteur de données Légifrance"""
    
    @patch('scripts.legifrance_collector.LegifranceAPI')
    def test_api_initialization(self, mock_api):
        """Teste l'initialisation de l'API Légifrance"""
        from scripts.legifrance_collector import LegifranceAPI
        
        # Configurer le mock
        mock_api.return_value = MagicMock()
        
        # Tester l'initialisation
        api = LegifranceAPI()
        self.assertIsNotNone(api)
        
        logger.info("Test d'initialisation de l'API Légifrance réussi")
    
    @patch('scripts.legifrance_collector.LegifranceAPI')
    def test_collector_initialization(self, mock_api):
        """Teste l'initialisation du collecteur"""
        from scripts.legifrance_collector import BusinessTaxLawCollector
        
        # Configurer le mock
        mock_api.return_value = MagicMock()
        
        # Tester l'initialisation
        collector = BusinessTaxLawCollector(mock_api.return_value, output_dir="./test_data")
        self.assertIsNotNone(collector)
        self.assertEqual(collector.output_dir, "./test_data")
        
        logger.info("Test d'initialisation du collecteur réussi")
    
    @patch('scripts.legifrance_collector.LegifranceAPI')
    def test_code_collection(self, mock_api):
        """Teste la collecte des codes juridiques"""
        from scripts.legifrance_collector import BusinessTaxLawCollector
        
        # Configurer le mock
        api_instance = mock_api.return_value
        api_instance.get_code_content.return_value = {"title": "Code de test", "content": "Contenu de test"}
        
        # Tester la collecte
        collector = BusinessTaxLawCollector(api_instance, output_dir="./test_data")
        
        # Créer le répertoire de test
        os.makedirs("./test_data/codes", exist_ok=True)
        
        # Exécuter la méthode
        collector.collect_codes()
        
        # Vérifier que la méthode a été appelée pour chaque code
        self.assertEqual(api_instance.get_code_content.call_count, len(collector.RELEVANT_CODES))
        
        logger.info("Test de collecte des codes réussi")


class TestLegalTextProcessor(unittest.TestCase):
    """Tests pour le processeur de textes juridiques"""
    
    def setUp(self):
        """Configuration des tests"""
        # Créer les répertoires de test
        os.makedirs("./test_data/input/codes", exist_ok=True)
        os.makedirs("./test_data/input/articles", exist_ok=True)
        os.makedirs("./test_data/output/structured", exist_ok=True)
        os.makedirs("./test_data/output/metadata", exist_ok=True)
        
        # Créer un fichier de test
        with open("./test_data/input/codes/test_code.json", "w") as f:
            json.dump({
                "title": "Code de test",
                "structure": [
                    {
                        "id": "TITRE_1",
                        "title": "Titre 1",
                        "level": 1,
                        "children": [
                            {
                                "id": "CHAPITRE_1",
                                "title": "Chapitre 1",
                                "level": 2
                            }
                        ]
                    }
                ]
            }, f)
        
        with open("./test_data/input/articles/test_article.json", "w") as f:
            json.dump({
                "article": {
                    "id": "TEST_ARTICLE",
                    "title": "Article de test",
                    "num": "L123-45",
                    "content": "Contenu de l'article de test",
                    "codeId": "TEST_CODE",
                    "codeName": "Code de test"
                }
            }, f)
    
    def tearDown(self):
        """Nettoyage après les tests"""
        # Supprimer les fichiers de test
        import shutil
        if os.path.exists("./test_data"):
            shutil.rmtree("./test_data")
    
    def test_processor_initialization(self):
        """Teste l'initialisation du processeur"""
        from scripts.legifrance_processor import LegalTextProcessor
        
        processor = LegalTextProcessor(
            input_dir="./test_data/input",
            output_dir="./test_data/output"
        )
        
        self.assertIsNotNone(processor)
        self.assertEqual(processor.input_dir, "./test_data/input")
        self.assertEqual(processor.output_dir, "./test_data/output")
        
        logger.info("Test d'initialisation du processeur réussi")
    
    def test_code_processing(self):
        """Teste le traitement d'un code juridique"""
        from scripts.legifrance_processor import LegalTextProcessor
        
        processor = LegalTextProcessor(
            input_dir="./test_data/input",
            output_dir="./test_data/output"
        )
        
        # Traiter le code
        metadata = processor.process_code("./test_data/input/codes/test_code.json")
        
        # Vérifier les résultats
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["title"], "Code de test")
        self.assertTrue(os.path.exists("./test_data/output/metadata/test_code_metadata.json"))
        
        logger.info("Test de traitement de code réussi")
    
    def test_article_processing(self):
        """Teste le traitement d'un article juridique"""
        from scripts.legifrance_processor import LegalTextProcessor
        
        processor = LegalTextProcessor(
            input_dir="./test_data/input",
            output_dir="./test_data/output"
        )
        
        # Traiter l'article
        article = processor.process_article("./test_data/input/articles/test_article.json")
        
        # Vérifier les résultats
        self.assertIsNotNone(article)
        self.assertEqual(article["metadata"]["code_name"], "Code de test")
        self.assertTrue(os.path.exists("./test_data/output/structured/test_article_structured.json"))
        
        logger.info("Test de traitement d'article réussi")


class TestVectorIndexer(unittest.TestCase):
    """Tests pour l'indexeur vectoriel"""
    
    @patch('scripts.vector_indexer.SentenceTransformer')
    @patch('scripts.vector_indexer.pinecone')
    def test_indexer_initialization(self, mock_pinecone, mock_transformer):
        """Teste l'initialisation de l'indexeur vectoriel"""
        from scripts.vector_indexer import VectorIndexer
        
        # Configurer les mocks
        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.get_sentence_embedding_dimension.return_value = 768
        
        mock_pinecone.list_indexes.return_value = []
        mock_pinecone.Index.return_value = MagicMock()
        
        # Tester l'initialisation
        indexer = VectorIndexer(input_dir="./test_data")
        
        self.assertIsNotNone(indexer)
        self.assertEqual(indexer.input_dir, "./test_data")
        
        # Vérifier que Pinecone a été initialisé
        mock_pinecone.init.assert_called_once()
        
        logger.info("Test d'initialisation de l'indexeur vectoriel réussi")
    
    @patch('scripts.vector_indexer.SentenceTransformer')
    @patch('scripts.vector_indexer.pinecone')
    def test_embedding_generation(self, mock_pinecone, mock_transformer):
        """Teste la génération d'embeddings"""
        from scripts.vector_indexer import VectorIndexer
        
        # Configurer les mocks
        model_instance = MagicMock()
        model_instance.encode.return_value = [0.1, 0.2, 0.3]
        model_instance.get_sentence_embedding_dimension.return_value = 3
        
        mock_transformer.return_value = model_instance
        mock_pinecone.list_indexes.return_value = []
        mock_pinecone.Index.return_value = MagicMock()
        
        # Tester la génération d'embeddings
        indexer = VectorIndexer(input_dir="./test_data")
        embedding = indexer.generate_embedding("Texte de test")
        
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding), 3)
        model_instance.encode.assert_called_with("Texte de test")
        
        logger.info("Test de génération d'embeddings réussi")
    
    @patch('scripts.vector_indexer.SentenceTransformer')
    @patch('scripts.vector_indexer.pinecone')
    def test_text_chunking(self, mock_pinecone, mock_transformer):
        """Teste le découpage de texte en chunks"""
        from scripts.vector_indexer import VectorIndexer
        
        # Configurer les mocks
        mock_transformer.return_value = MagicMock()
        mock_transformer.return_value.get_sentence_embedding_dimension.return_value = 768
        
        mock_pinecone.list_indexes.return_value = []
        mock_pinecone.Index.return_value = MagicMock()
        
        # Tester le découpage
        indexer = VectorIndexer(input_dir="./test_data")
        
        # Texte court (pas de découpage)
        short_text = "Ceci est un texte court."
        chunks = indexer.chunk_text(short_text, chunk_size=100, overlap=20)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short_text)
        
        # Texte long (avec découpage)
        long_text = " ".join(["mot"] * 200)  # 200 mots
        chunks = indexer.chunk_text(long_text, chunk_size=100, overlap=20)
        self.assertTrue(len(chunks) > 1)
        
        logger.info("Test de découpage de texte réussi")


class TestResponseGenerator(unittest.TestCase):
    """Tests pour le générateur de réponses"""
    
    @patch('scripts.response_generator.anthropic')
    def test_generator_initialization_claude(self, mock_anthropic):
        """Teste l'initialisation du générateur avec Claude"""
        from scripts.response_generator import LegalResponseGenerator
        
        # Configurer le mock
        mock_anthropic.Anthropic.return_value = MagicMock()
        
        # Tester l'initialisation
        generator = LegalResponseGenerator(model_provider="claude")
        
        self.assertIsNotNone(generator)
        self.assertEqual(generator.model_provider, "claude")
        
        logger.info("Test d'initialisation du générateur avec Claude réussi")
    
    @patch('scripts.response_generator.openai')
    def test_generator_initialization_openai(self, mock_openai):
        """Teste l'initialisation du générateur avec OpenAI"""
        from scripts.response_generator import LegalResponseGenerator
        
        # Configurer le mock
        mock_openai.OpenAI.return_value = MagicMock()
        
        # Tester l'initialisation
        generator = LegalResponseGenerator(model_provider="openai")
        
        self.assertIsNotNone(generator)
        self.assertEqual(generator.model_provider, "openai")
        
        logger.info("Test d'initialisation du générateur avec OpenAI réussi")
    
    @patch('scripts.response_generator.anthropic')
    def test_prompt_creation(self, mock_anthropic):
        """Teste la création de prompts spécialisés"""
        from scripts.response_generator import LegalResponseGenerator
        
        # Configurer le mock
        mock_anthropic.Anthropic.return_value = MagicMock()
        
        # Tester la création de prompts
        generator = LegalResponseGenerator(model_provider="claude")
        
        # Créer des résultats de recherche fictifs
        search_results = [
            {
                "metadata": {
                    "type": "ARTICLE",
                    "text": "Contenu de l'article",
                    "article_code_name": "Code de commerce",
                    "article_num": "L123-45"
                }
            }
        ]
        
        # Tester le prompt pour le droit des affaires
        business_prompt = generator._create_business_law_prompt(
            query="Comment créer une SAS ?",
            search_results=search_results,
            user_profile="professionnel"
        )
        
        self.assertIsNotNone(business_prompt)
        self.assertIn("Comment créer une SAS ?", business_prompt)
        self.assertIn("Code de commerce", business_prompt)
        
        # Tester le prompt pour le droit fiscal
        tax_prompt = generator._create_tax_law_prompt(
            query="Quel est le taux d'IS ?",
            search_results=search_results,
            user_profile="particulier"
        )
        
        self.assertIsNotNone(tax_prompt)
        self.assertIn("Quel est le taux d'IS ?", tax_prompt)
        self.assertIn("clair et accessible", tax_prompt)
        
        logger.info("Test de création de prompts réussi")
    
    @patch('scripts.response_generator.anthropic')
    def test_domain_detection(self, mock_anthropic):
        """Teste la détection automatique du domaine juridique"""
        from scripts.response_generator import LegalResponseGenerator
        
        # Configurer le mock
        mock_anthropic.Anthropic.return_value = MagicMock()
        
        # Tester la détection de domaine
        generator = LegalResponseGenerator(model_provider="claude")
        
        # Requête de droit des affaires
        business_query = "Comment créer une SARL et quels sont les statuts nécessaires ?"
        domain = generator.detect_domain(business_query)
        self.assertEqual(domain, "business")
        
        # Requête de droit fiscal
        tax_query = "Quel est le taux d'imposition pour les BIC et comment déduire la TVA ?"
        domain = generator.detect_domain(tax_query)
        self.assertEqual(domain, "tax")
        
        logger.info("Test de détection de domaine réussi")


class TestAuthPayment(unittest.TestCase):
    """Tests pour le système d'authentification et de paiement"""
    
    def test_password_hashing(self):
        """Teste le hachage et la vérification des mots de passe"""
        from app.auth_payment import get_password_hash, verify_password
        
        # Tester le hachage
        password = "MotDePasse123!"
        hashed = get_password_hash(password)
        
        self.assertIsNotNone(hashed)
        self.assertTrue(len(hashed) > 0)
        
        # Tester la vérification
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("MauvaisMotDePasse", hashed))
        
        logger.info("Test de hachage et vérification de mot de passe réussi")
    
    def test_token_creation(self):
        """Teste la création de tokens JWT"""
        from app.auth_payment import create_access_token
        from datetime import timedelta
        import jwt
        
        # Tester la création de token
        data = {"sub": "user@example.com"}
        token = create_access_token(data, expires_delta=timedelta(minutes=15))
        
        self.assertIsNotNone(token)
        
        # Décoder le token pour vérifier
        from app.auth_payment import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        self.assertEqual(payload["sub"], "user@example.com")
        self.assertTrue("exp" in payload)
        
        logger.info("Test de création de token JWT réussi")
    
    @patch('app.auth_payment.stripe')
    def test_subscription_manager(self, mock_stripe):
        """Teste le gestionnaire d'abonnements"""
        from app.auth_payment import SubscriptionManager
        
        # Configurer le mock
        mock_stripe.Customer.create.return_value = MagicMock(id="cus_test123")
        mock_stripe.Subscription.create.return_value = MagicMock(
            id="sub_test123",
            status="active",
            current_period_end=1714503091  # Timestamp futur
        )
        
        # Tester la création de client Stripe
        customer_id = SubscriptionManager.create_stripe_customer(
            email="user@example.com",
            name="Test User"
        )
        
        self.assertEqual(customer_id, "cus_test123")
        
        # Tester la création d'abonnement
        subscription = SubscriptionManager.create_subscription(
            customer_id="cus_test123",
            plan_type="standard",
            payment_method_id="pm_test123"
        )
        
        self.assertEqual(subscription["id"], "sub_test123")
        self.assertEqual(subscription["status"], "active")
        
        logger.info("Test du gestionnaire d'abonnements réussi")


class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour l'assistant juridique IA"""
    
    @patch('scripts.vector_indexer.SentenceTransformer')
    @patch('scripts.vector_indexer.pinecone')
    @patch('scripts.response_generator.anthropic')
    def test_query_processing_flow(self, mock_anthropic, mock_pinecone, mock_transformer):
        """Teste le flux complet de traitement d'une requête"""
        from scripts.vector_indexer import VectorIndexer, BusinessTaxLawSearcher
        from scripts.response_generator import LegalResponseGenerator, LegalAssistantAPI
        
        # Configurer les mocks
        model_instance = MagicMock()
        model_instance.encode.return_value = [0.1, 0.2, 0.3]
        model_instance.get_sentence_embedding_dimension.return_value = 3
        
        mock_transformer.return_value = model_instance
        
        mock_pinecone.list_indexes.return_value = []
        index_instance = MagicMock()
        index_instance.query.return_value = {
            "matches": [
                {
                    "id": "test_id_1",
                    "score": 0.95,
                    "metadata": {
                        "type": "ARTICLE",
                        "text": "Contenu de l'article",
                        "article_code_name": "Code de commerce",
                        "article_num": "L123-45"
                    }
                }
            ]
        }
        mock_pinecone.Index.return_value = index_instance
        
        claude_instance = MagicMock()
        claude_instance.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Réponse juridique générée par Claude")]
        )
        mock_anthropic.Anthropic.return_value = claude_instance
        
        # Initialiser les composants
        indexer = VectorIndexer(input_dir="./test_data")
        searcher = BusinessTaxLawSearcher(indexer)
        response_generator = LegalResponseGenerator(model_provider="claude")
        legal_assistant = LegalAssistantAPI(searcher, response_generator)
        
        # Tester le traitement d'une requête
        query = "Comment créer une SAS en France ?"
        response = legal_assistant.process_query(query, user_profile="particulier")
        
        # Vérifier les résultats
        self.assertIsNotNone(response)
        self.assertEqual(response["query"], query)
        self.assertIn("response", response)
        self.assertIn("sources", response)
        
        logger.info("Test d'intégration du flux de traitement de requête réussi")
    
    def test_system_performance(self):
        """Teste les performances du système"""
        import time
        
        # Mesurer le temps de chargement des modules
        start_time = time.time()
        
        # Importer les modules principaux
        try:
            from scripts.legifrance_collector import LegifranceAPI, BusinessTaxLawCollector
            from scripts.legifrance_processor import LegalTextProcessor
            from scripts.vector_indexer import VectorIndexer, BusinessTaxLawSearcher
            from scripts.response_generator import LegalResponseGenerator, LegalAssistantAPI
            from app.auth_payment import app, User, Subscription
            
            load_time = time.time() - start_time
            logger.info(f"Temps de chargement des modules: {load_time:.2f} secondes")
            
            # Vérifier que le temps de chargement est raisonnable
            self.assertLess(load_time, 5.0, "Le temps de chargement des modules est trop long")
            
        except ImportError as e:
            self.fail(f"Erreur lors de l'importation des modules: {str(e)}")
        
        logger.info("Test de performance du système réussi")


def run_tests():
    """Exécute tous les tests"""
    # Créer le répertoire de test
    os.makedirs("./test_data", exist_ok=True)
    
    # Exécuter les tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    run_tests()
