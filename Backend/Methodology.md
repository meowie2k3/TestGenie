# Input
Input will be project's source code (Flutter - Dart) and user test request (e.g which part to be tested)
# Output
Unit test file, integration test file 
# Process
### Step 1: Analyze the business logic using the source code 
Using connection between functions, function names and comment inside the code(if given)
=> Using a separate LLM model to analyze
### Step 2: Confirm to user the business rules analyzed
Let user justify the analyzed logic
=> adjustable
### Step 3: Generate test file
NOTE: Do not based on the source inside functions (avoid biases)
Use business logic and function names to call in the test file.
=> use a special model for flutter testfile generation.
Combine RAG to add information to FLUTTER model. Flutter model will communicate with
LLM model to find more testing technique.
## Step 4: Run a embeded flutter SDK to run test files.
Ensure test files are runnables. Dont need to care whats the result.