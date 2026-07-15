import re
import logging
from spellchecker import SpellChecker
import language_tool_python
from src.config import LANGUAGE, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

class WordChecker:
    def __init__(self, language='en'):
        """Initialize the word checker with specified language."""
        self.language = language
        self.spell = None
        self.grammar = None
        self._initialize_checkers()
    
    def _initialize_checkers(self):
        """Initialize spell and grammar checkers."""
        try:
            # Initialize spell checker
            if self.language in SUPPORTED_LANGUAGES:
                self.spell = SpellChecker(language=self.language)
            else:
                logger.warning(f"Language {self.language} not supported. Falling back to English.")
                self.spell = SpellChecker(language='en')
            
            # Initialize grammar checker
            try:
                self.grammar = language_tool_python.LanguageTool(self.language)
            except Exception as e:
                logger.warning(f"Grammar checker for {self.language} failed: {e}. Using English.")
                self.grammar = language_tool_python.LanguageTool('en')
                
        except Exception as e:
            logger.error(f"Failed to initialize checkers: {e}")
            raise
    
    def check_spelling(self, text):
        """Check spelling and return corrections."""
        if not text or not self.spell:
            return {}
        
        # Split text into words, removing punctuation
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', text)
        misspelled = self.spell.unknown(words)
        
        corrections = {}
        suggestions = {}
        
        for word in misspelled:
            correction = self.spell.correction(word)
            if correction and correction != word:
                corrections[word] = correction
                suggestions[word] = self.spell.candidates(word)
        
        return {
            'corrections': corrections,
            'suggestions': suggestions,
            'misspelled_count': len(corrections)
        }
    
    def check_grammar(self, text):
        """Check grammar and return issues."""
        if not text or not self.grammar:
            return []
        
        try:
            matches = self.grammar.check(text)
            return [{
                'message': match.message,
                'replacements': match.replacements[:5] if match.replacements else [],
                'offset': match.offset,
                'length': match.errorLength,
                'rule_id': match.ruleId,
                'category': match.category if hasattr(match, 'category') else 'Grammar'
            } for match in matches]
        except Exception as e:
            logger.error(f"Grammar check failed: {e}")
            return []
    
    def full_check(self, text):
        """Perform both spelling and grammar checks."""
        if not text:
            return {'spelling': {}, 'grammar': [], 'summary': 'No text provided'}
        
        spelling_results = self.check_spelling(text)
        grammar_results = self.check_grammar(text)
        
        total_issues = spelling_results['misspelled_count'] + len(grammar_results)
        
        return {
            'spelling': spelling_results,
            'grammar': grammar_results,
            'total_issues': total_issues,
            'has_issues': total_issues > 0,
            'summary': f"Found {total_issues} issue(s): {spelling_results['misspelled_count']} spelling, {len(grammar_results)} grammar"
        }
    
    def get_supported_languages(self):
        """Return list of supported languages."""
        return SUPPORTED_LANGUAGES
    
    def change_language(self, new_language):
        """Change the language for checking."""
        if new_language in SUPPORTED_LANGUAGES:
            self.language = new_language
            self._initialize_checkers()
            return True
        return False

# Create a singleton instance
checker = WordChecker(LANGUAGE)
