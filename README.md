# TestGenie

TestGenie is an intelligent testing automation tool designed for Flutter (Dart) projects. It generates unit test and integration test files based on the business logic of your project. With TestGenie, you can automate and streamline the testing process with minimal effort.

---

## Key Features

- **Automated Analysis**: Analyzes the business logic of your Flutter codebase by understanding function relationships, naming conventions, and comments within the code.
- **User Validation**: Provides a summarized understanding of the business rules for user confirmation and adjustment.
- **Test File Generation**: Creates runnable unit and integration test files without depending on the internal logic of functions, ensuring unbiased and reusable tests.
- **Embedded Testing Environment**: Runs the generated test files using an embedded Flutter SDK to verify their validity.

---

## Workflow

### 1. Input
Provide the source code of your Flutter project along with specific testing requirements. For example:
- Specify which parts of the project need testing.
- Highlight key functionalities to focus on during the test generation process.

### 2. Business Logic Analysis
TestGenie uses advanced language models to analyze the business logic:
- **Function Analysis**: Identifies relationships and interactions between functions.
- **Comment Parsing**: Leverages comments in the code to understand intended functionality.
- **Logic Extraction**: Derives business rules and operational logic based on the analyzed information.

### 3. User Validation
Before proceeding with test generation, TestGenie:
- Summarizes the analyzed business logic.
- Requests user confirmation or adjustments to ensure accuracy.
- Refines the logic based on user input.

### 4. Test File Generation
TestGenie generates test files by:
- Mapping business logic to relevant test cases.
- Using function names and logic relationships to create robust test scenarios.
- Avoiding reliance on internal function implementations to prevent biases.
- Combining Retrieval-Augmented Generation (RAG) techniques for advanced test methodologies.

### 5. Test Execution
- The generated test files are executed using an embedded Flutter SDK.
- Ensures the test files are runnable without focusing on the test outcomes.

---

## Prerequisites

To use TestGenie, ensure the following:
- Flutter SDK is installed and accessible.
- Your project follows standard Flutter/Dart conventions.
- Sufficient comments and clear function names in the codebase for effective analysis.

---

## Usage

1. **Provide Input**:
   - Upload the source code of your Flutter project.
   - Specify the testing requirements.

2. **Review Analyzed Logic**:
   - Confirm or modify the business rules derived by TestGenie.

3. **Generate Tests**:
   - Allow TestGenie to create unit and integration test files.

4. **Run Tests**:
   - TestGenie automatically executes the test files using the embedded Flutter SDK.

---

## Limitations

- TestGenie does not analyze internal function implementations to avoid biases.
- The quality of test generation is influenced by the clarity of function names and code comments.
- TestGenie focuses on generating runnable tests, not their outcomes or debugging.

---

## Feedback and Support

We value your feedback! If you encounter issues or have suggestions for improvement, please contact our support team or open an issue in our repository.

---

## License

TestGenie is licensed under [MIT License](LICENSE).

---

## Contribution

Contributions are welcome! Feel free to fork this repository, create a branch, and submit a pull request. For major changes, please discuss them with the project maintainers first.

---

Thank you for using TestGenie! Happy testing!
