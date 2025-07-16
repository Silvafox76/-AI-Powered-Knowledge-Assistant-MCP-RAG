#!/usr/bin/env python3
"""
Comprehensive system test script for AI Knowledge Assistant.
Tests authentication, document ingestion, RAG queries, and MCP agents.
"""

import requests
import json
import time
import os
import sys
from typing import Dict, Any, Optional

class SystemTester:
    """
    Comprehensive system tester for the AI Knowledge Assistant.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_health_check(self) -> bool:
        """Test the health check endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_authentication(self) -> bool:
        """Test user authentication."""
        try:
            # Test login with default credentials
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                self.log_test("Authentication", True, "Login successful")
                return True
            else:
                self.log_test("Authentication", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_user_info(self) -> bool:
        """Test getting current user info."""
        try:
            response = self.session.get(f"{self.base_url}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                username = data.get("username")
                self.log_test("User Info", True, f"User: {username}")
                return True
            else:
                self.log_test("User Info", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Info", False, f"Error: {str(e)}")
            return False
    
    def test_text_ingestion(self) -> bool:
        """Test text content ingestion."""
        try:
            test_content = """
            PRINCE2 Project Management Methodology
            
            PRINCE2 (Projects IN Controlled Environments) is a structured project management methodology.
            
            Key Principles:
            1. Continued business justification
            2. Learn from experience
            3. Defined roles and responsibilities
            4. Manage by stages
            5. Manage by exception
            6. Focus on products
            7. Tailor to suit the project environment
            
            This methodology is widely used in the UK government and private sector.
            """
            
            ingestion_data = {
                "content": test_content,
                "content_type": "text/plain",
                "metadata": {
                    "source": "test_document",
                    "title": "PRINCE2 Overview",
                    "category": "project_management"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/ingest/text",
                json=ingestion_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Text Ingestion", True, f"Ingested successfully")
                return True
            else:
                self.log_test("Text Ingestion", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Text Ingestion", False, f"Error: {str(e)}")
            return False
    
    def test_rag_query(self) -> bool:
        """Test RAG query functionality."""
        try:
            query_data = {
                "query": "What are the PRINCE2 principles?",
                "mode": "rag"
            }
            
            response = self.session.post(
                f"{self.base_url}/query/rag",
                json=query_data
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                if "PRINCE2" in response_text or "principles" in response_text.lower():
                    self.log_test("RAG Query", True, "Relevant response received")
                    return True
                else:
                    self.log_test("RAG Query", False, "Response not relevant")
                    return False
            else:
                self.log_test("RAG Query", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("RAG Query", False, f"Error: {str(e)}")
            return False
    
    def test_mcp_query(self) -> bool:
        """Test MCP agent query functionality."""
        try:
            query_data = {
                "query": "What are the key PRINCE2 themes?",
                "mode": "mcp",
                "agent_type": "prince2"
            }
            
            response = self.session.post(
                f"{self.base_url}/query/mcp",
                json=query_data
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_used = data.get("agent_used")
                response_text = data.get("response", "")
                self.log_test("MCP Query", True, f"Agent: {agent_used}")
                return True
            else:
                self.log_test("MCP Query", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("MCP Query", False, f"Error: {str(e)}")
            return False
    
    def test_agents_list(self) -> bool:
        """Test getting available agents."""
        try:
            response = self.session.get(f"{self.base_url}/agents")
            
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", [])
                agent_count = len(agents)
                self.log_test("Agents List", True, f"Found {agent_count} agents")
                return True
            else:
                self.log_test("Agents List", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Agents List", False, f"Error: {str(e)}")
            return False
    
    def test_stats(self) -> bool:
        """Test getting knowledge base statistics."""
        try:
            response = self.session.get(f"{self.base_url}/stats")
            
            if response.status_code == 200:
                data = response.json()
                total_chunks = data.get("total_chunks", 0)
                self.log_test("Statistics", True, f"Total chunks: {total_chunks}")
                return True
            else:
                self.log_test("Statistics", False, f"Status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Statistics", False, f"Error: {str(e)}")
            return False
    
    def test_unauthorized_access(self) -> bool:
        """Test that endpoints require authentication."""
        try:
            # Create session without auth token
            unauth_session = requests.Session()
            
            response = unauth_session.post(
                f"{self.base_url}/query/rag",
                json={"query": "test", "mode": "rag"}
            )
            
            if response.status_code in [401, 403]:
                self.log_test("Unauthorized Access", True, "Properly blocked")
                return True
            else:
                self.log_test("Unauthorized Access", False, f"Should be blocked but got: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized Access", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all system tests."""
        print("🚀 Starting AI Knowledge Assistant System Tests\n")
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Authentication", self.test_authentication),
            ("User Info", self.test_user_info),
            ("Text Ingestion", self.test_text_ingestion),
            ("RAG Query", self.test_rag_query),
            ("MCP Query", self.test_mcp_query),
            ("Agents List", self.test_agents_list),
            ("Statistics", self.test_stats),
            ("Unauthorized Access", self.test_unauthorized_access),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is ready for production.")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": (passed / total) * 100,
            "results": self.test_results
        }

def main():
    """Main function to run system tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Knowledge Assistant System Tester")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--output",
        help="Output file for test results (JSON format)"
    )
    
    args = parser.parse_args()
    
    # Run tests
    tester = SystemTester(args.url)
    results = tester.run_all_tests()
    
    # Save results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Test results saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if results["passed_tests"] == results["total_tests"] else 1)

if __name__ == "__main__":
    main()

