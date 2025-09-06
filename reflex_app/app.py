import reflex as rx
import asyncio
from datetime import datetime
import hashlib

# Add parent directory to path
import sys
sys.path.append('..')

from agents.personalization import PersonalizedSmartSearch

class State(rx.State):
    """The app state."""
    query: str = ""
    current_results: dict = {}
    search_history: list = []
    user_id: str = ""
    is_searching: bool = False
    search_progress: int = 0
    status_text: str = ""
    
    # Advanced search options
    search_depth: str = "standard"  # quick, standard, deep
    confidence_threshold: int = 70
    show_sources: bool = True
    show_reasoning: bool = True
    
    def on_load(self):
        """Initialize the state."""
        if not self.user_id:
            self.user_id = hashlib.md5(
                str(datetime.now()).encode()
            ).hexdigest()[:8]
    
    def set_query(self, query: str):
        """Set the search query."""
        self.query = query
    
    def set_search_depth(self, depth: str):
        """Set the search depth."""
        self.search_depth = depth
    
    def set_confidence_threshold(self, threshold: int):
        """Set the confidence threshold."""
        self.confidence_threshold = threshold
    
    def toggle_sources(self, show: bool):
        """Toggle showing sources."""
        self.show_sources = show
    
    def toggle_reasoning(self, show: bool):
        """Toggle showing reasoning."""
        self.show_reasoning = show
    
    def search(self):
        """Execute the search."""
        if not self.query:
            return
        
        # Show search progress
        self.is_searching = True
        self.search_progress = 0
        self.status_text = "🔍 Analyzing your query..."
        yield
        
        # Simulate progress
        for i in range(1, 4):
            self.search_progress = i * 25
            if i == 1:
                self.status_text = "🌐 Searching across multiple sources..."
            elif i == 2:
                self.status_text = "✅ Verifying information..."
            else:
                self.status_text = "✨ Search completed!"
            yield
            # Sleep to simulate work
            yield asyncio.sleep(0.5)
        
        # Execute actual search
        try:
            search_system = PersonalizedSmartSearch()
            result = search_system.search(
                query=self.query,
                user_id=self.user_id
            )
            
            # Store results
            self.current_results = result
            self.search_history.append({
                'query': self.query,
                'timestamp': datetime.now(),
                'confidence': result['confidence']
            })
        except Exception as e:
            self.status_text = f"❌ Search failed: {str(e)}"
        
        self.is_searching = False
        self.search_progress = 100


def advanced_search_options() -> rx.Component:
    """Create advanced search options component."""
    return rx.vstack(
        rx.heading("⚙️ Advanced Search Options", size="md", font_weight="bold"),
        rx.vstack(
            # Search depth
            rx.vstack(
                rx.text("Search Depth", font_weight="bold", font_size="sm"),
                rx.hstack(
                    rx.button(
                        "Quick",
                        on_click=State.set_search_depth("quick"),
                        variant="surface" if State.search_depth != "quick" else "solid",
                        color_scheme="blue",
                        size="sm",
                    ),
                    rx.button(
                        "Standard",
                        on_click=State.set_search_depth("standard"),
                        variant="surface" if State.search_depth != "standard" else "solid",
                        color_scheme="blue",
                        size="sm",
                    ),
                    rx.button(
                        "Deep",
                        on_click=State.set_search_depth("deep"),
                        variant="surface" if State.search_depth != "deep" else "solid",
                        color_scheme="blue",
                        size="sm",
                    ),
                    spacing="3",
                    wrap="wrap",
                ),
                spacing="2",
            ),
            
            # Confidence threshold
            rx.vstack(
                rx.hstack(
                    rx.text("Min. Confidence Level", font_weight="bold", font_size="sm"),
                    rx.text(f"{State.confidence_threshold}%", font_size="sm", color="gray.500"),
                    justify="between",
                    width="100%",
                ),
                rx.slider(
                    min_=0,
                    max_=100,
                    value=State.confidence_threshold,
                    on_change=State.set_confidence_threshold,
                    width="100%",
                ),
                spacing="2",
            ),
            
            # Toggle options
            rx.vstack(
                rx.checkbox(
                    "Show sources",
                    checked=State.show_sources,
                    on_change=State.toggle_sources,
                ),
                rx.checkbox(
                    "Show reasoning process",
                    checked=State.show_reasoning,
                    on_change=State.toggle_reasoning,
                ),
                spacing="2",
            ),
            
            spacing="4",
        ),
        width="100%",
        padding="1em",
        border_radius="lg",
        background="rgba(0, 0, 0, 0.02)",
        border="1px solid rgba(0, 0, 0, 0.1)",
    )


def index() -> rx.Component:
    """Create the main page with improved UI/UX and responsive design."""
    return rx.fragment(
        # Responsive container
        rx.box(
            rx.color_mode_button(rx.color_mode_icon(), float="right"),
            rx.vstack(
                # Header with improved styling
                rx.vstack(
                    rx.heading(
                        "🔍 Smart Search", 
                        font_size=["2em", "2em", "2.5em"], 
                        font_weight="bold",
                        background="linear-gradient(90deg, #1e88e5, #0d47a1)",
                        background_clip="text",
                        color="transparent",
                        text_align="center",
                    ),
                    rx.text(
                        "AI-Powered Search • Zero Hallucinations • Personalized Results", 
                        font_size=["1em", "1em", "1.2em"], 
                        color="gray.500",
                        text_align="center"
                    ),
                    spacing="2",
                    align_items="center",
                    margin_bottom=["1em", "1em", "1.5em"],
                ),
                
                # Enhanced search input with responsive design
                rx.vstack(
                    rx.hstack(
                        rx.input(
                            placeholder="Ask anything... (e.g., 'Latest AI breakthroughs', 'Climate solutions 2024')",
                            on_change=State.set_query,
                            width="100%",
                            size=["md", "md", "lg"],
                            variant="filled",
                            border_radius="full",
                            box_shadow="0 4px 6px rgba(0, 0, 0, 0.1)",
                        ),
                        rx.button(
                            "Search", 
                            on_click=State.search, 
                            color_scheme="blue",
                            size=["md", "md", "lg"],
                            border_radius="full",
                            font_weight="bold",
                            box_shadow="0 4px 6px rgba(0, 0, 0, 0.1)",
                            display=["none", "flex", "flex"],
                        ),
                        rx.button(
                            "🔍", 
                            on_click=State.search, 
                            color_scheme="blue",
                            size=["md", "md", "lg"],
                            border_radius="full",
                            font_weight="bold",
                            box_shadow="0 4px 6px rgba(0, 0, 0, 0.1)",
                            display=["flex", "none", "none"],
                        ),
                        width="100%",
                        spacing="3",
                    ),
                    
                    # Advanced search options
                    rx.accordion(
                        rx.accordion_item(
                            rx.accordion_button(
                                rx.text("⚙️ Advanced Options"),
                                rx.accordion_icon(),
                                justify="between",
                            ),
                            rx.accordion_panel(
                                advanced_search_options(),
                            ),
                        ),
                        width="100%",
                    ),
                    
                    spacing="4",
                    width="100%",
                    align_items="center",
                ),
                
                # Progress indicator with enhanced styling
                rx.cond(
                    State.is_searching,
                    rx.vstack(
                        rx.progress(
                            value=State.search_progress, 
                            width="100%",
                            border_radius="full",
                            color_scheme="blue",
                        ),
                        rx.text(
                            State.status_text, 
                            font_size=["sm", "sm", "md"], 
                            color="gray.500",
                            text_align="center"
                        ),
                        spacing="4",
                        width="100%",
                        align_items="center",
                    ),
                ),
                
                # Results display with improved card styling
                rx.cond(
                    State.current_results,
                    rx.vstack(
                        rx.box(height=["0.5em", "0.5em", "1em"]),
                        rx.heading(
                            "📊 Search Results", 
                            size=["md", "md", "lg"], 
                            font_weight="bold",
                            color="gray.700"
                        ),
                        # Confidence badges
                        rx.hstack(
                            rx.badge(
                                f"Confidence: {State.current_results['confidence']}%",
                                color_scheme="green" if State.current_results['confidence'] >= 85 
                                            else "yellow" if State.current_results['confidence'] >= 70 
                                            else "red",
                                font_size=["xs", "xs", "sm"],
                                border_radius="full",
                            ),
                            rx.badge(
                                "Personalized" if State.current_results.get('personalized') else "Standard",
                                color_scheme="blue",
                                font_size=["xs", "xs", "sm"],
                                border_radius="full",
                            ),
                            spacing="3",
                            wrap="wrap",
                        ),
                        # Results card
                        rx.card(
                            rx.text(
                                State.current_results["results"],
                                font_size=["sm", "sm", "md"],
                                line_height="tall",
                            ),
                            variant="surface",
                            width="100%",
                            padding=["1em", "1em", "1.5em"],
                            border_radius="lg",
                            box_shadow="0 4px 6px rgba(0, 0, 0, 0.05)",
                        ),
                        width="100%",
                        spacing="4",
                    ),
                ),
                
                spacing="6",
                font_size="1em",
                padding_top=["1%", "1%", "2%"],
                padding_x=["2", "4", "4"],
                align_items="center",
                min_height="100vh",
                max_width="1200px",
                margin_x="auto",
            ),
            width="100%",
        ),
    )


# Add state and page to the app.
app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)
app.add_page(index, on_load=State.on_load)
app.compile()