class Node {
    constructor(id, name, type) {
      this.id = id;
      this.name = name;
      this.type = type;
    }
  
    toGraphNode() {
      return {
        id: this.id,
        label: `${this.name}\n(${this.type})`,
        shape: "box", // You can customize the shape
        color: this.getNodeColor(),
      };
    }
  
    getNodeColor() {
      const typeColors = {
        File: "#FFD7E1",
        Class: "#FBF3C3",
        ClassAttribute: "#FF7777",
        ClassConstructor: "#FFC0CB",
        ClassFunction: "#FFB347",
        Enum: "#FFD700",
        Function: "#FFA07A",
        GlobalVariable: "#FFD700",
        default: "#D3D3D3",
      };
      return typeColors[this.type] || typeColors.default;
    }
  }
  
  export default Node;