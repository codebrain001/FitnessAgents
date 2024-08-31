from llama_index.core import (
    SimpleDirectoryReader,
    DocumentSummaryIndex,
    VectorStoreIndex,
    StorageContext,
    Settings,
    get_response_synthesizer
)

from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.nomic import NomicEmbedding
from crewai_tools import LlamaIndexTool

import os
import logging
import sys
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()
# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Vector store persistent directory
persist_vector_store_path = 'src/tools/data/chromadb/'

openai_api_key = os.getenv("OPENAI_API_KEY")
nomic_api_key = os.getenv("NOMIC_API_KEY")
model_name = os.getenv("OPENAI_MODEL_NAME")

class MedicalReportRagPipeline:
    """
    Class for a RAG pipeline for medical report to create a summarization and semantic search indices.
    """
    def __init__(self, document_dir):
        self.document_dir = document_dir
        # Define LLM to be utilize for the RAG pipeline
        self.llm = OpenAI(api_key=openai_api_key, model=model_name)
        self.embed_model = NomicEmbedding( 
            api_key=nomic_api_key,
            dimensionality=768,
            model_name="nomic-embed-text-v1.5"
        )
        self.documents = self.load_documents()
        self.initialize_models()
        self.chroma_client = self.initialize_vector_store_client()
        self.summary_index = self.create_summary_index()
        self.semantic_search_index = self.create_vector_store_index()

    def load_documents(self):
        """
        Load documents from the specified directory.
        """
        try:
            reader = SimpleDirectoryReader(input_dir=self.document_dir, required_exts=['.pdf', '.docx', '.txt', '.md', 'mp3', '.mp4'])
            documents = reader.load_data()
            return documents
        except Exception as e:
            logging.error(f"Error loading documents: {e}")
            return []
        
    def initialize_models(self):
        """
        Initialize LLM and embedding models based on the specified type for query engines.
        """
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.text_splitter = SemanticSplitterNodeParser(
            buffer_size=1, breakpoint_percentile_threshold=95, embed_model=Settings.embed_model
        )

    def initialize_vector_store_client(self):
        """
        Initialize the Chroma vector store client
        """
        try:
            chroma_client = chromadb.PersistentClient(path=persist_vector_store_path, settings=ChromaSettings(allow_reset=True))
            logging.info(f"Chroma DB client created successfully")
            return chroma_client
        except Exception as e:
            logging.error(f"Error iinitializing vector store client: {e}")
            return None
        
    def create_chroma_db_collection(self, chroma_client, collection_name):
        """
        Create or load a Chroma DB collection for storing vectors.
        """
        try:
            chroma_collection = chroma_client.get_or_create_collection(collection_name)
            vector_store_instance = ChromaVectorStore(chroma_collection=chroma_collection)
            logging.info(f"Chroma DB collection created or loaded successfully: {collection_name}")
            return vector_store_instance

        except Exception as e:
            logging.error(f"Error creating Chroma DB collection: {e}")
            return None

    def create_summary_index(self, collection_name='input-summary'):
        """
        Create a summary index for the loaded documents.
        """
    
        try:
            logging.info(f"Creating or loading summary vector store with collection name: {collection_name}")
            summary_vector_store_instance = self.create_chroma_db_collection(
                self.chroma_client,
                collection_name,
            )
            if not summary_vector_store_instance:
                logging.error("Failed to create or load summary vector store instance.")
                return None

            summary_storage_context = StorageContext.from_defaults(vector_store=summary_vector_store_instance)
            response_synthesizer = get_response_synthesizer(
                llm=Settings.llm, response_mode="tree_summarize", use_async=True
            )
            
            logging.info("Creating DocumentSummaryIndex from documents")
            summary_index = DocumentSummaryIndex.from_documents(
                documents=self.documents,
                llm=Settings.llm,
                transformations=[Settings.text_splitter],
                response_synthesizer=response_synthesizer,
                storage_context=summary_storage_context,
                embed_model=Settings.embed_model,
                show_progress=True,
            )
            logging.info("DocumentSummaryIndex created successfully")
            return summary_index
        except Exception as e:
            logging.error(f"Error creating summary index: {e}")
            return None

    def create_vector_store_index(self, collection_name='input-semantic-search'):
        """
        Create a vector store index for semantic search.
        """
        try:
            logging.info(f"Creating or loading semantic search vector store with collection name: {collection_name}")
            semantic_search_vector_store_instance = self.create_chroma_db_collection(
                self.chroma_client,
                collection_name,
            )
            if not semantic_search_vector_store_instance:
                logging.error("Failed to create or load semantic search vector store instance.")
                return None

            semantic_search_storage_context = StorageContext.from_defaults(vector_store=semantic_search_vector_store_instance)

            logging.info("Creating vector store index from documents")
            vector_store_index = VectorStoreIndex.from_documents(
                documents=self.documents,
                llm=Settings.llm,
                transformations=[Settings.text_splitter],
                embed_model=Settings.embed_model,
                storage_context=semantic_search_storage_context,
                show_progress=True,
            )
            logging.info("Vector store index created successfully")
            return vector_store_index
        except Exception as e:
            logging.error(f"Error creating vector store index: {e}")
            return None

    def create_tools(self):
        """
        Create query engine tools for interacting with the summary and vector store indices.
        """
        try:
            self.summary_query_engine = self.summary_index.as_query_engine(response_mode="tree_summarize", use_async=True)
            self.vector_store_query_engine = self.semantic_search_index.as_query_engine(similarity_top_k=5, llm=Settings.llm)
            self.summary_tool = LlamaIndexTool.from_query_engine(
                self.summary_query_engine,
                name="Summary Index Query Tool",
                description="Use this tool to query summaries over the given document(s)."
            )
            self.vector_store_tool = LlamaIndexTool.from_query_engine(
                self.vector_store_query_engine,
                name="Vector Store Index Query Tool",
                description="Use this tool to semantic search over the given document(s)."
            )
            return self.summary_tool, self.vector_store_tool
        except Exception as e:
            logging.error(f"Error creating query engine tools: {e}")
            return None, None