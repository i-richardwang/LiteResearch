"""
Langfuse tools class, providing unified monitoring configuration and management
"""

import os
import logging
import uuid
from typing import Optional, Dict, Any
from langfuse.langchain import CallbackHandler

logger = logging.getLogger(__name__)


class LangfuseManager:
    """
    Langfuse monitoring manager for unified management of LLM call monitoring
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangfuseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._enabled = self._check_langfuse_config()
            self._initialized = True
    
    def _check_langfuse_config(self) -> bool:
        """
        Check if langfuse configuration is available
        
        Returns:
            bool: Returns True if configuration is complete, otherwise False
        """
        langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        
        if langfuse_secret_key and langfuse_public_key:
            logger.info("✅ Langfuse configuration detected successfully")
            return True
        else:
            logger.warning("⚠️  Langfuse configuration not fully set up, monitoring will be disabled")
            return False
    
    def get_callback_handler(self, trace_name: Optional[str] = None, 
                           metadata: Optional[Dict[str, Any]] = None,
                           session_id: Optional[str] = None) -> Optional[CallbackHandler]:
        """
        Get langfuse callback handler
        
        Args:
            trace_name: Optional trace name
            metadata: Optional metadata
            session_id: Optional session ID
            
        Returns:
            CallbackHandler or None: Returns callback handler if langfuse is available, otherwise None
        """
        if not self._enabled:
            return None
        
        try:
            handler = CallbackHandler()
            if trace_name:
                handler.trace_name = trace_name
            if metadata:
                handler.metadata = metadata
            if session_id:
                handler.session_id = session_id
            return handler
        except Exception as e:
            logger.error(f"❌ Failed to create Langfuse callback handler: {e}")
            return None
    
    def get_config_with_callbacks(self, trace_name: Optional[str] = None,
                                 metadata: Optional[Dict[str, Any]] = None,
                                 existing_config: Optional[Dict[str, Any]] = None,
                                 session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration dictionary containing langfuse callbacks
        
        Args:
            trace_name: Optional trace name
            metadata: Optional metadata
            existing_config: Existing configuration dictionary
            session_id: Optional session ID
            
        Returns:
            Dict[str, Any]: Configuration dictionary containing callbacks
        """
        config = existing_config.copy() if existing_config else {}
        
        handler = self.get_callback_handler(trace_name, metadata, session_id)
        if handler:
            if "callbacks" not in config:
                config["callbacks"] = []
            config["callbacks"].append(handler)
        
        return config
    
    @property
    def is_enabled(self) -> bool:
        """
        Check if langfuse is enabled
        
        Returns:
            bool: Returns True if enabled
        """
        return self._enabled


# Create global instance
langfuse_manager = LangfuseManager()


def get_langfuse_config(trace_name: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       existing_config: Optional[Dict[str, Any]] = None,
                       session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function: Get configuration containing langfuse callbacks
    
    Args:
        trace_name: Optional trace name
        metadata: Optional metadata
        existing_config: Existing configuration dictionary
        session_id: Optional session ID
        
    Returns:
        Dict[str, Any]: Configuration dictionary containing callbacks
    """
    # Add application identifier to metadata
    enhanced_metadata = {"application": "LiteResearch"}
    if metadata:
        enhanced_metadata.update(metadata)
    
    return langfuse_manager.get_config_with_callbacks(trace_name, enhanced_metadata, existing_config, session_id)


def get_langfuse_handler(trace_name: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None,
                        session_id: Optional[str] = None) -> Optional[CallbackHandler]:
    """
    Convenience function: Get langfuse callback handler
    
    Args:
        trace_name: Optional trace name
        metadata: Optional metadata
        session_id: Optional session ID
        
    Returns:
        CallbackHandler or None: Callback handler
    """
    # Add application identifier to metadata
    enhanced_metadata = {"application": "LiteResearch"}
    if metadata:
        enhanced_metadata.update(metadata)
    
    return langfuse_manager.get_callback_handler(trace_name, enhanced_metadata, session_id)


def generate_session_id() -> str:
    """
    Generate a new session ID
    
    Returns:
        str: Unique session ID (UUID format)
    """
    return str(uuid.uuid4()) 