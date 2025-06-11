class Edge {
    constructor(headId, tailId, type) {
      this.headId = headId; // Source node
      this.tailId = tailId; // Target node
      this.type = type; // Edge type (e.g., "call", "inheritance", "dependency")
    }
  
    toGraphEdge() {
      return {
        from: this.headId,
        to: this.tailId,
        color: this.getEdgeColor(),
        arrows: "to", // Default arrow style
        dashes: this.isDashed(), // Dashed for dependency edges
      };
    }
  
    getEdgeColor() {
      const typeColors = {
        Call: "#FF0000", // Orange
        Contain: "#33FF57", // Green
        Extend: "#3357FF", // Blue
        Implement: "#FF33F9", // Purple
        Import: "#FF5733", // Orange
        Use: "#33FF57", // Green
        default: "#D3D3D3", // Light gray
      };
      return typeColors[this.type] || typeColors.default;
    }
  
    isDashed() {
      return this.type === "Extend" || this.type === 'Implement'; // Only dependency edges are dashed
    }
  }
  
  export default Edge;