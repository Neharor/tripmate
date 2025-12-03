"""MongoDB Atlas Data API client - bypasses SSL issues"""
import requests
import os
from typing import Dict, List, Optional, Any

class AtlasDataAPI:
    """MongoDB Atlas Data API wrapper"""
    
    def __init__(self):
        self.api_key = os.getenv('ATLAS_API_KEY')
        self.app_id = os.getenv('ATLAS_APP_ID')
        self.cluster = "Cluster0"
        self.database = "tripmate_db"
        self.base_url = f"https://data.mongodb-api.com/app/{self.app_id}/endpoint/data/v1"
        
        self.headers = {
            'Content-Type': 'application/json',
            'api-key': self.api_key
        }
    
    def find_one(self, collection: str, filter: Dict) -> Optional[Dict]:
        """Find single document"""
        url = f"{self.base_url}/action/findOne"
        payload = {
            "dataSource": self.cluster,
            "database": self.database,
            "collection": collection,
            "filter": filter
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('document')
        return None
    
    def find(self, collection: str, filter: Dict = None, limit: int = 100) -> List[Dict]:
        """Find multiple documents"""
        url = f"{self.base_url}/action/find"
        payload = {
            "dataSource": self.cluster,
            "database": self.database,
            "collection": collection,
            "filter": filter or {},
            "limit": limit
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('documents', [])
        return []
    
    def insert_one(self, collection: str, document: Dict) -> Optional[str]:
        """Insert single document, returns insertedId"""
        url = f"{self.base_url}/action/insertOne"
        payload = {
            "dataSource": self.cluster,
            "database": self.database,
            "collection": collection,
            "document": document
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 201:
            return response.json().get('insertedId')
        return None
    
    def update_one(self, collection: str, filter: Dict, update: Dict) -> bool:
        """Update single document"""
        url = f"{self.base_url}/action/updateOne"
        payload = {
            "dataSource": self.cluster,
            "database": self.database,
            "collection": collection,
            "filter": filter,
            "update": update
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return response.status_code == 200
    
    def delete_one(self, collection: str, filter: Dict) -> bool:
        """Delete single document"""
        url = f"{self.base_url}/action/deleteOne"
        payload = {
            "dataSource": self.cluster,
            "database": self.database,
            "collection": collection,
            "filter": filter
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        return response.status_code == 200

# Global instance
atlas_api = None

def init_atlas_api():
    """Initialize Atlas Data API"""
    global atlas_api
    atlas_api = AtlasDataAPI()
    return atlas_api
