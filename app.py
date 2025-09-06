import os
import yaml
import json
import requests
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename
import tempfile
import zipfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'yaml', 'yml', 'json'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

class LLMClient:
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        
    def generate_spring_boot_code(self, openapi_spec, project_config, user_rules=""):
        """Generate Spring Boot code using LLM"""
        
        # Prepare the prompt
        prompt = self._create_prompt(openapi_spec, project_config, user_rules)
        
        # Try Azure OpenAI first, then fallback to Ollama
        if self.azure_endpoint and self.azure_api_key:
            return self._call_azure_openai(prompt)
        else:
            return self._call_ollama(prompt)
    
    def _create_prompt(self, openapi_spec, project_config, user_rules):
        """Create a comprehensive prompt for code generation"""
        
        prompt = f"""
You are an expert Spring Boot developer. Generate a complete Spring Boot application based on the following OpenAPI 3 specification and project configuration.

PROJECT CONFIGURATION:
- Group ID: {project_config.get('groupId', 'com.example')}
- Artifact ID: {project_config.get('artifactId', 'demo')}
- Version: {project_config.get('version', '0.0.1-SNAPSHOT')}
- Java Version: {project_config.get('javaVersion', '17')}
- Spring Boot Version: {project_config.get('springBootVersion', '3.2.0')}
- Package Name: {project_config.get('packageName', 'com.example.demo')}
- Description: {project_config.get('description', 'Demo project for Spring Boot')}

USER RULES:
{user_rules}

OPENAPI SPECIFICATION:
{json.dumps(openapi_spec, indent=2)}

REQUIREMENTS:
1. Generate a complete Spring Boot project structure
2. Create all necessary controllers, services, repositories, and entities based on the OpenAPI spec
3. Include proper validation annotations
4. Add appropriate error handling
5. Include a proper pom.xml with all necessary dependencies
6. Create application.yml with proper configuration
7. Add proper package structure
8. Include basic tests
9. Follow Spring Boot best practices

Please provide the complete project structure as a JSON response with the following format:
{{
    "files": {{
        "pom.xml": "content here",
        "src/main/java/.../Application.java": "content here",
        "src/main/resources/application.yml": "content here",
        // ... all other files
    }}
}}

Generate only the essential files for a working Spring Boot application. Focus on:
- Main application class
- Controllers for each API endpoint
- DTOs/Entities for request/response models
- Services for business logic
- Repositories for data access
- Configuration files
- Basic tests
"""
        return prompt
    
    def _call_azure_openai(self, prompt):
        """Call Azure OpenAI API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'api-key': self.azure_api_key
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": "You are an expert Spring Boot developer."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.azure_endpoint}/openai/deployments/{self.azure_deployment}/chat/completions?api-version=2023-12-01-preview",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"Azure OpenAI API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Error calling Azure OpenAI: {str(e)}")
    
    def _call_ollama(self, prompt):
        """Call Ollama API"""
        try:
            data = {
                "model": "llama2",  # You can change this to your preferred model
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['response']
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"Error calling Ollama: {str(e)}")

class SpringBootGenerator:
    def __init__(self):
        self.llm_client = LLMClient()
    
    def generate_project(self, openapi_spec, project_config, user_rules=""):
        """Generate complete Spring Boot project"""
        
        # Validate required parameters
        required_params = ['groupId', 'artifactId', 'version', 'packageName']
        missing_params = [param for param in required_params if not project_config.get(param)]
        
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
        
        # Generate code using LLM
        try:
            generated_code = self.llm_client.generate_spring_boot_code(openapi_spec, project_config, user_rules)
        except Exception as e:
            print(f"LLM generation failed: {str(e)}, falling back to basic project generation")
            return self._create_fallback_project(openapi_spec, project_config)
        
        # Parse the generated code
        try:
            # Try to extract JSON from the response
            if '```json' in generated_code:
                json_start = generated_code.find('```json') + 7
                json_end = generated_code.find('```', json_start)
                json_str = generated_code[json_start:json_end].strip()
            elif '{' in generated_code and '}' in generated_code:
                json_start = generated_code.find('{')
                json_end = generated_code.rfind('}') + 1
                json_str = generated_code[json_start:json_end]
            else:
                json_str = generated_code
            
            project_files = json.loads(json_str)
            
            # Create project directory
            project_name = project_config['artifactId']
            project_path = os.path.join(GENERATED_FOLDER, project_name)
            os.makedirs(project_path, exist_ok=True)
            
            # Write all files
            for file_path, content in project_files.get('files', {}).items():
                full_path = os.path.join(project_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Create ZIP file
            zip_path = os.path.join(GENERATED_FOLDER, f"{project_name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_path)
                        zipf.write(file_path, arcname)
            
            return {
                'success': True,
                'project_path': project_path,
                'zip_path': zip_path,
                'message': f'Spring Boot project generated successfully: {project_name}'
            }
            
        except (json.JSONDecodeError, Exception) as e:
            # If JSON parsing fails or LLM call fails, create a basic project structure
            print(f"LLM generation failed: {str(e)}, falling back to basic project generation")
            return self._create_fallback_project(openapi_spec, project_config)
    
    def _create_fallback_project(self, openapi_spec, project_config):
        """Create a basic Spring Boot project structure as fallback"""
        project_name = project_config['artifactId']
        project_path = os.path.join(GENERATED_FOLDER, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Create basic pom.xml
        pom_content = self._generate_pom_xml(project_config)
        with open(os.path.join(project_path, 'pom.xml'), 'w') as f:
            f.write(pom_content)
        
        # Create basic application class
        app_content = self._generate_main_application(project_config)
        app_dir = os.path.join(project_path, 'src', 'main', 'java', *project_config['packageName'].split('.'))
        os.makedirs(app_dir, exist_ok=True)
        with open(os.path.join(app_dir, 'Application.java'), 'w') as f:
            f.write(app_content)
        
        # Create application.yml
        yml_content = self._generate_application_yml()
        resources_dir = os.path.join(project_path, 'src', 'main', 'resources')
        os.makedirs(resources_dir, exist_ok=True)
        with open(os.path.join(resources_dir, 'application.yml'), 'w') as f:
            f.write(yml_content)
        
        # Create ZIP file
        zip_path = os.path.join(GENERATED_FOLDER, f"{project_name}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)
        
        return {
            'success': True,
            'project_path': project_path,
            'zip_path': zip_path,
            'message': f'Basic Spring Boot project generated: {project_name}'
        }
    
    def _generate_pom_xml(self, config):
        """Generate basic pom.xml"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>{config.get('springBootVersion', '3.2.0')}</version>
        <relativePath/>
    </parent>
    
    <groupId>{config['groupId']}</groupId>
    <artifactId>{config['artifactId']}</artifactId>
    <version>{config['version']}</version>
    <name>{config['artifactId']}</name>
    <description>{config.get('description', 'Demo project for Spring Boot')}</description>
    
    <properties>
        <java.version>{config.get('javaVersion', '17')}</java.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>"""
    
    def _generate_main_application(self, config):
        """Generate main application class"""
        package_name = config['packageName']
        class_name = ''.join(word.capitalize() for word in config['artifactId'].split('-'))
        
        return f"""package {package_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {class_name}Application {{
    
    public static void main(String[] args) {{
        SpringApplication.run({class_name}Application.class, args);
    }}
}}"""
    
    def _generate_application_yml(self):
        """Generate basic application.yml"""
        return """server:
  port: 8080

spring:
  application:
    name: demo
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password: password
  h2:
    console:
      enabled: true
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true

logging:
  level:
    com.example: DEBUG"""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and validate OpenAPI specification"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Parse and validate OpenAPI spec
            spec_dict, spec_url = read_from_filename(filepath)
            validate_spec(spec_dict)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'spec': spec_dict,
                'message': 'OpenAPI specification uploaded and validated successfully'
            })
            
        except Exception as e:
            return jsonify({'error': f'Invalid OpenAPI specification: {str(e)}'}), 400
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/generate', methods=['POST'])
def generate_project():
    """Generate Spring Boot project from OpenAPI spec"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        openapi_spec = data.get('openapi_spec')
        project_config = data.get('project_config', {})
        user_rules = data.get('user_rules', '')
        
        if not openapi_spec:
            return jsonify({'error': 'OpenAPI specification is required'}), 400
        
        # Validate required project configuration
        required_params = ['groupId', 'artifactId', 'version', 'packageName']
        missing_params = [param for param in required_params if not project_config.get(param)]
        
        if missing_params:
            return jsonify({
                'error': f'Missing required parameters: {", ".join(missing_params)}',
                'missing_params': missing_params
            }), 400
        
        # Generate project
        generator = SpringBootGenerator()
        result = generator.generate_project(openapi_spec, project_config, user_rules)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<project_name>')
def download_project(project_name):
    """Download generated project as ZIP file"""
    zip_path = os.path.join(GENERATED_FOLDER, f"{project_name}.zip")
    
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name=f"{project_name}.zip")
    else:
        return jsonify({'error': 'Project not found'}), 404

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Spring Boot Generator API is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)