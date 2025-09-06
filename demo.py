#!/usr/bin/env python3
"""
Demo script for Spring Boot Generator
This script demonstrates how to use the API programmatically
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
SAMPLE_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "User Management API",
        "description": "A simple API for managing users",
        "version": "1.0.0"
    },
    "paths": {
        "/users": {
            "get": {
                "summary": "Get all users",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": "Create a new user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateUserRequest"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "User created successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    }
                }
            }
        }
    },
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "required": ["id", "name", "email"],
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "integer", "minimum": 0, "maximum": 150}
                }
            },
            "CreateUserRequest": {
                "type": "object",
                "required": ["name", "email"],
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "age": {"type": "integer", "minimum": 0, "maximum": 150}
                }
            }
        }
    }
}

PROJECT_CONFIG = {
    "groupId": "com.example",
    "artifactId": "user-management-api",
    "version": "1.0.0",
    "packageName": "com.example.usermanagement",
    "javaVersion": "17",
    "springBootVersion": "3.2.0",
    "description": "User Management API - Generated from OpenAPI spec"
}

USER_RULES = """
- Use Spring Boot best practices
- Include proper validation annotations
- Add comprehensive error handling
- Use JPA repositories for data access
- Include unit tests for controllers and services
- Follow RESTful API conventions
- Add proper logging
"""

def check_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API is healthy and running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the application is running on http://localhost:5000")
        return False

def generate_project():
    """Generate a Spring Boot project"""
    print("\n🚀 Generating Spring Boot project...")
    
    payload = {
        "openapi_spec": SAMPLE_OPENAPI_SPEC,
        "project_config": PROJECT_CONFIG,
        "user_rules": USER_RULES
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ {result['message']}")
                print(f"📁 Project path: {result['project_path']}")
                print(f"📦 ZIP file: {result['zip_path']}")
                return result.get("project_path", "").split("/")[-1]
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The generation process might take longer.")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def download_project(project_name):
    """Download the generated project"""
    if not project_name:
        print("❌ No project name provided for download")
        return
    
    print(f"\n📥 Downloading project: {project_name}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/download/{project_name}")
        
        if response.status_code == 200:
            filename = f"{project_name}.zip"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ Project downloaded as: {filename}")
        else:
            print(f"❌ Download failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Download error: {str(e)}")

def main():
    """Main demo function"""
    print("🎯 Spring Boot Generator Demo")
    print("=" * 50)
    
    # Check API health
    if not check_health():
        return
    
    # Generate project
    project_name = generate_project()
    
    if project_name:
        # Download project
        download_project(project_name)
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Extract the downloaded ZIP file")
        print("2. Navigate to the project directory")
        print("3. Run: mvn spring-boot:run")
        print("4. Visit: http://localhost:8080")
    else:
        print("\n❌ Demo failed. Please check the logs above.")

if __name__ == "__main__":
    main()