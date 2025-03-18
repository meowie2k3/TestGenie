import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./Home.css"; // Import the CSS file

export default function Home() {
  const navigate = useNavigate();
  const [repoLink, setRepoLink] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (repoLink.trim()) {
      navigate(`/diagram`);
    }
  };

  return (
    <motion.div
      className="home-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      style={{ pointerEvents: "auto" }} // Ensure clicks are allowed
    >
      <div className="home-bg-glow"></div>

      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="home-title"
      >
        Test Genie
      </motion.h1>

      <motion.form
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 1 }}
        onSubmit={handleSubmit}
        className="home-form"
        style={{ pointerEvents: "auto" }} // Explicitly set interaction
      >
        <input
          type="text"
          placeholder="Enter GitHub Repo Link..."
          value={repoLink}
          onChange={(e) => setRepoLink(e.target.value)}
          className="home-input"
        />
        <button type="submit" className="home-button">
          ➜
        </button>
      </motion.form>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
        className="home-subtext"
      >
        We analyze your code structure and visualize it instantly.
      </motion.p>
    </motion.div>
  );
}
