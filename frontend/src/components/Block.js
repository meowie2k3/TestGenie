import { Handle, Position } from "@xyflow/react";

export default function CustomNode({ data }) {
  return (
    <div className="p-4 bg-white border shadow rounded">
      <strong>{data.label}</strong>
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}