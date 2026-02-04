"""
Test MongoDB connection and save negotiation
"""

from utils.mongodb_client import get_mongodb_client

def test_mongodb():
    """Test MongoDB connection"""
    print("=" * 70)
    print("Testing MongoDB Connection")
    print("=" * 70)
    print()
    
    try:
        # Get MongoDB client
        print("Connecting to MongoDB...")
        mongodb = get_mongodb_client()
        print("✅ Connected successfully!")
        print()
        
        # Get statistics
        print("Getting statistics...")
        stats = mongodb.get_statistics()
        print(f"Total negotiations: {stats.get('total_negotiations', 0)}")
        print(f"Successful: {stats.get('successful_negotiations', 0)}")
        print(f"Failed: {stats.get('failed_negotiations', 0)}")
        print(f"Success rate: {stats.get('success_rate', 0):.2f}%")
        print(f"Average rounds: {stats.get('average_rounds', 0):.2f}")
        print()
        
        # Test save (dummy data)
        print("Testing save operation...")
        test_results = {
            "agreement_reached": True,
            "rounds": 5,
            "max_rounds": 10,
            "messages": [
                {"round": 1, "agent": "Agent A", "persona": "Aggressive", "message": "Test message 1"},
                {"round": 1, "agent": "Agent B", "persona": "Fair", "message": "Test message 2"}
            ],
            "agreement_terms": {"price": 650},
            "utility_a": 0.8,
            "utility_b": 0.9,
            "scenario_type": "price_negotiation"
        }
        
        doc_id = mongodb.save_negotiation(
            scenario_name="Test Scenario",
            agent_a_persona="Aggressive",
            agent_b_persona="Fair",
            results=test_results
        )
        print(f"✅ Saved test negotiation with ID: {doc_id}")
        print()
        
        # Retrieve it
        print("Retrieving saved negotiation...")
        retrieved = mongodb.get_negotiation(doc_id)
        if retrieved:
            print(f"✅ Retrieved negotiation:")
            print(f"  Scenario: {retrieved.get('scenario_name')}")
            print(f"  Agreement: {retrieved.get('agreement_reached')}")
            print(f"  Rounds: {retrieved.get('rounds')}")
        print()
        
        print("=" * 70)
        print("✅ MongoDB is working correctly!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure:")
        print("  1. Your .env file has DB_NAME, DB_USER, DB_PASS")
        print("  2. MongoDB credentials are correct")
        print("  3. You have installed pymongo: pip install pymongo dnspython")

if __name__ == "__main__":
    test_mongodb()
