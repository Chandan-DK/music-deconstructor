import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "./components/ui/card";
import { Button } from "./components/ui/button";

export default function HistoryPage() {
  const [songs, setSongs] = useState([]);
  const [expandedSong, setExpandedSong] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://127.0.0.1:8000/history") // Fetch all songs from backend
      .then((res) => res.json())
      .then((data) => setSongs(data))
      .catch((err) => console.error("Error fetching history:", err));
  }, []);

  const handleExpand = (songTitle) => {
    setExpandedSong(expandedSong === songTitle ? null : songTitle);
  };

  return (
    <div className="p-4">
      <Button onClick={() => navigate("/")}>Home</Button>
      <h1 className="text-xl font-bold my-4">History</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {songs.map((song, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div
                className="cursor-pointer text-lg font-semibold"
                onClick={() => handleExpand(song.title)}
              >
                {song.title}
              </div>
              {expandedSong === song.title && (
                <div className="mt-2 space-y-2">
                  <h2 className="text-md font-bold">Extracted Stems</h2>
                  {Object.entries(song.stems).map(([stemName, stemUrl], idx) => (
                    <div key={idx}>
                      {stemName} <audio controls src={stemUrl}></audio>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
