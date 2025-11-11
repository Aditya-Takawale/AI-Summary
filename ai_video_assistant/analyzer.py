"""
Content analysis module for the AI-Powered Video Lecture Assistant.
Uses Ollama (local LLM) to analyze transcriptions and generate learning aids.
"""

import json
import logging
from typing import Dict
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaContentAnalyzer:
    """Analyzes lecture transcriptions using Ollama (local LLM)."""
    
    # System instruction for the AI model
    SYSTEM_INSTRUCTION = """You are an expert educational assistant and curriculum designer. Your task is to analyze a provided lecture transcription and generate a structured set of learning aids. The output must be in a single, valid JSON object.

Rules:

Summary: The summary must be a single, concise paragraph (4-6 sentences) capturing the main argument and topics of the lecture.

Insights: The insights must be a list of 5-7 distinct, important facts, definitions, or concepts from the text. Each insight should be a single, clear sentence.

Quiz: The quiz must contain exactly 5 multiple-choice questions.

Quiz Structure: Each question must have:
  - A question text.
  - A list of 4 options.
  - The correct_answer (which must be one of the provided options).

Relevance: All summaries, insights, and questions must be 100% derived from the provided transcription. Do not introduce external information."""
    
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434", timeout: int = 600):
        """
        Initialize the OllamaContentAnalyzer.
        
        Args:
            model: Ollama model name (e.g., 'llama3.1', 'mistral', 'llama2')
            base_url: Ollama API base URL
            timeout: Request timeout in seconds (default: 600 = 10 minutes)
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.timeout = timeout
        logger.info(f"OllamaContentAnalyzer initialized with model: {model}, timeout: {timeout}s")
    
    def _create_user_prompt(self, transcription: str) -> str:
        """
        Create the user prompt for the LLM.
        
        Args:
            transcription: The video transcription text
        
        Returns:
            Formatted prompt string
        """
        return f"""Here is the transcription from an educational lecture. Please analyze it and provide the summary, key insights, and a 5-question multiple-choice quiz based on the rules.

Transcription:

{transcription}


Output Format:

Provide your response as a single, valid JSON object using this exact schema:

{{
  "summary": "A single-paragraph summary of the lecture content...",
  "insights": [
    "The first key insight or definition.",
    "The second key insight or fact.",
    "..."
  ],
  "quiz": [
    {{
      "question": "What is the first question?",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "Option B"
    }},
    {{
      "question": "What is the second question?",
      "options": [
        "Option 1",
        "Option 2",
        "Option 3",
        "Option 4"
      ],
      "correct_answer": "Option 3"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, nothing else."""
    
    def _call_ollama(self, prompt: str, retry_count: int = 0) -> str:
        """
        Call Ollama API to generate content with retry logic.
        
        Args:
            prompt: The complete prompt
            retry_count: Current retry attempt (for internal use)
        
        Returns:
            Generated text response
        """
        full_prompt = f"{self.SYSTEM_INSTRUCTION}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent output
                "top_p": 0.9,
                "num_predict": 4096,  # Allow longer responses
                "num_ctx": 8192  # Increased context window
            }
        }
        
        try:
            logger.info(f"Calling Ollama API with model: {self.model} (timeout: {self.timeout}s)")
            if retry_count > 0:
                logger.info(f"Retry attempt {retry_count}/3")
            
            response = requests.post(self.api_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to Ollama. Make sure Ollama is running.\n"
                "Start it with: ollama serve"
            )
        except requests.exceptions.Timeout:
            # Retry up to 3 times with increasing timeout
            if retry_count < 3:
                logger.warning(f"Request timed out after {self.timeout}s. Retrying with extended timeout...")
                self.timeout = int(self.timeout * 1.5)  # Increase timeout by 50%
                return self._call_ollama(prompt, retry_count + 1)
            else:
                raise Exception(
                    f"Ollama request timed out after {self.timeout}s. \n\n"
                    "Suggestions:\n"
                    "1. Try a smaller/faster model: ollama pull llama3.2 (or mistral, phi)\n"
                    "2. Process shorter videos (split long videos into segments)\n"
                    "3. Increase system resources (close other applications)\n"
                    "4. Check Ollama is responding: curl http://localhost:11434/api/tags\n"
                )
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def analyze(self, transcription: str, auto_chunk: bool = True) -> Dict:
        """
        Analyze a lecture transcription and generate learning aids.
        
        Args:
            transcription: The full text transcription of the lecture
            auto_chunk: If True, automatically chunk long transcriptions (default: True)
        
        Returns:
            Dictionary containing:
                - summary: Concise paragraph summary
                - insights: List of key takeaways (5-7 items)
                - quiz: List of 5 multiple-choice questions
        
        Raises:
            ValueError: If the transcription is empty or too short
            Exception: If the API call fails or returns invalid JSON
        """
        if not transcription or len(transcription.strip()) < 50:
            raise ValueError("Transcription is too short or empty for meaningful analysis")
        
        # Check if transcription is very long (>10,000 words ~40,000 chars)
        word_count = len(transcription.split())
        char_count = len(transcription)
        
        logger.info(f"Analyzing transcription ({char_count:,} characters, ~{word_count:,} words)...")
        
        # Warn if transcription is very long
        if word_count > 10000 and auto_chunk:
            logger.warning(f"Long transcription detected ({word_count:,} words)")
            logger.warning("This may take 10+ minutes. Consider:")
            logger.warning("  1. Processing shorter video segments")
            logger.warning("  2. Using a faster model (llama3.2, mistral)")
            logger.warning("  3. Waiting patiently - processing continues...")
        
        try:
            # Create the prompt
            prompt = self._create_user_prompt(transcription)
            
            # Generate content
            response_text = self._call_ollama(prompt)
            
            # Try to extract JSON from the response
            response_text = response_text.strip()
            
            # Sometimes the model might wrap JSON in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Find the first { and last } to extract JSON
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            
            if start_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate the structure
            self._validate_result(result)
            
            logger.info("Analysis completed successfully")
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}...")
            raise Exception(f"Invalid JSON response from Ollama: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            raise
    
    def _validate_result(self, result: Dict):
        """
        Validate that the result has the expected structure.
        
        Args:
            result: The parsed JSON result
        
        Raises:
            ValueError: If the result structure is invalid
        """
        required_keys = ["summary", "insights", "quiz"]
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key in response: {key}")
        
        if not isinstance(result["summary"], str):
            raise ValueError("Summary must be a string")
        
        if not isinstance(result["insights"], list) or len(result["insights"]) < 5:
            raise ValueError("Insights must be a list with at least 5 items")
        
        if not isinstance(result["quiz"], list) or len(result["quiz"]) != 5:
            raise ValueError("Quiz must contain exactly 5 questions")
        
        # Validate quiz structure
        for i, question in enumerate(result["quiz"]):
            if "question" not in question or "options" not in question or "correct_answer" not in question:
                raise ValueError(f"Quiz question {i+1} is missing required fields")
            
            # Convert options to dict format if it's a list
            options = question["options"]
            if isinstance(options, list):
                # Convert list to dict with A, B, C, D keys
                option_dict = {}
                for idx, opt in enumerate(options):
                    key = chr(65 + idx)  # 65 is 'A', 66 is 'B', etc.
                    option_dict[key] = opt
                question["options"] = option_dict
                options = option_dict
                logger.warning(f"Quiz question {i+1}: Converted list options to dict format")
            
            if len(options) != 4:
                raise ValueError(f"Quiz question {i+1} must have exactly 4 options")
            
            # Check if correct_answer is in options
            correct_answer = question["correct_answer"]
            
            # If correct_answer is a letter (A/B/C/D), check if it's a valid key
            if len(correct_answer) == 1 and correct_answer.upper() in options:
                question["correct_answer"] = correct_answer.upper()
                continue
            
            # If correct_answer is the full text, try to match it
            if correct_answer not in options.values():
                # Try to find a close match (case-insensitive, strip whitespace)
                normalized_correct = correct_answer.strip().lower()
                
                for key, value in options.items():
                    if value.strip().lower() == normalized_correct:
                        question["correct_answer"] = key
                        logger.warning(f"Quiz question {i+1}: Matched answer to option {key}")
                        break
                else:
                    # Still no match found
                    logger.error(f"Quiz question {i+1} validation failed:")
                    logger.error(f"  Correct answer: '{correct_answer}'")
                    logger.error(f"  Options: {options}")
                    raise ValueError(f"Quiz question {i+1}: correct_answer must be one of the options")
    
    def analyze_and_save(self, transcription: str, output_path: str = "output.json") -> str:
        """
        Analyze transcription and save results to a JSON file.
        
        Args:
            transcription: The full text transcription
            output_path: Path to save the results
        
        Returns:
            Path to the output file
        """
        result = self.analyze(transcription)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis results saved to: {output_path}")
        return output_path


if __name__ == "__main__":
    # Example usage
    analyzer = OllamaContentAnalyzer(model="llama3.1")
    
    # Test with sample transcription
    sample_text = """
    Today we're going to discuss machine learning fundamentals.
    Machine learning is a subset of AI that allows computers to learn from data.
    """
    
    try:
        result = analyzer.analyze(sample_text)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
