import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import Graph from "react-graph-vis";
import Node from "./components/Node/Node.js";
import Edge from "./components/Edge/Edge.js";
import { fetchDiagramData } from "../../services/DiagramService";
import "./Diagram.css";

const Diagram = () => {

  var runOnce = false;
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const gitUrl = queryParams.get("git_url"); // Extract git_url
  console.log(gitUrl);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  const handleGraphDataMap = (graphData) => {
    /*
    graphData = {
      "project": "sample"
      "blocks": [
        {
            "id": 32,
            "name": "lib/main.dart",
            "type": "File"
        },
        {
            "id": 33,
            "name": "lib/widgets/app.dart",
            "type": "File"
        },
      ]
      "connections": [
        {
            "head": 32,
            "tail": 33,
            "type": "Import"
        },
        {
            "head": 33,
            "tail": 34,
            "type": "Import"
        },
      ]
    }
    */
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
    // dummy data first
    // const nodes = [
    //   { id: 32, label: "Node 1", color: "#e04141" },
    //   { id: 33, label: "Node 2", color: "#e09c41" }
    // ];
    // const edges = [
    //   { from: 32, to: 33 },
    // ];
    const nodes = graphData.blocks.map((block) => {
      return new Node(block.id, block.name, block.type).toGraphNode();
    });
    const edges = graphData.connections.map((connection) => {
      return new Edge(connection.head, connection.tail, connection.type).toGraphEdge();
    });
    
    setGraphData({
      nodes: nodes,
      edges: edges,
    });
  };

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
    <div className="graph-container">
      <Graph 
        graph={graphData} 
        options={options} 
        style={{ width: "100vw", height: "100vh" }} />
    </div>
  );
};

export default Diagram;