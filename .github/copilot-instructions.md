# Code Generation Guidelines

## Code Style & Documentation

- **No inline comments**: Do not include inline comments explaining code logic within functions, classes, or methods.
- **No function/class documentation**: Do not add docstrings, JavaDoc, or similar documentation blocks to functions or classes unless explicitly requested.
- **Consistent formatting**: Ensure the generated code adheres to standard formatting conventions for the target programming language (e.g., indentation, spacing). There should be two lines instead of one to separate different blocks (between the "import" section and the start of the class, between methods, etc.).
- **Prefer Strong Typing**: Use strong typing conventions available in the programming language (e.g., type hints in Python, TypeScript types).
- **Wrap long lines**: Ensure that lines do not exceed 80 characters in length for better readability.
- **Define each field on its own line**: When defining or instantiating data structures (like classes or interfaces), place each field on a separate line.
- **Do not make config values as hardcoded or default parameters**: Avoid hardcoding configuration values or using them as default parameters in functions or classes. 
- **Define data classes in separate files**: When creating data classes, models, or schemas, place them in their own dedicated files rather than embedding them within other modules.
- **Organize imports**: Group and order imports logically (e.g., standard libraries first, followed by third-party libraries, then local modules). Make sure there is a newline between each group. Do not add inline import statements within functions or methods unless absolutely necessary.
- **Named arguments**: Use named arguments when calling functions or methods for better readability. Put each named argument on its own line if there are multiple arguments.

## Scope & Completeness

- **Implement only what is requested**: Generate code that directly addresses the user's request without adding extra features or enhancements not mentioned.
- **Use TODO stubs for gaps**: If the user's request results in incomplete code or missing implementations, mark these with concise `TODO` comments indicating what needs to be filled in later.
