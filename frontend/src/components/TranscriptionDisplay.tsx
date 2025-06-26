import { useEffect, useMemo, useState } from 'react';
import { Participant, RoomEvent, TranscriptionSegment, TrackPublication } from 'livekit-client';
import { useConnectionState, useMaybeRoomContext } from '@livekit/components-react';

export function useTranscriber() {
  const state = useConnectionState();
  const room = useMaybeRoomContext();
  const [transcriptions, setTranscriptions] = useState<{
    [id: string]: {
      segment: TranscriptionSegment;
      participantName?: string;
    };
  }>({});

  useEffect(() => {
    if (!room) return;

    const updateTranscriptions = (
      segments: TranscriptionSegment[],
      participant?: Participant,
      publication?: TrackPublication
    ) => {
      console.log('Received transcription:', segments, 'from participant:', participant?.name);
      setTranscriptions((prev) => {
        const newTranscriptions = { ...prev };
        for (const segment of segments) {
          newTranscriptions[segment.id] = {
            segment,
            participantName: participant?.name || participant?.identity,
          };
        }
        return newTranscriptions;
      });
    };

    room.on(RoomEvent.TranscriptionReceived, updateTranscriptions);
    return () => {
      room.off(RoomEvent.TranscriptionReceived, updateTranscriptions);
    };
  }, [room, state]);

  return { state, transcriptions };
}

export function TranscriptionDisplay() {
  const { transcriptions } = useTranscriber();
  
  const transcriptionSegments = useMemo(() => 
    Object.values(transcriptions)
      .sort((a, b) => a.segment.firstReceivedTime - b.segment.firstReceivedTime),
    [transcriptions]
  );
  
  if (transcriptionSegments.length === 0) {
    return (
      <div className="transcription-container">
        <h3>Live Transcription</h3>
        <p className="no-transcription">No transcription available yet...</p>
      </div>
    );
  }

  return (
    <div className="transcription-container">
      <h3>Live Transcription</h3>
      <div className="transcription-segments">
        {transcriptionSegments.map((item) => (
          <div key={item.segment.id} className="transcription-segment">
            <span className="speaker">{item.participantName || 'Unknown'}: </span>
            <span className="text">{item.segment.text}</span>
            {!item.segment.final && <span className="interim"> ...</span>}
          </div>
        ))}
      </div>
    </div>
  );
}