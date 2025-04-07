import { useEffect, useRef, useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism"; // Using a close match to Catppuccin Latte

const SidePanel = ({ selectedNode, setSelectedNode, onSavePrediction }) => {
  const [editedPrediction, setEditedPrediction] = useState(selectedNode?.prediction || "");
  const textareaRef = useRef(null);

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
          </div>
        </>
      ) : (
        <p>Select a block to view details</p>
      )}
    </div>
  );
};
export default SidePanel;
