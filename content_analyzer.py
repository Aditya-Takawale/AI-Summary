"""
Content analysis module for the AI-Powered Video Lecture Assistant.
Uses Google Gemini API to analyze transcriptions and generate learning aids.
"""

import json
import logging
from typing import Dict, List
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentAnalyzer:
    """Analyzes lecture transcriptions using Google Gemini API."""
    
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
    
    def __init__(self, api_key: str):
        """
        Initialize the ContentAnalyzer.
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Initialize the model with system instruction
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=self.SYSTEM_INSTRUCTION
        )
        logger.info("ContentAnalyzer initialized with Gemini API")
    
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
}}"""
    
    def analyze(self, transcription: str) -> Dict:
        """
        Analyze a lecture transcription and generate learning aids.
        
        Args:
            transcription: The full text transcription of the lecture
        
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
        
        logger.info(f"Analyzing transcription ({len(transcription)} characters)...")
        
        try:
            # Create the prompt
            prompt = self._create_user_prompt(transcription)
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            # Extract the text response
            response_text = response.text.strip()
            
            # Try to parse JSON from the response
            # Sometimes the model might wrap JSON in markdown code blocks
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate the structure
            self._validate_result(result)
            
            logger.info("Analysis completed successfully")
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}...")
            raise Exception(f"Invalid JSON response from AI model: {str(e)}")
        
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
            
            if len(question["options"]) != 4:
                raise ValueError(f"Quiz question {i+1} must have exactly 4 options")
            
            if question["correct_answer"] not in question["options"]:
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
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        analyzer = ContentAnalyzer(api_key)
        # result = analyzer.analyze("Your transcription text here...")
        # print(json.dumps(result, indent=2))
