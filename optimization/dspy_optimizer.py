import dspy
from dspy.teleprompt import MIPROv2, BootstrapFewShot
from config import OPENAI_API_KEY

class SearchOptimizer:
    def __init__(self):
        # Configure DSPy
        self.lm = dspy.OpenAI(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            max_tokens=1000
        )
        dspy.settings.configure(lm=self.lm)
    
    def create_optimized_search(self):
        """Create optimized search module"""
        
        class SearchSignature(dspy.Signature):
            """Search for accurate, relevant information"""
            query = dspy.InputField(desc="user search query")
            context = dspy.InputField(desc="user preferences (optional)")
            answer = dspy.OutputField(desc="comprehensive, accurate search results with sources")
        
        class OptimizedSearch(dspy.Module):
            def __init__(self):
                super().__init__()
                self.prog = dspy.ChainOfThought(SearchSignature)
            
            def forward(self, query, context=""):
                return self.prog(query=query, context=context)
        
        return OptimizedSearch()
    
    def optimize_with_examples(self, examples):
        """Optimize using examples"""
        
        def accuracy_metric(gold, pred, trace=None):
            # Check if prediction contains accurate info
            accuracy = 1.0 if gold.answer in pred.answer else 0.0
            
            # Check for sources
            has_sources = 1.0 if "source" in pred.answer.lower() else 0.0
            
            # Check length (penalize too short)
            length_score = min(len(pred.answer) / 200, 1.0)
            
            return (accuracy * 0.5 + has_sources * 0.3 + length_score * 0.2)
        
        # Create optimizer
        optimizer = BootstrapFewShot(metric=accuracy_metric, max_rounds=3)
        
        # Compile
        optimized = optimizer.compile(
            self.create_optimized_search(),
            trainset=examples
        )
        
        return optimized

# Create training examples
def create_training_examples():
    examples = []
    
    # Example 1
    examples.append(dspy.Example(
        query="What are the latest AI breakthroughs in 2024?",
        context="interested in technical details",
        answer="Recent AI breakthroughs include GPT-4's multimodal capabilities, Claude 3's improved reasoning, and advances in robotics. Sources: OpenAI blog, Anthropic research papers."
    ))
    
    # Add more examples...
    
    return examples

# Quick optimization test
if __name__ == "__main__":
    optimizer = SearchOptimizer()
    examples = create_training_examples()
    optimized_search = optimizer.optimize_with_examples(examples)
    
    # Test
    result = optimized_search("Tell me about quantum computing")
    print(result.answer)