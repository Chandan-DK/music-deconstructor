import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import HistoryPage from "./HistoryPage"; // Import History Page

function HomePage() {
  const [url, setUrl] = useState("");
  const [stems, setStems] = useState({});
  const navigate = useNavigate(); // Navigation hook

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(JSON.stringify({ url }));

    const response = await fetch("http://127.0.0.1:8000/extract-stems/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();
    console.log("Backend Response:", data);

    setStems(data.stems);
  };

  return (
    <div>
      <h1>Music Stems Extractor</h1>
      <button onClick={() => navigate("/history")}>History</button> {/* History Button */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter YouTube link"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit">Extract Stems</button>
      </form>

      <h2>Extracted Stems</h2>
      {Object.entries(stems).map(([stemName, stemUrl], index) => (
        <div key={index}>
          {stemName} <audio controls src={stemUrl}></audio>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </Router>
  );
}
