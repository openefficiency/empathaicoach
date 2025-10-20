"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import DailyIframe, { DailyCall, DailyEventObjectAppMessage } from "@daily-co/daily-js";

export type ConnectionState = "idle" | "connecting" | "connected" | "disconnected" | "error";

interface DailyClientConfig {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
  onAppMessage?: (event: DailyEventObjectAppMessage) => void;
}

export const useDailyClient = (config?: DailyClientConfig) => {
  const [connectionState, setConnectionState] = useState<ConnectionState>("idle");
  const [error, setError] = useState<Error | null>(null);
  const [isMicEnabled, setIsMicEnabled] = useState(true);
  const [isCamEnabled, setIsCamEnabled] = useState(false);
  const [isScreenShareEnabled, setIsScreenShareEnabled] = useState(false);
  
  const callObjectRef = useRef<DailyCall | null>(null);
  const roomUrlRef = useRef<string | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);

  // Initialize Daily call object and audio element
  useEffect(() => {
    if (!callObjectRef.current) {
      // Create audio element for playback
      if (!audioElementRef.current) {
        audioElementRef.current = document.createElement('audio');
        audioElementRef.current.autoplay = true;
        audioElementRef.current.playsInline = true;
        document.body.appendChild(audioElementRef.current);
        console.log("Audio element created and added to DOM");
      }

      callObjectRef.current = DailyIframe.createCallObject({
        audioSource: true,
        videoSource: false,
        subscribeToTracksAutomatically: true, // Subscribe to remote audio/video
      });
      
      console.log("Daily call object created with audio subscription enabled");
    }

    return () => {
      // Cleanup audio element on unmount
      if (audioElementRef.current && document.body.contains(audioElementRef.current)) {
        document.body.removeChild(audioElementRef.current);
        audioElementRef.current = null;
      }
    };
  }, []);

  // Set up event listeners
  useEffect(() => {
    const daily = callObjectRef.current;
    if (!daily) return;

    const handleJoinedMeeting = () => {
      console.log("Joined Daily meeting");
      setConnectionState("connected");
      config?.onConnect?.();
    };

    const handleLeftMeeting = () => {
      console.log("Left Daily meeting");
      setConnectionState("disconnected");
      config?.onDisconnect?.();
    };

    const handleError = (event: any) => {
      console.error("Daily error:", event);
      const err = new Error(event.errorMsg || "Daily connection error");
      setError(err);
      setConnectionState("error");
      config?.onError?.(err);
    };

    const handleAppMessage = (event: DailyEventObjectAppMessage) => {
      config?.onAppMessage?.(event);
    };

    const handleParticipantUpdated = (event: any) => {
      console.log("Participant updated:", event);
      // Log audio track status
      if (event.participant?.tracks?.audio) {
        console.log("Audio track state:", event.participant.tracks.audio.state);
      }
    };

    const handleTrackStarted = (event: any) => {
      console.log("Track started:", event);
      if (event.track?.kind === 'audio' && event.participant?.local === false) {
        console.log("Remote audio track started! Attaching to audio element...");
        
        // Attach the remote audio track to our audio element
        if (audioElementRef.current && event.track) {
          const stream = new MediaStream([event.track]);
          audioElementRef.current.srcObject = stream;
          audioElementRef.current.play().then(() => {
            console.log("✅ Audio playback started successfully!");
          }).catch((err) => {
            console.error("❌ Failed to play audio:", err);
            // Try to play with user interaction
            console.log("Audio playback may require user interaction. Click anywhere to enable audio.");
          });
        }
      }
    };

    daily.on("joined-meeting", handleJoinedMeeting);
    daily.on("left-meeting", handleLeftMeeting);
    daily.on("error", handleError);
    daily.on("app-message", handleAppMessage);
    daily.on("participant-updated", handleParticipantUpdated);
    daily.on("track-started", handleTrackStarted);

    return () => {
      daily.off("joined-meeting", handleJoinedMeeting);
      daily.off("left-meeting", handleLeftMeeting);
      daily.off("error", handleError);
      daily.off("app-message", handleAppMessage);
      daily.off("participant-updated", handleParticipantUpdated);
      daily.off("track-started", handleTrackStarted);
    };
  }, [config]);

  const connect = useCallback(async (roomUrl: string, token?: string) => {
    if (!callObjectRef.current) {
      throw new Error("Daily call object not initialized");
    }

    try {
      setConnectionState("connecting");
      setError(null);
      roomUrlRef.current = roomUrl;

      await callObjectRef.current.join({
        url: roomUrl,
        token,
      });
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to connect");
      setError(error);
      setConnectionState("error");
      config?.onError?.(error);
      throw error;
    }
  }, [config]);

  const disconnect = useCallback(async () => {
    if (!callObjectRef.current) return;

    try {
      await callObjectRef.current.leave();
      setConnectionState("disconnected");
    } catch (err) {
      console.error("Error disconnecting:", err);
    }
  }, []);

  const toggleMic = useCallback(async () => {
    if (!callObjectRef.current) return;

    try {
      const newState = !isMicEnabled;
      await callObjectRef.current.setLocalAudio(newState);
      setIsMicEnabled(newState);
    } catch (err) {
      console.error("Error toggling microphone:", err);
    }
  }, [isMicEnabled]);

  const toggleCam = useCallback(async () => {
    if (!callObjectRef.current) return;

    try {
      const newState = !isCamEnabled;
      await callObjectRef.current.setLocalVideo(newState);
      setIsCamEnabled(newState);
    } catch (err) {
      console.error("Error toggling camera:", err);
    }
  }, [isCamEnabled]);

  const startScreenShare = useCallback(async () => {
    if (!callObjectRef.current) return;

    try {
      await callObjectRef.current.startScreenShare();
      setIsScreenShareEnabled(true);
    } catch (err) {
      console.error("Error starting screen share:", err);
    }
  }, []);

  const stopScreenShare = useCallback(async () => {
    if (!callObjectRef.current) return;

    try {
      await callObjectRef.current.stopScreenShare();
      setIsScreenShareEnabled(false);
    } catch (err) {
      console.error("Error stopping screen share:", err);
    }
  }, []);

  const sendAppMessage = useCallback((data: any, to?: string) => {
    if (!callObjectRef.current) return;

    try {
      callObjectRef.current.sendAppMessage(data, to);
    } catch (err) {
      console.error("Error sending app message:", err);
    }
  }, []);

  return {
    callObject: callObjectRef.current,
    connectionState,
    isConnected: connectionState === "connected",
    isConnecting: connectionState === "connecting",
    isDisconnected: connectionState === "disconnected" || connectionState === "idle",
    error,
    isMicEnabled,
    isCamEnabled,
    isScreenShareEnabled,
    connect,
    disconnect,
    toggleMic,
    toggleCam,
    startScreenShare,
    stopScreenShare,
    sendAppMessage,
  };
};
