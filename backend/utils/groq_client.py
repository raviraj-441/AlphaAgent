"""
Groq API client for LLM integration.
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class GroqLLMClient:
    """
    Client for integrating with Groq API.
    Supports chat-based interactions using latest LLaMA models.
    Includes automatic model fallback on rate limits.
    """
    
    # Model priority list - will fallback in order if rate limit hit
    AVAILABLE_MODELS = [
        "llama-3.1-8b-instant",      # Primary (fastest)
        "llama-3.2-3b-preview",      # Fallback 1 (smaller, faster)
        "llama-3.1-70b-versatile",   # Fallback 2 (slower but more capable)
        "mixtral-8x7b-32768",        # Fallback 3 (alternative architecture)
        "gemma2-9b-it",              # Fallback 4 (Google's model)
    ]
    
    DEFAULT_MODEL = AVAILABLE_MODELS[0]
    API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq LLM Client.
        
        Args:
            api_key: Groq API key. If None, reads from GROQ_API_KEY env variable.
        
        Raises:
            ValueError: If API key is not provided and env variable not set.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Groq API key not provided. Set GROQ_API_KEY environment variable or "
                "pass api_key parameter."
            )
        
        self.model = self.DEFAULT_MODEL
        self.current_model_index = 0
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        logger.info(f"GroqLLMClient initialized with model: {self.model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 1.0,
    ) -> str:
        """
        Send a chat message to Groq API and get response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
        
        Returns:
            Assistant's reply text
        
        Raises:
            RuntimeError: If API request fails
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        
        try:
            logger.debug(f"Sending request to Groq API with {len(messages)} messages")
            
            response = self.session.post(
                self.API_ENDPOINT,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise RuntimeError("Invalid API response: no choices returned")
            
            assistant_message = result["choices"][0]["message"]["content"]
            
            usage = result.get("usage", {})
            logger.info(
                f"Groq API call successful. "
                f"Input tokens: {usage.get('prompt_tokens', 0)}, "
                f"Output tokens: {usage.get('completion_tokens', 0)}"
            )
            
            return assistant_message
        
        except requests.exceptions.Timeout:
            logger.error("Groq API request timed out")
            raise RuntimeError("Groq API request timed out after 30 seconds")
        
        except requests.exceptions.HTTPError as e:
            # Check if it's a rate limit error
            if e.response.status_code == 429:
                error_data = e.response.json() if e.response.content else {}
                error_msg = error_data.get("error", {}).get("message", "")
                
                # Try to switch to next available model
                if self.current_model_index < len(self.AVAILABLE_MODELS) - 1:
                    self.current_model_index += 1
                    old_model = self.model
                    self.model = self.AVAILABLE_MODELS[self.current_model_index]
                    
                    logger.warning(
                        f"Rate limit hit on {old_model}. "
                        f"Switching to fallback model: {self.model}"
                    )
                    
                    # Retry with new model
                    payload["model"] = self.model
                    try:
                        response = self.session.post(
                            self.API_ENDPOINT,
                            json=payload,
                            timeout=30
                        )
                        response.raise_for_status()
                        result = response.json()
                        
                        if "choices" not in result or not result["choices"]:
                            raise RuntimeError("Invalid API response: no choices returned")
                        
                        assistant_message = result["choices"][0]["message"]["content"]
                        
                        usage = result.get("usage", {})
                        logger.info(
                            f"Groq API call successful with fallback model {self.model}. "
                            f"Input tokens: {usage.get('prompt_tokens', 0)}, "
                            f"Output tokens: {usage.get('completion_tokens', 0)}"
                        )
                        
                        return assistant_message
                        
                    except Exception as retry_error:
                        logger.error(f"Fallback model {self.model} also failed: {retry_error}")
                        raise RuntimeError(f"Groq API error (after model fallback): {e.response.text}")
                else:
                    logger.error(f"All models exhausted. Rate limit error: {error_msg}")
                    raise RuntimeError(f"Groq API error (all models rate limited): {e.response.text}")
            
            # Non-rate-limit HTTP errors
            logger.error(f"Groq API HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"Groq API error: {e.response.text}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {e}")
            raise RuntimeError(f"Failed to communicate with Groq API: {e}")
        
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse Groq API response: {e}")
            raise RuntimeError(f"Failed to parse API response: {e}")
    
    def chat_with_system(
        self,
        user_message: str,
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send a message with system prompt to Groq API.
        
        Args:
            user_message: The user's message
            system_prompt: System prompt for context
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        
        Returns:
            Assistant's reply text
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return self.chat(messages, temperature=temperature, max_tokens=max_tokens)
    
    def json_chat(
        self,
        user_message: str,
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Get JSON-formatted response from Groq API.
        
        Args:
            user_message: The user's message
            system_prompt: System prompt (should instruct JSON output)
            temperature: Sampling temperature (lower for consistency)
            max_tokens: Maximum tokens in response
        
        Returns:
            Parsed JSON response as dict
        
        Raises:
            ValueError: If response is not valid JSON
        """
        response_text = self.chat_with_system(
            user_message,
            system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return json.loads(response_text)
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_text}")
            raise ValueError(f"Response is not valid JSON: {e}")
    
    def batch_chat(
        self,
        messages_list: List[List[Dict[str, str]]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> List[str]:
        """
        Send multiple chat requests sequentially.
        
        Args:
            messages_list: List of message lists
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response
        
        Returns:
            List of assistant replies
        """
        results = []
        for messages in messages_list:
            try:
                result = self.chat(messages, temperature, max_tokens)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch chat error: {e}")
                results.append(f"Error: {str(e)}")
        
        return results
    
    def set_model(self, model: str):
        """
        Change the model being used.
        
        Args:
            model: Model name to use
        """
        if model in self.AVAILABLE_MODELS:
            self.model = model
            self.current_model_index = self.AVAILABLE_MODELS.index(model)
            logger.info(f"Model changed to: {self.model} (index {self.current_model_index})")
        else:
            logger.warning(f"Model {model} not in available models list. Using anyway.")
            self.model = model
    
    def reset_model(self):
        """Reset to the default primary model."""
        self.model = self.DEFAULT_MODEL
        self.current_model_index = 0
        logger.info(f"Model reset to default: {self.model}")
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about current model and available fallbacks."""
        return {
            "current_model": self.model,
            "model_index": self.current_model_index,
            "available_models": self.AVAILABLE_MODELS,
            "api_endpoint": self.API_ENDPOINT,
            "max_tokens_default": 2048
        }
