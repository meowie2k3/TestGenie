import { useState, useEffect } from "react";
import axios from "axios";
import { ReactFlow, Controls, Background } from "@xyflow/react";
import CustomNode from "../components/Block.js";
import { useSearchParams } from "react-router-dom";
import { fetchGraphData } from "../services/api";

export default function Graph() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [searchParams] = useSearchParams();
  const repo = searchParams.get("repo") || "";

  useEffect(() => {
    fetchGraphData(repo)
      .then(({ nodes, edges }) => {
        setNodes(
          nodes.map((node) => ({
            id: node.id,
            type: "custom",
            position: { x: Math.random() * 400, y: Math.random() * 400 },
            data: { label: node.label },
          }))
        );
        setEdges(
          edges.map((edge) => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
          }))
        );
      })
      .catch(console.error);
  }, [repo]);

  return (
    <div className="h-screen bg-gray-100">
      <ReactFlow nodes={nodes} edges={edges} nodeTypes={{ custom: CustomNode }}>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
