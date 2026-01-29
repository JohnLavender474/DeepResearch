# Sequential Task Decomposition

You are tasked with breaking down a user's query into
3-5 sequential sub-tasks that build on each other.

## Instructions

Given the following user query, generate a list of
3-5 distinct sub-tasks that must be solved
sequentially, where each task depends on or builds
upon the results of the previous task(s).

Each sub-task should be:
- Specific and actionable
- Ordered logically so later tasks depend on earlier results
- Designed to gather information or insights that inform subsequent tasks
- Progress toward a comprehensive answer

The tasks should form a logical chain where:
1. Early tasks provide foundational information
2. Mid-level tasks build on that foundation
3. Later tasks synthesize or refine earlier findings

Return the sub-tasks as a numbered list with clear
descriptions that reflect their sequential nature.

# Input Data

Use the input data provided below to inform your 
decomposition process.

```json
{input_data}
```
