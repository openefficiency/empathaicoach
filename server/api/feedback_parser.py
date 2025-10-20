"""Feedback data parsing utilities.

This module provides functions to parse 360° feedback data from various formats
(text, CSV, JSON) and extract themes and categories.
"""

import csv
import json
import re
from collections import Counter
from io import StringIO
from typing import Any, Dict, List, Tuple

from loguru import logger


def parse_feedback_text(text: str) -> Dict[str, Any]:
    """
    Parse raw feedback text and extract themes.
    
    Uses simple heuristics to identify feedback themes and sentiments.
    In production, this could be enhanced with NLP/ML models.
    
    Args:
        text: Raw feedback text
        
    Returns:
        Dictionary with parsed themes and comments
    """
    # Split into individual comments (by newlines or common separators)
    comments = [c.strip() for c in re.split(r'\n+|;|\.(?=\s+[A-Z])', text) if c.strip()]
    
    # Extract themes using keyword matching
    themes_counter = Counter()
    parsed_comments = []
    
    # Define theme keywords (simplified for MVP)
    theme_keywords = {
        'communication': ['communication', 'communicate', 'clarity', 'clear', 'explain', 'articulate'],
        'leadership': ['leadership', 'lead', 'direction', 'vision', 'inspire', 'motivate'],
        'technical': ['technical', 'technology', 'code', 'engineering', 'expertise', 'skill'],
        'collaboration': ['collaboration', 'teamwork', 'team', 'cooperate', 'work together'],
        'delegation': ['delegation', 'delegate', 'empower', 'trust', 'distribute'],
        'feedback': ['feedback', 'input', 'suggestions', 'advice'],
        'time_management': ['time', 'deadline', 'schedule', 'prioritize', 'organize'],
        'problem_solving': ['problem', 'solution', 'solve', 'resolve', 'fix'],
    }
    
    # Sentiment keywords
    positive_keywords = ['great', 'excellent', 'strong', 'good', 'impressive', 'outstanding', 'helpful']
    negative_keywords = ['could improve', 'needs work', 'lacking', 'weak', 'should', 'needs to']
    
    for comment in comments:
        comment_lower = comment.lower()
        
        # Detect themes
        detected_themes = []
        for theme, keywords in theme_keywords.items():
            if any(keyword in comment_lower for keyword in keywords):
                detected_themes.append(theme)
                themes_counter[theme] += 1
        
        # Detect sentiment
        sentiment = 'neutral'
        if any(keyword in comment_lower for keyword in positive_keywords):
            sentiment = 'positive'
        elif any(keyword in comment_lower for keyword in negative_keywords):
            sentiment = 'negative'
        
        # Determine category (strength vs improvement)
        category = 'improvement' if sentiment == 'negative' else 'strength' if sentiment == 'positive' else 'neutral'
        
        parsed_comments.append({
            'source': 'unknown',  # Can't determine from raw text
            'category': detected_themes[0] if detected_themes else 'general',
            'comment': comment,
            'sentiment': sentiment,
            'themes': detected_themes
        })
    
    # Build theme summaries
    themes = []
    for theme, count in themes_counter.most_common():
        # Get examples for this theme
        examples = [
            c['comment'] for c in parsed_comments 
            if theme in c.get('themes', [])
        ][:3]  # Limit to 3 examples
        
        # Determine if it's a strength or improvement area
        theme_comments = [c for c in parsed_comments if theme in c.get('themes', [])]
        positive_count = sum(1 for c in theme_comments if c['sentiment'] == 'positive')
        negative_count = sum(1 for c in theme_comments if c['sentiment'] == 'negative')
        
        category = 'strength' if positive_count > negative_count else 'improvement' if negative_count > positive_count else 'neutral'
        
        themes.append({
            'category': category,
            'theme': theme.replace('_', ' ').title(),
            'frequency': count,
            'examples': examples
        })
    
    return {
        'themes': themes,
        'raw_comments': parsed_comments,
        'total_comments': len(comments)
    }


def parse_feedback_csv(csv_content: str) -> Dict[str, Any]:
    """
    Parse feedback from CSV format.
    
    Expected CSV columns: source, category, comment, sentiment (optional)
    
    Args:
        csv_content: CSV file content as string
        
    Returns:
        Dictionary with parsed themes and comments
    """
    try:
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        comments = []
        themes_counter = Counter()
        
        for row in reader:
            # Extract fields with fallbacks
            source = row.get('source', row.get('Source', 'unknown'))
            category = row.get('category', row.get('Category', 'general'))
            comment = row.get('comment', row.get('Comment', ''))
            sentiment = row.get('sentiment', row.get('Sentiment', 'neutral'))
            
            if not comment:
                continue
            
            comments.append({
                'source': source,
                'category': category,
                'comment': comment,
                'sentiment': sentiment
            })
            
            themes_counter[category] += 1
        
        # Build theme summaries
        themes = []
        for theme, count in themes_counter.most_common():
            # Get examples for this theme
            examples = [
                c['comment'] for c in comments 
                if c['category'] == theme
            ][:3]
            
            # Determine category (strength vs improvement)
            theme_comments = [c for c in comments if c['category'] == theme]
            positive_count = sum(1 for c in theme_comments if c['sentiment'] == 'positive')
            negative_count = sum(1 for c in theme_comments if c['sentiment'] == 'negative')
            
            category = 'strength' if positive_count > negative_count else 'improvement' if negative_count > positive_count else 'neutral'
            
            themes.append({
                'category': category,
                'theme': theme.title(),
                'frequency': count,
                'examples': examples
            })
        
        return {
            'themes': themes,
            'raw_comments': comments,
            'total_comments': len(comments)
        }
        
    except Exception as e:
        logger.error(f"Failed to parse CSV feedback: {e}")
        raise ValueError(f"Invalid CSV format: {str(e)}")


def parse_feedback_json(json_content: str) -> Dict[str, Any]:
    """
    Parse feedback from JSON format.
    
    Expected JSON structure:
    {
        "themes": [...],
        "comments": [...]
    }
    or
    {
        "feedback": [...]
    }
    or 360° feedback format:
    {
        "employee": {...},
        "strengths": [...],
        "areas_for_improvement": [...]
    }
    
    Args:
        json_content: JSON file content as string
        
    Returns:
        Dictionary with parsed themes and comments
    """
    try:
        data = json.loads(json_content)
        
        # If already in the expected format, return it
        if 'themes' in data and 'raw_comments' in data:
            return data
        
        # Check if it's 360° feedback format (with strengths and areas_for_improvement)
        if 'strengths' in data or 'areas_for_improvement' in data:
            return parse_360_feedback_format(data)
        
        # If it has a comments or feedback array, process it
        comments = data.get('comments', data.get('feedback', data.get('raw_comments', [])))
        
        if not comments:
            raise ValueError("No comments found in JSON data")
        
        # Count themes
        themes_counter = Counter()
        parsed_comments = []
        
        for comment in comments:
            if isinstance(comment, str):
                # Simple string comment, parse as text
                parsed = parse_feedback_text(comment)
                parsed_comments.extend(parsed['raw_comments'])
                for theme in parsed['themes']:
                    themes_counter[theme['theme']] += theme['frequency']
            elif isinstance(comment, dict):
                # Structured comment
                category = comment.get('category', 'general')
                themes_counter[category] += 1
                parsed_comments.append({
                    'source': comment.get('source', 'unknown'),
                    'category': category,
                    'comment': comment.get('comment', comment.get('text', '')),
                    'sentiment': comment.get('sentiment', 'neutral')
                })
        
        # Build theme summaries
        themes = []
        for theme, count in themes_counter.most_common():
            # Get examples for this theme
            examples = [
                c['comment'] for c in parsed_comments 
                if c['category'] == theme
            ][:3]
            
            # Determine category (strength vs improvement)
            theme_comments = [c for c in parsed_comments if c['category'] == theme]
            positive_count = sum(1 for c in theme_comments if c.get('sentiment') == 'positive')
            negative_count = sum(1 for c in theme_comments if c.get('sentiment') == 'negative')
            
            category = 'strength' if positive_count > negative_count else 'improvement' if negative_count > positive_count else 'neutral'
            
            themes.append({
                'category': category,
                'theme': theme if isinstance(theme, str) else str(theme),
                'frequency': count,
                'examples': examples
            })
        
        return {
            'themes': themes,
            'raw_comments': parsed_comments,
            'total_comments': len(parsed_comments)
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON feedback: {e}")
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to process JSON feedback: {e}")
        raise ValueError(f"Error processing JSON: {str(e)}")


def parse_360_feedback_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse 360° feedback format with strengths and areas_for_improvement.
    
    Args:
        data: Parsed JSON data in 360° format
        
    Returns:
        Dictionary with parsed themes and comments
    """
    themes = []
    parsed_comments = []
    total_comments = 0
    
    # Process strengths
    for strength in data.get('strengths', []):
        theme_name = strength.get('theme', 'Unknown Strength')
        frequency = strength.get('frequency', 0)
        comments = strength.get('comments', [])
        
        themes.append({
            'category': 'strength',
            'theme': theme_name,
            'frequency': frequency,
            'examples': comments[:3]  # Limit to 3 examples
        })
        
        # Add to parsed comments
        for comment in comments:
            parsed_comments.append({
                'source': 'unknown',
                'category': theme_name,
                'comment': comment,
                'sentiment': 'positive'
            })
            total_comments += 1
    
    # Process areas for improvement
    for improvement in data.get('areas_for_improvement', []):
        theme_name = improvement.get('theme', 'Unknown Improvement Area')
        frequency = improvement.get('frequency', 0)
        comments = improvement.get('comments', [])
        
        themes.append({
            'category': 'improvement',
            'theme': theme_name,
            'frequency': frequency,
            'examples': comments[:3]  # Limit to 3 examples
        })
        
        # Add to parsed comments
        for comment in comments:
            parsed_comments.append({
                'source': 'unknown',
                'category': theme_name,
                'comment': comment,
                'sentiment': 'negative'
            })
            total_comments += 1
    
    return {
        'themes': themes,
        'raw_comments': parsed_comments,
        'total_comments': total_comments
    }


def parse_feedback(
    feedback_text: str = None,
    feedback_file: str = None,
    file_type: str = None
) -> Dict[str, Any]:
    """
    Parse feedback data from various formats.
    
    Args:
        feedback_text: Raw feedback text
        feedback_file: File content (for CSV or JSON)
        file_type: Type of file ('csv', 'json', or 'text')
        
    Returns:
        Dictionary with parsed themes and comments
    """
    if feedback_file and file_type:
        if file_type.lower() == 'csv':
            return parse_feedback_csv(feedback_file)
        elif file_type.lower() == 'json':
            return parse_feedback_json(feedback_file)
        elif file_type.lower() == 'text':
            return parse_feedback_text(feedback_file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    elif feedback_text:
        return parse_feedback_text(feedback_text)
    else:
        raise ValueError("Either feedback_text or feedback_file must be provided")
