# Agent Samples

Ready-to-use Kiro agent configurations and prompt templates for each SDLC phase. Copy these into your project's `.kiro/agents/` directory and the prompts into your preferred location.

## Agents

| Agent | Description |
|-------|-------------|
| `plan` | Creates implementation plans from issue descriptions with codebase research |
| `build` | Executes implementation plans with precision — reads, writes, and validates code |
| `test` | Runs validation test suites and reports structured results |
| `review` | Reviews implementations against specifications, classifies issues by severity |
| `document` | Generates documentation from code changes and specifications |
| `deploy` | Handles git operations — commits, pushes, and creates pull requests |

## Usage

```bash
# Copy an agent to your project
cp agents/build.json /path/to/your-project/.kiro/agents/

# Or copy all agents
cp agents/*.json /path/to/your-project/.kiro/agents/
```

Each agent references a prompt file via `file://` URI. Update the path in the agent's `prompt` field to match where you place the prompt files.

## Prompts

Prompt templates live in `prompts/` as markdown files. Each corresponds to an agent and defines the phase-specific instructions, constraints, and output format.
