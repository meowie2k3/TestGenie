import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [repoLink, setRepoLink] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (repoLink.trim()) {
      navigate(`/graph?repo=${encodeURIComponent(repoLink)}`);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-2xl font-bold mb-4">Enter GitHub Repo Link</h1>
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          placeholder="https://github.com/user/repo"
          value={repoLink}
          onChange={(e) => setRepoLink(e.target.value)}
          className="p-2 border rounded w-80"
        />
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Visualize
        </button>
      </form>
    </div>
  );
}
