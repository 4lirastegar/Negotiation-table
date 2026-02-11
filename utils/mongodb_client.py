"""
MongoDB Client
Handles connection and operations for storing negotiation histories
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Dict, List, Any, Optional
from datetime import datetime
from config.config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_CONNECTION_STRING


class MongoDBClient:
    """MongoDB client for storing negotiation data"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = None
        self.db = None
        self.negotiations_collection = None
        self.tests_collection = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            # Use full connection string if provided, otherwise build it
            if DB_CONNECTION_STRING:
                connection_string = DB_CONNECTION_STRING
            else:
                # Build connection string from components
                if not all([DB_NAME, DB_USER, DB_PASS]):
                    raise ValueError("MongoDB credentials not found in environment. Check DB_NAME, DB_USER, DB_PASS in .env")
                
                # MongoDB Atlas connection string format
                # Note: tlsAllowInvalidCertificates=true is added to handle SSL cert issues on some systems
                connection_string = f"mongodb+srv://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true"
            
            # Connect to MongoDB
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collections
            self.db = self.client[DB_NAME]
            self.negotiations_collection = self.db['negotiations']
            self.tests_collection = self.db['tests']
            
            print(f"✅ Connected to MongoDB: {DB_NAME}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            raise
    
    def save_negotiation(
        self,
        scenario_name: str,
        agent_a_persona: str,
        agent_b_persona: str,
        results: Dict[str, Any]
    ) -> str:
        """
        Save a negotiation to MongoDB
        
        Args:
            scenario_name: Name of the scenario
            agent_a_persona: Persona of Agent A
            agent_b_persona: Persona of Agent B
            results: Full results dictionary from negotiation
            
        Returns:
            Document ID of the saved negotiation
        """
        try:
            # Prepare document
            document = {
                "scenario_name": scenario_name,
                "agent_a_persona": agent_a_persona,
                "agent_b_persona": agent_b_persona,
                "timestamp": datetime.utcnow(),
                "agreement_reached": results.get("agreement_reached", False),
                "rounds": results.get("rounds", 0),
                "max_rounds": results.get("max_rounds", 10),
                "messages": results.get("messages", []),
                "agreement_terms": results.get("agreement_terms"),
                "utility_a": results.get("utility_a"),
                "utility_b": results.get("utility_b"),
                "agent_a_info": results.get("agent_a_info"),
                "agent_b_info": results.get("agent_b_info"),
                "judge_analysis": results.get("judge_analysis"),
                "scenario_type": results.get("scenario_type"),
                "qualitative_metrics": results.get("qualitative_metrics")  # ← Academic metrics!
            }
            
            # Insert into MongoDB
            result = self.negotiations_collection.insert_one(document)
            
            print(f"✅ Saved negotiation to MongoDB: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error saving to MongoDB: {e}")
            raise
    
    def get_negotiation(self, negotiation_id: str) -> Optional[Dict]:
        """
        Retrieve a negotiation by ID
        
        Args:
            negotiation_id: MongoDB document ID
            
        Returns:
            Negotiation document or None
        """
        try:
            from bson.objectid import ObjectId
            result = self.negotiations_collection.find_one({"_id": ObjectId(negotiation_id)})
            return result
        except Exception as e:
            print(f"❌ Error retrieving negotiation: {e}")
            return None
    
    def get_negotiation_by_id(self, negotiation_id: str) -> Optional[Dict]:
        """Alias for get_negotiation()"""
        return self.get_negotiation(negotiation_id)
    
    def get_negotiations_by_scenario(self, scenario_name: str, limit: int = 100) -> List[Dict]:
        """
        Get all negotiations for a specific scenario
        
        Args:
            scenario_name: Name of the scenario
            limit: Maximum number of results
            
        Returns:
            List of negotiation documents
        """
        try:
            results = self.negotiations_collection.find(
                {"scenario_name": scenario_name}
            ).sort("timestamp", -1).limit(limit)
            return list(results)
        except Exception as e:
            print(f"❌ Error querying negotiations: {e}")
            return []
    
    def get_negotiations_by_personas(
        self,
        agent_a_persona: str,
        agent_b_persona: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get all negotiations with specific persona combination
        
        Args:
            agent_a_persona: Persona of Agent A
            agent_b_persona: Persona of Agent B
            limit: Maximum number of results
            
        Returns:
            List of negotiation documents
        """
        try:
            results = self.negotiations_collection.find({
                "agent_a_persona": agent_a_persona,
                "agent_b_persona": agent_b_persona
            }).sort("timestamp", -1).limit(limit)
            return list(results)
        except Exception as e:
            print(f"❌ Error querying negotiations: {e}")
            return []
    
    def get_all_negotiations(self, limit: int = None) -> List[Dict]:
        """
        Get all negotiations
        
        Args:
            limit: Maximum number of results (None = all)
            
        Returns:
            List of negotiation documents
        """
        try:
            query = self.negotiations_collection.find().sort("timestamp", -1)
            if limit is not None:
                query = query.limit(limit)
            return list(query)
        except Exception as e:
            print(f"❌ Error querying negotiations: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about negotiations
        
        Returns:
            Dictionary with statistics
        """
        try:
            total = self.negotiations_collection.count_documents({})
            successful = self.negotiations_collection.count_documents({"agreement_reached": True})
            failed = self.negotiations_collection.count_documents({"agreement_reached": False})
            
            # Average rounds
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "avg_rounds": {"$avg": "$rounds"}
                    }
                }
            ]
            avg_result = list(self.negotiations_collection.aggregate(pipeline))
            avg_rounds = avg_result[0]["avg_rounds"] if avg_result else 0
            
            return {
                "total_negotiations": total,
                "successful_negotiations": successful,
                "failed_negotiations": failed,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "average_rounds": avg_rounds
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def save_test(
        self,
        test_name: str,
        scenario_name: str,
        agent_a_persona: str,
        agent_b_persona: str,
        negotiation_ids: List[str],
        metrics: Dict[str, Any]
    ) -> str:
        """
        Save a batch test document
        
        Args:
            test_name: Name/description of the test
            scenario_name: Scenario used
            agent_a_persona: Persona for Agent A
            agent_b_persona: Persona for Agent B
            negotiation_ids: List of negotiation document IDs from this test
            metrics: Dictionary of calculated metrics
            
        Returns:
            Test document ID
        """
        if self.tests_collection is None:
            raise ConnectionError("MongoDB not connected")
        
        test_document = {
            "test_name": test_name,
            "scenario": scenario_name,
            "agent_a_persona": agent_a_persona,
            "agent_b_persona": agent_b_persona,
            "negotiation_ids": negotiation_ids,
            "total_negotiations": len(negotiation_ids),
            "metrics": metrics,
            "created_at": datetime.utcnow(),
            "status": "completed"
        }
        
        result = self.tests_collection.insert_one(test_document)
        return str(result.inserted_id)
    
    def get_all_tests(self, limit: int = None) -> List[Dict]:
        """
        Get all test documents
        
        Args:
            limit: Maximum number of tests to return (optional)
            
        Returns:
            List of test documents
        """
        if self.tests_collection is None:
            raise ConnectionError("MongoDB not connected")
        
        cursor = self.tests_collection.find().sort("created_at", -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        tests = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            tests.append(doc)
        
        return tests
    
    def get_test_by_id(self, test_id: str) -> Optional[Dict]:
        """
        Get a specific test by ID
        
        Args:
            test_id: Test document ID
            
        Returns:
            Test document or None if not found
        """
        if self.tests_collection is None:
            raise ConnectionError("MongoDB not connected")
        
        from bson.objectid import ObjectId
        
        try:
            test_doc = self.tests_collection.find_one({"_id": ObjectId(test_id)})
            if test_doc:
                test_doc['_id'] = str(test_doc['_id'])
            return test_doc
        except Exception as e:
            print(f"Error retrieving test {test_id}: {e}")
            return None
    
    def get_test_negotiations(self, negotiation_ids: List[str]) -> List[Dict]:
        """
        Get all negotiations for a test
        
        Args:
            negotiation_ids: List of negotiation document IDs
            
        Returns:
            List of negotiation documents
        """
        if self.negotiations_collection is None:
            raise ConnectionError("MongoDB not connected")
        
        from bson.objectid import ObjectId
        
        negotiations = []
        for neg_id in negotiation_ids:
            try:
                neg = self.negotiations_collection.find_one({"_id": ObjectId(neg_id)})
                if neg:
                    neg['_id'] = str(neg['_id'])
                    negotiations.append(neg)
            except Exception as e:
                print(f"Error retrieving negotiation {neg_id}: {e}")
        
        return negotiations
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✅ MongoDB connection closed")


# Global client instance
_mongodb_client = None


def get_mongodb_client() -> MongoDBClient:
    """Get or create MongoDB client singleton"""
    global _mongodb_client
    if _mongodb_client is None:
        _mongodb_client = MongoDBClient()
    return _mongodb_client
