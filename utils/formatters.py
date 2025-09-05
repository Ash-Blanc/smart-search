import re
from typing import List, Dict, Any
from datetime import datetime

def format_results(content: str) -> str:
    """Format search results for display"""
    
    # Add syntax highlighting for code blocks
    content = highlight_code_blocks(content)
    
    # Format links
    content = format_links(content)
    
    # Add emphasis to important terms
    content = emphasize_keywords(content)
    
    # Format lists properly
    content = format_lists(content)
    
    return content

def highlight_code_blocks(content: str) -> str:
    """Add syntax highlighting to code blocks"""
    # Pattern for code blocks
    pattern = r'```(\w+)?\n(.*?)```'
    
    def replace_code(match):
        language = match.group(1) or 'python'
        code = match.group(2)
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    
    return re.sub(pattern, replace_code, content, flags=re.DOTALL)

def format_links(content: str) -> str:
    """Convert URLs to clickable links"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    
    def replace_url(match):
        url = match.group(0)
        return f'<a href="{url}" target="_blank" style="color: #1e88e5;">{url}</a>'
    
    return re.sub(url_pattern, replace_url, content)

def emphasize_keywords(content: str, keywords: List[str] = None) -> str:
    """Emphasize important keywords"""
    if keywords is None:
        # Default important terms
        keywords = ['important', 'note', 'warning', 'tip', 'key', 'critical']
    
    for keyword in keywords:
        pattern = rf'\b({keyword})\b'
        replacement = r'<span style="background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;">\1</span>'
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    return content

def format_lists(content: str) -> str:
    """Format bullet points and numbered lists"""
    # Convert markdown lists to HTML
    lines = content.split('\n')
    formatted_lines = []
    in_list = False
    list_type = None
    
    for line in lines:
        # Check for bullet points
        if re.match(r'^\s*[-*]\s+', line):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            item = re.sub(r'^\s*[-*]\s+', '', line)
            formatted_lines.append(f'<li>{item}</li>')
        # Check for numbered lists
        elif re.match(r'^\s*\d+\.\s+', line):
            if not in_list:
                formatted_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            item = re.sub(r'^\s*\d+\.\s+', '', line)
            formatted_lines.append(f'<li>{item}</li>')
        else:
            if in_list:
                formatted_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            formatted_lines.append(line)
    
    # Close any open lists
    if in_list:
        formatted_lines.append(f'</{list_type}>')
    
    return '\n'.join(formatted_lines)

def create_summary_card(title: str, content: str, metadata: Dict[str, Any] = None) -> str:
    """Create a formatted summary card"""
    metadata_html = ""
    if metadata:
        metadata_items = [f'<span class="metadata-item">{k}: {v}</span>' for k, v in metadata.items()]
        metadata_html = f'<div class="metadata">{" | ".join(metadata_items)}</div>'
    
    return f"""
    <div class="summary-card">
        <h4>{title}</h4>
        <div class="content">{content}</div>
        {metadata_html}
    </div>
    """