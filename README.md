# Spring Boot Generator

A Python web application that integrates with LLMs (Ollama or Azure OpenAI) to generate Spring Boot applications based on OpenAPI 3 specifications and user-defined rules.

## Features

- **OpenAPI 3 Support**: Upload and validate YAML/JSON OpenAPI specifications
- **LLM Integration**: Supports both Ollama (local) and Azure OpenAI for code generation
- **Interactive Web UI**: User-friendly interface for configuration and project generation
- **Parameter Validation**: Ensures all required parameters are provided before generation
- **Complete Project Structure**: Generates full Spring Boot projects with proper structure
- **Custom Rules**: Support for user-defined coding standards and requirements

## Prerequisites

- Python 3.8+
- Ollama (for local LLM) or Azure OpenAI API access
- OpenAPI 3 specification file (YAML or JSON)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd spring-boot-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

### Azure OpenAI Setup
1. Create an Azure OpenAI resource
2. Deploy a model (e.g., GPT-3.5-turbo or GPT-4)
3. Set the following environment variables:
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
   - `AZURE_OPENAI_API_KEY`: Your API key
   - `AZURE_OPENAI_DEPLOYMENT`: Your deployment name

### Ollama Setup (Alternative)
1. Install Ollama: https://ollama.ai/
2. Pull a model: `ollama pull llama2`
3. The application will use `http://localhost:11434` by default

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Follow the steps:
   - **Step 1**: Upload your OpenAPI 3 specification file
   - **Step 2**: Configure project parameters (Group ID, Artifact ID, etc.)
   - **Step 3**: Add custom rules (optional)
   - **Step 4**: Generate and download your Spring Boot project

## API Endpoints

- `GET /`: Web interface
- `POST /api/upload`: Upload OpenAPI specification
- `POST /api/generate`: Generate Spring Boot project
- `GET /api/download/<project_name>`: Download generated project
- `GET /api/health`: Health check

## Generated Project Structure

The application generates a complete Spring Boot project including:

- `pom.xml` with proper dependencies
- Main application class
- Controllers for each API endpoint
- DTOs/Entities for request/response models
- Services for business logic
- Repositories for data access
- Configuration files (`application.yml`)
- Basic tests
- Proper package structure

## Required Parameters

The following parameters are required for project generation:

- **Group ID**: Maven group identifier (e.g., `com.example`)
- **Artifact ID**: Maven artifact identifier (e.g., `demo`)
- **Version**: Project version (e.g., `0.0.1-SNAPSHOT`)
- **Package Name**: Java package name (e.g., `com.example.demo`)

## Optional Parameters

- **Java Version**: Java version (11, 17, 21)
- **Spring Boot Version**: Spring Boot version (2.7.0, 3.1.0, 3.2.0)
- **Description**: Project description
- **User Rules**: Custom requirements and coding standards

## Error Handling

The application includes comprehensive error handling:

- OpenAPI specification validation
- Required parameter validation
- LLM API error handling
- File upload validation
- Fallback project generation if LLM fails

## Development

To run in development mode:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.