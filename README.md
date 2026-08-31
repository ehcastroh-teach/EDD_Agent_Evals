# EDD Agent Evals

Most LLM agents fail silently. A wrong tool is called, a hallucinated column slips into a SQL query, a chart specification comes back malformed, and the user still sees *some* answer back - just not the right one. Debugging by rerunning prompts and staring at print output does not scale.

This three-notebook series teaches **Evaluation-Driven Development (EDD)** for LLM agents. You build a small multi-tool agent, instrument it with OpenTelemetry tracing via Arize Phoenix so its behavior becomes queryable data, then run LLM-as-judge and programmatic evaluations to identify failure modes and confirm that a targeted fix actually moved the score.

## Learning Objectives

- Define agent tools (database lookup, data analysis, data visualization) as callable Python functions
- Implement a router that selects and sequences tools in response to a natural language query
- Set up Arize Phoenix and add OpenTelemetry tracing to every LLM call and tool invocation
- Query trace spans programmatically using `SpanQuery` to retrieve evaluation inputs
- Apply Phoenix's built-in tool calling evaluator and write custom LLM-as-judge prompts
- Implement a deterministic code runnability eval without LLM cost
- Write evaluation scores back to Phoenix and use them to drive targeted prompt improvements

## Data / File Dictionary

| File | Description |
|---|---|
| `01_evaluating_agents.ipynb` | Build a three-tool agent with a router, then compare baseline and improved SQL prompts |
| `02_tracing_agents.ipynb` | Add Phoenix/OpenTelemetry tracing to the agent from notebook 01 |
| `03_router_and_skill_evals.ipynb` | Run tool calling, code runnability, clarity, and SQL quality evals; write scores to Phoenix |
| `data/Store_Sales_Price_Elasticity_Promotions_Data.parquet` | Retail sales transaction data used as the agent's knowledge source |
| `requirements.txt` | Python package dependencies |

## Workflow

```
01_evaluating_agents.ipynb
  -> Build tools + router
  -> Compare baseline vs. improved SQL prompt
       |
       v
02_tracing_agents.ipynb
  -> Add @tracer.tool(), @tracer.chain(), and agent span
  -> Run agent and inspect trace tree in Phoenix
       |
       v
03_router_and_skill_evals.ipynb
  -> Query spans from Phoenix
  -> Score: tool calling | code runnability | response clarity | SQL quality
  -> Write scores back to Phoenix
  -> Apply targeted improvement and re-run
```

## Step-by-Step Walkthrough

**Notebook 01** starts from scratch. Three tools are built as Python functions - a database lookup tool that translates natural language to SQL via DuckDB, a data analysis tool that summarizes query results, and a visualization tool that generates matplotlib code. A router loop drives the agent: the LLM selects which tool to call, calls it, reads the result, and decides whether to call another tool or return a final answer. The final section shows why the original SQL prompt fails on ambiguous queries and demonstrates the improved prompt that fixes it.

**Notebook 02** adds observability to the same agent without changing its logic. Arize Phoenix is started locally and registered as the OpenTelemetry collector. `@tracer.tool()`, `@tracer.chain()`, and a manually created agent span turn every function call into a visible span. After running the agent, the Phoenix UI shows the full trace tree - every LLM call, every tool invocation, every intermediate step - as structured, queryable data.

**Notebook 03** operationalizes the EDD cycle. The agent runs against a batch of questions to populate Phoenix with spans. Four evaluations then score each span type: the tool calling eval (did the router call the right tool?), the code runnability eval (does the generated visualization code execute?), the response clarity eval (is the final answer coherent and direct?), and the SQL generation eval (does the SQL correctly answer the question?). All scores are written back to Phoenix. The final section shows how to apply the improved SQL prompt from notebook 01 as a targeted fix driven by eval results.

## How to Run

Prerequisites: Python 3.10+, an OpenAI API key, and Arize Phoenix.

```bash
# Clone the repo and install dependencies
pip install -r requirements.txt

# Add your OpenAI API key to a .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Start Phoenix in a separate terminal before running notebooks 02 and 03.
# The CLI entrypoint is preferred; the module form still works as a fallback.
phoenix serve
# Fallback: python -m phoenix.server.main serve

# Run notebooks in order
jupyter notebook
```

Open `01_evaluating_agents.ipynb` first. Notebooks 02 and 03 depend on Phoenix running locally.

## Key Concepts Glossary

**Agent** - An LLM combined with tools it can call to retrieve information or take actions, controlled by a loop that runs until the LLM decides it has enough to answer.

**Router** - The LLM call at the center of the agent loop that decides which tool (if any) to call next, given the conversation history and the available tool schemas.

**Span** - A single unit of work recorded by OpenTelemetry - one LLM call, one tool invocation, or one pipeline step. Spans have a type, a start time, a duration, and input/output attributes.

**Trace** - The complete tree of spans generated by a single agent run. A trace shows the entire sequence of calls from the user's first message to the agent's final answer.

**Evaluation-Driven Development (EDD)** - A development practice for AI systems: instrument the system to collect structured data, evaluate that data with programmatic or LLM-based judges, identify failure patterns, and make one targeted change per improvement cycle.

**LLM-as-judge** - An evaluation technique that uses a separate, often larger LLM to score another LLM's output against a rubric. Used when correctness cannot be determined by a simple function (e.g., response clarity, reasoning quality).

**Tool calling** - The mechanism by which a router LLM selects a tool and fills in its parameters, as specified by the OpenAI function-calling API. The router does not execute the tool - it returns a structured request that the agent loop executes.

**Arize Phoenix** - An open-source LLM observability platform that collects OpenTelemetry spans, displays trace trees, and supports evaluation workflows including writing eval scores back alongside traces.

**Structured outputs** - An OpenAI API feature that constrains the LLM's response to match a specific JSON schema (defined as a Pydantic model). Used in the visualization tool to reliably extract chart configuration before passing it to a code generation step.

**Prompt improvement** - In EDD, a change to a prompt that is made in direct response to an observed failure mode in eval scores - not as a general quality improvement, but as a targeted fix for a specific, measured problem.

## Further Reading

- OpenAI Function Calling guide
- OpenAI Structured Outputs guide
- Arize Phoenix Tracing documentation
- OpenInference span-kinds reference (agent, chain, tool, LLM)
- OpenTelemetry concepts: traces, spans, and context propagation
- "Building LLM Applications" - general agent architecture patterns
- LLM evaluation survey literature (LLM-as-Judge methods)

## Credits and Acknowledgements

Sales dataset: Store Sales Price Elasticity Promotions dataset (public domain retail transaction data).

---

## Contact

<div align="center">
  <img src="images/thumbnails/ehcastroh_teach_banner_flower.png" alt="ehcastroh" width="90" style="border-radius: 50%;" />

  <sub>ehcastroh</sub>

  <a href="https://github.com/ehcastroh">GitHub</a> · <a href="https://www.linkedin.com/in/ehcastroh/">LinkedIn</a>
</div>
