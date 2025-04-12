import { useEffect, useRef, useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism"; // Using a close match to Catppuccin Latte
// import { ClipboardCopy } from 'lucide-react';

const SidePanel = ({ selectedNode, setSelectedNode, onSavePrediction, handleGenerateTest }) => {
  const [editedPrediction, setEditedPrediction] = useState(selectedNode?.prediction || "");
  const textareaRef = useRef(null);

  const [isGeneratingTest, setIsGeneratingTest] = useState(false);

  useEffect(() => {
    if (selectedNode) {
      setEditedPrediction(selectedNode.prediction || "");
      // Auto-resize on initial render
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.style.height = "auto";
          textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
      }, 0);
    }
  }, [selectedNode]);

  // Handle prediction save
  const handleSave = () => {
    onSavePrediction(selectedNode.id, editedPrediction);
  };

  const handleClickGenerateTest = () => {
    // change state to loading
    setIsGeneratingTest(true);
    handleGenerateTest(selectedNode.id)
      .then(() => {
        // After generating test, set state back to false
        setIsGeneratingTest(false);
      })
      .catch((error) => {
        console.error("Error generating test:", error);
        setIsGeneratingTest(false);
      });
  }

  return (
    <div className={`side-panel ${selectedNode ? "visible" : ""}`}>
      {selectedNode ? (
        <>
          <div className="panel-header">
            <h2>{selectedNode.name}</h2>
            <button className="close-btn" onClick={() => setSelectedNode(null)}>✖</button>
          </div>

          <div className="panel-content">
            <p><strong>ID:</strong> {selectedNode.id}</p>
            <p><strong>Type:</strong> {selectedNode.type}</p>

            {/* Code Viewer */}
            <div className="code-container">
              <p><strong>Source code:</strong></p>
              <SyntaxHighlighter language="javascript" style={vscDarkPlus}>
                {selectedNode.content}
              </SyntaxHighlighter>
            </div>

            {/* Editable Prediction Box */}
            <div className="prediction-container">
              <p><strong>Prediction:</strong></p>
              <textarea
                ref={textareaRef}
                value={editedPrediction}
                onChange={(e) => {
                  setEditedPrediction(e.target.value);
                  e.target.style.height = "auto";
                  e.target.style.height = `${e.target.scrollHeight}px`;
                }}
                className="prediction-box auto-resize"
              />
              <button className="save-btn" onClick={handleSave}>Save</button>
            </div>

            {/* test code viewer, with copy button on top right of code viewer */}
            <div className="test-code-container">
              <div className="flex justify-between items-center">
                <p><strong>Test Content</strong></p>
                <button className="generate-btn" onClick={handleClickGenerateTest}>
                  Generate Test
                </button>
              </div>
              {isGeneratingTest ? (
                <div className="loading-spinner-container">
                  <div className="spinner"></div>
                  <p>Generating test...</p>
                </div>
              ) : (
                selectedNode.test_file_content ? (
                  <div className="test-code relative">
                    {/* Copy Button */}
                    <button
                      className="copy-btn"
                      onClick={() =>
                        navigator.clipboard.writeText(selectedNode.test_file_content)
                      }
                      title="Copy to clipboard"
                    >
                      📋
                    </button>

                    <SyntaxHighlighter language="javascript" style={vscDarkPlus}>
                      {selectedNode.test_file_content}
                    </SyntaxHighlighter>
                  </div>
                ) : (
                  <p>This block has not generated tests yet</p>
                )
              )}
            </div>
          </div>
        </>
      ) : (
        null
      )}
    </div>
  );
};

export default SidePanel;
