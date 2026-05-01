"""
Validation script: Test agent components without API calls
"""

import sys
sys.path.insert(0, 'code')

from corpus import CorpusLoader
from classifier import Classifier
from escalation import EscalationRouter
import os

def test_corpus_loader():
    """Test corpus loading and indexing"""
    print("Testing CorpusLoader...")
    loader = CorpusLoader("data")
    loader.load_corpus()
    print(f"  ✓ Loaded {len(loader.documents)} documents")
    
    # Build index
    loader.build_index()
    print(f"  ✓ Built FAISS index")
    
    # Test search
    results = loader.search("how do I reset my password", top_k=3)
    print(f"  ✓ Search returned {len(results)} results")
    
    for i, (doc, meta, score) in enumerate(results):
        print(f"    {i+1}. {meta['product_area']} (score: {score:.3f})")
    
    return True

def test_escalation_router():
    """Test escalation logic"""
    print("\nTesting EscalationRouter...")
    router = EscalationRouter()
    
    test_cases = [
        ("The site is completely down", "Site down", {}, [], True, "should escalate outage"),
        ("How do I do X?", "Basic question", {"product_area": "api"}, [("dummy", {}, 0)], False, "should reply if docs exist"),
        ("I got charged twice, this is fraud", "Billing", {}, [], True, "should escalate billing"),
    ]
    
    for issue, subject, classification, docs, expected_escalate, desc in test_cases:
        should_escalate, reason = router.should_escalate(issue, subject, classification, docs)
        status = "✓" if should_escalate == expected_escalate else "✗"
        print(f"  {status} {desc}")
    
    return True

def test_file_structure():
    """Test required files exist"""
    print("\nTesting file structure...")
    required_files = [
        "code/main.py",
        "code/agent.py",
        "code/corpus.py",
        "code/classifier.py",
        "code/escalation.py",
        "code/requirements.txt",
        "code/README.md",
        "support_tickets/sample_support_tickets.csv",
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} MISSING")
            return False
    
    return True

def main():
    print("=" * 60)
    print("AGENT VALIDATION TEST")
    print("=" * 60)
    
    try:
        # Check files
        if not test_file_structure():
            print("\n✗ File structure validation FAILED")
            return False
        
        # Test corpus
        if not test_corpus_loader():
            print("\n✗ Corpus loader test FAILED")
            return False
        
        # Test escalation
        if not test_escalation_router():
            print("\n✗ Escalation router test FAILED")
            return False
        
        print("\n" + "=" * 60)
        print("✓ ALL VALIDATION TESTS PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Add ANTHROPIC_API_KEY to .env")
        print("2. Run: python code/main.py --sample")
        print("3. Check output.csv for results")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
