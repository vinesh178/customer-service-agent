import { useParticipants, useIsSpeaking } from '@livekit/components-react';
import '../styles/SpeakingIndicator.css';

function ParticipantItem({ participant }: { participant: any }) {
  // Use the dedicated useIsSpeaking hook from LiveKit
  const isSpeaking = useIsSpeaking(participant);
  
  return (
    <div 
      className={`participant-item ${isSpeaking ? 'speaking' : 'listening'}`}
    >
      <div className="status-indicator"></div>
      <span className="participant-name">
        {participant.name || participant.identity}
        {participant.isLocal && ' (You)'}
      </span>
      <span className="status-text">
        {isSpeaking ? 'Speaking' : 'Listening'}
      </span>
    </div>
  );
}

export function SpeakingIndicator() {
  const participants = useParticipants();
  
  return (
    <div className="speaking-indicator-container">
      <h3>Participants</h3>
      <div className="participants-list">
        {participants.map(participant => (
          <ParticipantItem 
            key={participant.identity} 
            participant={participant} 
          />
        ))}
      </div>
    </div>
  );
}