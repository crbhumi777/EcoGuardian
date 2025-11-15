# 🌍 EcoGuardian – Multi-Agent Sustainability Assistant

EcoGuardian is a multi-agent, AI-powered sustainability assistant that helps individuals understand, measure, and reduce their carbon footprint. It uses Google’s Gemini models, the Agent Development Kit (ADK), custom tools, and memory to create a personalized environmental advisor.

---

## 1. Problem Statement

People struggle to understand their real carbon footprint and make informed decisions about reducing it. Most calculators require manual input, lack personalization, and offer generic or unclear guidance.

### ✔ Solution

EcoGuardian solves this by enabling:
- Automatic extraction of lifestyle activities from natural language  
- Accurate carbon footprint estimation across travel, electricity, and food  
- Personalized AI-generated recommendations based on the largest emission categories  
- Emission tracking over time using session memory and long-term storage  

This project fits the “Agents for Good” track by promoting sustainability and environmental awareness.

---

## 2. System Architecture

EcoGuardian is built as a multi-agent ecosystem orchestrated by a central controller.

### Agents:
- **OrchestratorAgent** — Routes user queries, manages workflow, composes final responses  
- **DataFetcherAgent** — Extracts structured activity data from natural language  
- **CarbonCalculatorAgent** — Computes emissions using custom tools  
- **RecommendationAgent** — Uses Gemini to provide tailored carbon reduction advice  
- **ProgressTrackerAgent** — Stores user history and reports progress  

### Tools:
- `electricity_tool.py`  
- `product_alternatives_tool.py`  
- `carbon_calculation_tools.py`  
- `mcp_emissions_tool.py`  

### ADK Concepts Used:
- Multi-agent orchestration  
- Sequential + parallel flows  
- Gemini-powered reasoning  
- Custom tools  
- MCP-ready structure  
- Long-running operation support  
- Sessions & memory  
- Long-term memory  
- Context engineering  
- Observability (logs & metrics)  
- Evaluation  
- Deployment readiness

---

## 3. Directory Structure

```text
EcoGuardian/
│  
├── agents/
│   ├── orchestrator_agent.py
│   ├── data_fetcher_agent.py
│   ├── carbon_calculator_agent.py
│   ├── recommendation_agent.py
│   └── progress_tracker_agent.py
│  
├── tools/
│   ├── electricity_tool.py
│   ├── product_alternatives_tool.py
│   ├── carbon_calculation_tools.py
│   └── mcp_emissions_tool.py
│  
├── memory/
│   └── memory_service.py
│  
├── observability/
│   ├── logging_config.py
│   └── metrics.py
│  
├── evaluation/
│   └── evaluate.py
│  
├── deployment/
│   ├── cloud_run_example.md
│   └── agent_engine_config.json
│  
├── main_demo.py
├── config.py
├── requirements.txt
├── architecture_diagram.png
├── .env.example
└── README.md
└── ui_app.py

```

---

## 4. Setup & Installation

### 1. Clone the repository  
```bash
git clone https://github.com/crbhumi777/EcoGuardian
cd EcoGuardian
```

### 2. Create a virtual environment  
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies  
```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key  
Create a file named `.env`:

```env
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

### 5. Run the app  
```bash
streamlit run ui_app.py
```

---

## 6. Evaluation

Includes:
- LLM-as-a-Judge evaluation script  
- Tool usage scoring  
- Response quality checks  

Located in: `evaluation/evaluate.py`

---

## 7. Limitations

- Emission factors are approximations  
- No live Maps API  
- Food emissions simplified  
- Not a certified carbon calculation tool  

This project focuses on demonstrating ADK concepts and agent workflows.

---

## 8. Future Improvements

- Add accurate carbon emissions datasets  
- Integrate Google Maps distance tool  
- Add sustainability goals + reminders
- Monthly carbon reports
