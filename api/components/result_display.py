import streamlit as st
from typing import Dict, Any
import re
from datetime import datetime

class ResultsDisplay:
    """Component for displaying search results with rich formatting"""
    
    @staticmethod
    def display_results(results: Dict[str, Any]):
        """Display search results with proper formatting"""
        
        # Parse results for better display
        content = results.get('results', '')
        sources = ResultsDisplay._extract_sources(content)
        main_content = ResultsDisplay._clean_content(content)
        
        # Display main content with formatting
        st.markdown(f"""
        <div class="search-results">
            {ResultsDisplay._format_content(main_content)}
        </div>
        """, unsafe_allow_html=True)
        
        # Display sources if any
        if sources:
            with st.expander(f"📚 Sources ({len(sources)})"):
                for idx, source in enumerate(sources, 1):
                    st.markdown(f"{idx}. {source}")
        
        # Display confidence indicator
        confidence = results.get('confidence', 0)
        ResultsDisplay._show_confidence_indicator(confidence)
    
    @staticmethod
    def _extract_sources(content: str) -> list:
        """Extract sources from content"""
        # Look for various source patterns
        patterns = [
            r'Source[s]?:\s*([^\n]+)',
            r'Reference[s]?:\s*([^\n]+)',
            r'\[(\d+)\]\s*([^\n]+)'
        ]
        
        sources = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            sources.extend(matches)
        
        return list(set(sources))  # Remove duplicates
    
    @staticmethod
    def _clean_content(content: str) -> str:
        """Clean content for display"""
        # Remove source references from main content
        cleaned = re.sub(r'Source[s]?:\s*[^\n]+\n?', '', content, flags=re.IGNORECASE)
        cleaned = re.sub(r'Reference[s]?:\s*[^\n]+\n?', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\[\d+\]', '', cleaned)
        
        return cleaned.strip()
    
    @staticmethod
    def _format_content(content: str) -> str:
        """Format content with HTML for better display"""
        # Convert markdown-like formatting
        formatted = content
        
        # Headers
        formatted = re.sub(r'^### (.+)$', r'<h4>\1</h4>', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'^## (.+)$', r'<h3>\1</h3>', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'^# (.+)$', r'<h2>\1</h2>', formatted, flags=re.MULTILINE)
        
        # Bold and italic
        formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', formatted)
        formatted = re.sub(r'\*(.+?)\*', r'<em>\1</em>', formatted)
        
        # Lists
        formatted = re.sub(r'^\* (.+)$', r'<li>\1</li>', formatted, flags=re.MULTILINE)
        formatted = re.sub(r'((?:<li>.*</li>\n?)+)', r'<ul>\1</ul>', formatted)
        
        # Paragraphs
        paragraphs = formatted.split('\n\n')
        formatted = '\n'.join(f'<p>{p}</p>' if not p.startswith('<') else p for p in paragraphs)
        
        return formatted
    
    @staticmethod
    def _show_confidence_indicator(confidence: float):
        """Show visual confidence indicator"""
        if confidence >= 85:
            color = "#4caf50"
            label = "High Confidence"
            icon = "✅"
        elif confidence >= 70:
            color = "#ff9800"
            label = "Medium Confidence"
            icon = "⚠️"
        else:
            color = "#f44336"
            label = "Low Confidence"
            icon = "❌"
        
        st.markdown(f"""
        <div style='background-color: {color}20; border-left: 4px solid {color}; 
                    padding: 0.5rem 1rem; margin: 1rem 0; border-radius: 5px;'>
            <strong>{icon} {label}</strong> - {confidence}% confidence
        </div>
        """, unsafe_allow_html=True)