import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import Graph from "react-graph-vis";
import Node from "./components/Node/Node.js";
import Edge from "./components/Edge/Edge.js";
import { fetchDiagramData, fetchBlockDetails, savePrediction } from "../../services/DiagramService";
import SidePanel from "./components/Side-panel/SidePanel.js";
import "./Diagram.css";

const Diagram = () => {

  var runOnce = false;
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const gitUrl = queryParams.get("git_url"); // Extract git_url
  // console.log(gitUrl);
  
  const [nodeData, setNodeData] = useState([]);
  const [edgeData, setEdgeData] = useState([]);

  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedNode, setSelectedNode] = useState(null); // New state for side panel

  useEffect(() => {
    if (gitUrl) {
      fetchDiagramData(gitUrl)
        .then((response) => {
          // console.log(response);
          if (response && runOnce === false) {
            runOnce = true;
            handleGraphDataMap(response);
            // setGraphData(graphDataMap);
          }
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [gitUrl]);

  const handleNodeClick = (event) => {
    const nodeId = event.nodes[0]; // Get clicked node ID
    if (!nodeId) return;

    const clickedNode = nodeData.find((node) => node.id === nodeId);
    if (!clickedNode) return;

    // Fetch block details using the clicked node ID
    setSelectedNode(null); // Reset selected node
    fetchBlockDetails(gitUrl, clickedNode.id)
      .then((response) => {
        if (response) {
          // Update the selected node with details
          console.log(response);
          const updatedNode = {
            ...clickedNode,
            id: clickedNode.id,
            content: response.content || "No content available", // Fallback if content is not available
            prediction: response.prediction || "No prediction available", // Fallback if prediction is not available
          };
          setSelectedNode(updatedNode);
        }
      })
      .catch((err) => setError(err.message));
    
  };

  const handleSavePrediction = async (nodeId, newPrediction) => {
    try {
      // TODO: Implement the save logic
      const response = await savePrediction(gitUrl, nodeId, newPrediction);
      console.log(response);
      if (response && response.success) {
        alert("Prediction updated successfully!");
      }
      else
        alert("Failed to update prediction.");
    } catch (error) {
      console.error("Failed to save prediction:", error);
    }
  };

  const handleGraphDataMap = (graphData) => {

    // check for duplicate ids
    const idSet = new Set();
    for (const block of graphData.blocks) {
      if (idSet.has(block.id)) {
        console.error(`Duplicate id found: ${block.id}`);
      }
      idSet.add(block.id);
    }
    for (const connection of graphData.connections) {
      if (!idSet.has(connection.head)) {
        console.error(`Invalid head id found: ${connection.head}`);
      }
      if (!idSet.has(connection.tail)) {
        console.error(`Invalid tail id found: ${connection.tail}`);
      }
    }
    console.log(graphData);
    var nodes = [];
    var edges = [];
    // create nodes
    for (const block of graphData.blocks) {
      const node = new Node(block.id, block.name, block.type);
      nodes.push(node);
    }
    // create edges
    for (const connection of graphData.connections) {
      const edge = new Edge(
        connection.head,
        connection.tail,
        connection.type,
      );
      edges.push(edge);
    }

    // console.log("nodes", nodes);
    // console.log("edges", edges);

    setNodeData([...nodes]);
    setEdgeData([...edges]);

    const graphDataMap = {
      nodes: nodes.map((node) => node.toGraphNode()),
      edges: edges.map((edge) => edge.toGraphEdge()),
    };
    setGraphData(graphDataMap);
    
  };

  // render section

  const options = {
    layout: {
      hierarchical: false, // Keep it false for a free-flow layout
    },
    edges: {
      smooth: {
        type: "curvedCW", // Enable curved edges
        roundness: 0.2,   // Adjust curve roundness
      },
      arrows: { to: { enabled: true } }, // Enable directional arrows
      color: "#848484", // Edge color
    },
    nodes: {
      shape: "box", // Better block visibility
      margin: 10, // Add spacing
    },
    physics: {
      enabled: true,
      barnesHut: {
        gravitationalConstant: -3000, // Spread nodes out
        centralGravity: 0.1, // Keep some clustering
        springLength: 200, // Increase spacing
        springConstant: 0.0, // Softer pull
      },
    },
    interaction: {
      dragNodes: true, // Allow users to adjust node positions
      zoomView: true, // Enable zooming
    },
  };
  
  if (loading) return <div className="loading">Loading diagram...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="diagram-container">
      {/* Graph Section */}
      <div className="graph-section">
        <Graph
          graph={graphData}
          options={options}
          events={{ selectNode: handleNodeClick }}
          style={{ width: "75vw", height: "100vh" }}
        />
      </div>

      {/* Side Panel for Block Details */}
      <SidePanel 
        selectedNode={selectedNode} 
        setSelectedNode={setSelectedNode} 
        onSavePrediction={handleSavePrediction} 
      />
    </div>
  );
};

export default Diagram;