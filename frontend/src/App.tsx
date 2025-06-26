import { useState, useEffect } from 'react';
import { LiveKitRoom, AudioConference } from '@livekit/components-react';
import '@livekit/components-styles';
import './App.css';
import { TranscriptionDisplay } from './components/TranscriptionDisplay';
import { SpeakingIndicator } from './components/SpeakingIndicator';
import './styles/Transcription.css';
import './styles/SpeakingIndicator.css';

interface Room {
  name: string;
  num_participants: number;
  creation_time: number;
}

function App() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<string>('');
  const [token, setToken] = useState<string>('');
  const [url, setUrl] = useState<string>('');
  const [participantName, setParticipantName] = useState<string>('');
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch active customer service rooms
  useEffect(() => {
    fetchRooms();
    const interval = setInterval(fetchRooms, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/rooms');
      const data = await response.json();
      setRooms(data);
    } catch (e) {
      console.error('Failed to fetch rooms:', e);
    }
  };

  const joinRoom = async () => {
    if (!selectedRoom || !participantName) {
      alert('Please select a room and enter your name');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/join-token?room_name=${encodeURIComponent(selectedRoom)}&participant_name=${encodeURIComponent(participantName)}`
      );
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get token');
      }

      const data = await response.json();
      setToken(data.token);
      setUrl(data.url);
      setConnected(true);
    } catch (e) {
      console.error(e);
      alert(`Failed to join room: ${e instanceof Error ? e.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const disconnect = () => {
    setConnected(false);
    setToken('');
    setSelectedRoom('');
  };

  const onConnected = () => {
    console.log('Connected to room');
  };

  const onDisconnected = () => {
    setConnected(false);
    setToken('');
    console.log('Disconnected from room');
  };

  const onError = (error: Error) => {
    console.error('Room error:', error);
    alert(`Connection error: ${error.message}`);
  };

  const formatRoomName = (name: string) => {
    if (name.startsWith('inbound')) {
      return `📞 Inbound Call - ${name}`;
    } else if (name.startsWith('outbound')) {
      return `📱 Outbound Call - ${name}`;
    }
    return name;
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <div className="container" data-lk-theme="default">
      <h1>Customer Service Call Monitor</h1>
      
      {!connected ? (
        <div className="card">
          <h2>Join Active Call</h2>
          
          <div className="form-group">
            <label htmlFor="participant">Your Name:</label>
            <input
              id="participant"
              type="text"
              value={participantName}
              onChange={(e) => setParticipantName(e.target.value)}
              placeholder="Enter your name (e.g., Supervisor)"
            />
          </div>

          <div className="form-group">
            <label htmlFor="room">Active Calls:</label>
            {rooms.length === 0 ? (
              <p className="no-rooms">No active customer service calls</p>
            ) : (
              <select
                id="room"
                value={selectedRoom}
                onChange={(e) => setSelectedRoom(e.target.value)}
              >
                <option value="">Select a call to join...</option>
                {rooms.map((room) => (
                  <option key={room.name} value={room.name}>
                    {formatRoomName(room.name)} - {room.num_participants} participants - Started {formatTime(room.creation_time)}
                  </option>
                ))}
              </select>
            )}
          </div>

          <button 
            onClick={joinRoom} 
            disabled={!selectedRoom || !participantName || loading}
          >
            {loading ? 'Joining...' : 'Join Call'}
          </button>

          <button onClick={fetchRooms} className="refresh-btn">
            Refresh Calls
          </button>
        </div>
      ) : (
        <>
          <div className="call-header">
            <h2>Monitoring: {formatRoomName(selectedRoom)}</h2>
            <button onClick={disconnect} className="disconnect-btn">
              Leave Call
            </button>
          </div>
          
          <LiveKitRoom
            serverUrl={url}
            token={token}
            connect={true}
            onConnected={onConnected}
            onDisconnected={onDisconnected}
            onError={onError}
          >
            <AudioConference />
            <SpeakingIndicator />
            <TranscriptionDisplay />
          </LiveKitRoom>
        </>
      )}
    </div>
  );
}

export default App;
