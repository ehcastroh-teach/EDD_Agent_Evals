# EDD Agent Evals

Most LLM agents fail silently. A wrong tool is called, a hallucinated column slips into a SQL query, a chart specification comes back malformed - and the user still sees some answer. Just not the right one. Debugging by rerunning prompts and staring at print output does not scale past a handful of queries. This three-notebook series teaches **Evaluation-Driven Development (EDD)** for LLM agents: build a small multi-tool agent, instrument it with OpenTelemetry tracing via Arize Phoenix so its behavior becomes queryable data, then run LLM-as-judge and programmatic evaluations to identify failure modes and confirm that a targeted fix actually moved the score.

## Learning Objectives

- Define agent tools (database lookup, data analysis, data visualization) as callable Python functions with tool schemas that the router LLM can read
- Implement a router loop that selects and sequences tools in response to a natural language query, preserving conversation history across turns
- Set up Arize Phoenix locally and register an OpenTelemetry tracer provider that sends spans to the Phoenix collector
- Apply `@tracer.tool()`, `@tracer.chain()`, and manual agent spans to instrument every function call without changing its logic
- Query trace spans programmatically using `SpanQuery` to extract evaluation inputs at batch scale
- Apply Phoenix's built-in tool calling evaluator and write custom LLM-as-judge prompts for response clarity and SQL quality
- Implement a deterministic code runnability eval using `exec` without LLM cost
- Write evaluation scores back to Phoenix so they appear alongside traces and drive targeted prompt improvements

## Data / File Dictionary

| File | Description |
|---|---|
| `01_evaluating_agents.ipynb` | Build a three-tool agent with a router loop, then compare a baseline SQL prompt against a schema-aware improved version |
| `02_tracing_agents.ipynb` | Add Phoenix/OpenTelemetry tracing to the agent from notebook 01, making every LLM call and tool invocation a visible, queryable span |
| `03_router_and_skill_evals.ipynb` | Run tool calling, code runnability, response clarity, and SQL quality evals against a batch of questions; write scores to Phoenix |
| `data/Store_Sales_Price_Elasticity_Promotions_Data.parquet` | Retail sales transaction dataset used as the agent's knowledge source (public domain) |
| `requirements.txt` | Python package dependencies for all three notebooks |

## Workflow Diagram

```
01_evaluating_agents.ipynb
  -> Build three agent tools (database lookup, analysis, visualization)
  -> Assemble the router loop (tool schemas + while-loop dispatcher)
  -> Identify SQL hallucination failure; compare baseline vs. improved prompt
       |
       v
02_tracing_agents.ipynb
  -> Register Phoenix as the OpenTelemetry collector
  -> Apply @tracer.tool(), @tracer.chain(), and agent span to the agent
  -> Run a query; inspect the full trace tree in Phoenix UI
       |
       v
03_router_and_skill_evals.ipynb
  -> Run the traced agent against a six-question batch
  -> Query spans with SpanQuery to extract eval inputs
  -> Score: tool calling | code runnability | response clarity | SQL quality
  -> Write scores back to Phoenix alongside traces
  -> Apply improved SQL prompt as a targeted, data-driven fix
```

## Step-by-Step Walkthrough

**Notebook 01 - Build the agent and find a failure mode**

The notebook starts by building each tool as a standalone Python function. The database lookup tool runs in three steps: load the Parquet file into an in-memory DuckDB table, generate a SQL query from the user's natural language input using an LLM call, and execute the query against DuckDB. DuckDB is chosen because it reads Parquet natively without a separate database server - the entire knowledge source is a single file. The data analysis tool takes the lookup result and a question, then calls the LLM once to produce an analytical summary. It is deliberately simple: one prompt, one call, one returned string. Simplicity matters here because the tool's job is interpretation, not transformation - additional complexity would only obscure failures later.

The visualization tool is more elaborate because chart generation benefits from structure. A first LLM call uses OpenAI structured outputs (a Pydantic model enforces the response schema) to extract a configuration object - chart type, axis columns, title. A second call uses that configuration to generate executable Python code. Splitting the task into two calls is an explicit tradeoff: it adds one API round-trip but makes the chart config inspectable and debuggable without parsing a raw string.

The router loop is a `while True` that calls the LLM with the current message history and the tool list, appends every response to history to preserve context, and either dispatches tool calls or breaks when the LLM produces a final answer. Tool schemas (OpenAI function-calling format) are the contract between the router and the Python functions - the schema's `description` field is what the LLM reads to decide which tool to call, so it must be precise.

The notebook closes by reproducing a concrete failure: the baseline SQL prompt does not tell the LLM what columns exist, so it invents plausible-sounding column names. The improved prompt passes the column list and instructs the LLM to return an `ERROR` sentinel if a requested column is absent. This is the first EDD cycle - observe a failure, make one targeted change, verify the result.

**Notebook 02 - Make the agent's behavior observable**

The agent from notebook 01 works but is opaque. When it returns a wrong answer, the final string gives no indication of where things went wrong. Notebook 02 adds observability without touching the agent's logic.

Arize Phoenix is started locally as the OpenTelemetry collector. `register()` creates a tracer provider pointing at `http://localhost:6006/v1/traces`. The `OpenAIInstrumentor` auto-patches the OpenAI client so that every `chat.completions.create()` call emits an LLM-typed span with the full prompt, response, and token counts - zero code changes required. Manual spans are added for tool and chain functions using `@tracer.tool()` and `@tracer.chain()`. These decorators are from the OpenInference semantic conventions layer; they ensure Phoenix categorizes each span correctly so the UI can filter and aggregate by span type. The entire agent run is wrapped in a manually created agent-typed root span via `start_main_span`, making every nested call a child in a single trace tree.

After running a query, the Phoenix UI at `http://localhost:6006` shows the complete call graph for that agent run - which tools were called, in what order, with what inputs and outputs - as structured, filterable data. This is qualitatively different from print debugging: it survives across runs, supports batch inspection, and becomes the input to automated evaluations.

**Notebook 03 - Evaluate at batch scale and close the loop**

Notebook 02 produced one trace at a time. Notebook 03 runs the agent against six questions chosen to exercise all three tools in different combinations, generating enough spans to evaluate systematically. `SpanQuery` retrieves spans from Phoenix by span kind (tool, LLM, chain, agent), joining span attributes to produce a flat dataframe of evaluation inputs - no manual copy-paste from the UI.

Four evaluations then run against this data, each chosen because it cannot be handled by the others:

- The **tool calling eval** uses Phoenix's built-in `ToolCallClassificationEvaluator` to check whether the router called the right tool. This is an LLM judge eval - it requires understanding intent.
- The **code runnability eval** calls `exec()` on each generated visualization string and returns a boolean. This is deterministic and free - LLM judgment would add cost without improving accuracy for a binary pass/fail question.
- The **response clarity eval** uses a custom LLM-as-judge prompt that classifies the final agent answer as `clear` or `unclear`. The rubric is written to catch answers that are technically correct but poorly structured or too verbose.
- The **SQL generation eval** uses a custom judge that receives the user's instruction and the generated SQL, returning `correct` or `incorrect`. This checks the tool's internal artifact, not just whether the right tool was called.

All four scores are written back to Phoenix using `log_evaluations`, making them visible in the trace UI alongside the spans they annotate. The final section shows how the improved SQL prompt from notebook 01 - originally introduced as a manual hypothesis - is now a data-driven fix supported by a concrete eval score.

## How to Run

Prerequisites: Python 3.10+, an OpenAI API key, and Arize Phoenix running locally.

```bash
# Clone the repo and install dependencies
git clone https://github.com/ehcastroh-teach/EDD_Agent_Evals.git
cd EDD_Agent_Evals
pip install -r requirements.txt

# Store your OpenAI API key in a .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Start Phoenix in a separate terminal before opening notebooks 02 or 03
phoenix serve
# Fallback if the CLI entrypoint is not available:
# python -m phoenix.server.main serve

# Launch Jupyter and open notebooks in order
jupyter notebook
```

Open `01_evaluating_agents.ipynb` first. Notebooks 02 and 03 require Phoenix running at `http://localhost:6006`. Run all cells in notebook 02 before starting notebook 03 to ensure spans are available for evaluation.

## Key Concepts Glossary

**Agent** - An LLM combined with a set of tools it can call to retrieve information or take actions, controlled by a loop that runs until the LLM decides it has a complete answer.

**Router** - The LLM call at the center of the agent loop that reads the conversation history and the available tool schemas, then decides which tool to call next or whether to return a final answer.

**Tool schema** - A JSON description of a Python function in the OpenAI function-calling format. It specifies the function name, a natural language description the router uses for selection, and the parameter types. The description field is the primary signal the router uses - imprecise descriptions cause wrong tool selections.

**Span** - A single unit of work recorded by OpenTelemetry: one LLM call, one tool invocation, or one pipeline step. Each span has a kind (LLM, tool, chain, agent), a start time, a duration, and input/output attributes.

**Trace** - The complete tree of spans generated by a single agent run. A trace shows the entire call sequence from the user's first message to the agent's final answer, with parent-child relationships preserved.

**Evaluation-Driven Development (EDD)** - A development practice for AI systems: instrument the system to collect structured data, evaluate that data with programmatic or LLM-based judges, identify failure patterns, and make one targeted change per improvement cycle. The key discipline is changing one thing at a time and re-running evals to verify the change had the expected effect.

**LLM-as-judge** - An evaluation technique that uses a separate LLM to score another LLM's output against a rubric. Used when correctness cannot be determined by a function - for example, assessing whether a response is clear or whether a SQL query correctly answers a question.

**Programmatic eval** - An evaluation that uses a deterministic function rather than an LLM judge. The code runnability eval (`exec()` with exception catching) is an example: it is faster, cheaper, and more consistent than asking an LLM whether code will run.

**SpanQuery** - A Phoenix API for retrieving stored spans as a dataframe, filtered by span kind and time range. It is the bridge between the trace store and the evaluation pipeline - it extracts the inputs and outputs that evaluators need without requiring manual export from the UI.

**Arize Phoenix** - An open-source LLM observability platform that collects OpenTelemetry spans, displays trace trees, and supports evaluation workflows including writing eval scores back alongside traces.

**OpenInference** - A set of semantic conventions for OpenTelemetry span attributes specific to LLM applications (span kinds: agent, chain, tool, LLM; attribute names for prompts, completions, token counts). Phoenix uses OpenInference to categorize and display spans correctly.

**Structured outputs** - An OpenAI API feature that constrains the LLM's response to match a JSON schema defined as a Pydantic model. Used in the visualization tool to reliably extract chart configuration before passing it to a code generation step - eliminates JSON parsing errors from free-form responses.

**Prompt improvement** - In EDD, a change to a prompt made in direct response to an observed failure mode in eval scores - not a general quality pass, but a targeted fix for a specific, measured problem. The improved SQL prompt in this series was written to address a specific hallucination failure identified by the SQL generation evaluator.

## Further Reading

- OpenAI Function Calling guide
- OpenAI Structured Outputs guide
- Arize Phoenix Tracing documentation
- OpenInference semantic conventions: span kinds reference (agent, chain, tool, LLM)
- OpenTelemetry concepts: traces, spans, and context propagation
- LLM-as-Judge: a survey of evaluation methods for language model outputs
- DuckDB documentation: in-process analytics on Parquet files

## Credits and Acknowledgements

Sales dataset: Store Sales Price Elasticity Promotions dataset (public domain retail transaction data).

---

## Contact

<div align="center">
  <img src="images/thumbnails/ehcastroh_teach_banner_flower.png" alt="ehcastroh" width="90" style="border-radius: 50%;" />

  <sub>ehcastroh</sub>

  <a href="https://github.com/ehcastroh">GitHub</a> · <a href="https://www.linkedin.com/in/ehcastroh/">LinkedIn</a>
</div>
