# LawGenie

LawGenie is an advanced contract negotiation system that leverages various AI technologies to analyze, assist, and streamline the contract negotiation process.

## Table of Contents
- [What LawGenie Does](#what-lawgenie-does)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

## What LawGenie Does

LawGenie automates and enhances the contract review process through the following steps:

1. **Document Parsing**: 
   - Uploads a contract document (PDF or DOCX) to the system.
   - Uses Upstage's document parser API to convert the contract into plain text.

2. **Clause Segmentation**:
   - Employs Llama 3.1 (running on Together AI) to split the contract text into individual clauses.
   - Structures the clauses in JSON format for further processing.

3. **AI-Powered Clause Analysis**:
   - For each clause, triggers an AI agent orchestrated through Crew AI.
   - Within each agent, the clause text is passed to the RAGTool function in Composio, which is integrated with Crew AI.
   - This RAG system queries a Chroma DB that has been pre-trained on a repository of existing contract clauses.
   - Utilizes ChatGPT-4 to generate an analysis of each clause and recommendations for potential improvements, comparing with standard clauses in the Chroma DB.

4. **User Interaction**:
   - Presents the analysis and recommendations to the user through a Streamlit interface.
   - Allows the user to choose whether to accept or reject each clause or add points for negotiation.

5. **Response Generation**:
   - Collects all user feedback, including analysis and recommendations for each clause.
   - Passes this information back to Llama 3.1 on Together AI.
   - Generates a draft response to the original contract drafter, suggesting amendments based on the analysis and user input.

## Key Features

- Automated contract parsing using Upstage's document parser API
- AI-driven clause segmentation using Llama 3.1 on Together AI
- Detailed clause analysis using Crew AI, Composio's RAGTool, and ChatGPT-4
- Comparison with standard clauses stored in Chroma DB
- User-friendly interface for reviewing and providing input on each clause
- Automated generation of response drafts for contract amendments using Llama 3.1

## Technologies Used

- Flask: Web framework for the backend API
- Streamlit: Frontend user interface
- Together AI: Hosting Llama 3.1 for text processing, clause segmentation, and response generation
- Upstage Document Parser API: Converting contracts to text format
- Crew AI: Orchestrating AI agents for clause analysis
- Composio: Providing RAGTool function for integration with Crew AI
- Chroma DB: Vector database for storing and querying standard contract clauses
- OpenAI GPT-4: Advanced language model for clause analysis and recommendations
- uv: Fast Python package installer and resolver
- Python: Primary programming language
- SQLite: Database for storing application data
- pre-commit: Managing and maintaining pre-commit hooks

## Project Structure

```
.
├── __init__.py
├── app.py                 # Flask application
├── clause_agents.py       # Definitions for AI agents
├── clause_tasks.py        # Task definitions for AI agents
├── crew.py                # Crew AI orchestration
├── db/                    # Database files
│   ├── chroma.sqlite3
│   └── ...
├── models.py              # Data models
├── streamlit_app.py       # Streamlit frontend
├── tools.py               # Utility functions and tools
└── uploads/               # Uploaded contract files
```

## Setup

1. Install the `uv` package manager:
   ```
   pip install uv
   ```

2. Clone the repository:
   ```
   git clone https://github.com/your-username/lawgenie.git
   cd lawgenie
   ```

3. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   TOGETHER_API_KEY=your_together_api_key
   UPSTAGE_API_KEY=your_upstage_api_key
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_API_BASE=your_openai_api_base
   OPENAI_MODEL_NAME=your_openai_model_name
   ```

## Usage

1. Start the Flask backend:
   ```
   uv run python app.py
   ```
   The backend will be available at `http://localhost:5002`.

2. In a separate terminal, start the Streamlit frontend:
   ```
   uv run streamlit run streamlit_app.py
   ```
   Access the frontend at `http://localhost:8503` in your web browser.

3. Upload a contract document through the Streamlit interface.

4. The system will process the document, segment it into clauses, and provide analysis and recommendations for each clause.

5. Review the analysis, accept or reject recommendations, and add negotiation points as needed.

6. Generate a response to the contract drafter based on your inputs.

## Development

### Package Management with uv

- Add a package: `uv add <package>`
- Remove a package: `uv remove <package>`
- Run a command in the virtual environment: `uv run <command>`

### Pre-commit Hooks

1. Install pre-commit hooks:
   ```
   uv run pre-commit install
   ```

2. Run pre-commit checks manually:
   ```
   uv run pre-commit run --all-files
   ```

Pre-commit hooks help maintain code quality by running checks for formatting, linting, and other issues before each commit.

### Customizing AI Agents

To modify or add new AI agents, edit the `clause_agents.py` file. Each agent is defined with a specific role, goal, and set of tools.

### Modifying RAG Functionality

The RAG system uses Chroma DB to store and query contract clauses. To update the knowledge base:

1. Add new contract documents to the `uploads/` directory.
2. Modify the `tools.py` file to update the ingestion process if necessary.
3. Run the ingestion process to update the Chroma DB.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure that your code adheres to the project's coding standards and passes all pre-commit checks before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

If you encounter any issues with the Upstage Document Parser API or Together AI, please check your API keys and ensure you have the necessary permissions.

For issues related to the AI agents or RAG system, check the `output.log` file for detailed error messages and stack traces.

Common issues and solutions:
1. API key errors: Ensure all API keys in the `.env` file are correct and up to date.
2. Database connection issues: Check if the Chroma DB is properly initialized and accessible.
3. Memory errors: If processing large contracts, you may need to increase the available memory for the Python process.

## Future Improvements

- Implement user authentication and multi-user support
- Enhance the RAG system with more sophisticated retrieval techniques
- Add support for more document formats
- Improve the user interface for easier clause-by-clause review
- Implement a feedback loop to continuously improve AI recommendations
- Expand the pre-trained contract clause database for better comparisons
- Implement version control for contract revisions
- Add support for multiple languages in contract analysis

For any additional questions or support, please open an issue in the GitHub repository or contact the maintainers directly.
