"use client";

import React from "react";
import { Mic, MicOff, Video, VideoOff, MonitorUp, MonitorOff } from "lucide-react";
import { Button } from "./Button";

interface AudioControlsProps {
  isMicEnabled: boolean;
  isCamEnabled: boolean;
  isScreenShareEnabled: boolean;
  onToggleMic: () => void;
  onToggleCam: () => void;
  onToggleScreenShare: () => void;
  showVideo?: boolean;
  showScreenShare?: boolean;
}

export const AudioControls: React.FC<AudioControlsProps> = ({
  isMicEnabled,
  isCamEnabled,
  isScreenShareEnabled,
  onToggleMic,
  onToggleCam,
  onToggleScreenShare,
  showVideo = true,
  showScreenShare = true,
}) => {
  return (
    <div className="flex items-center gap-2">
      {/* Microphone Control */}
      <Button
        variant={isMicEnabled ? "primary" : "outline"}
        size="md"
        onClick={onToggleMic}
        title={isMicEnabled ? "Mute microphone" : "Unmute microphone"}
      >
        {isMicEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
      </Button>

      {/* Camera Control */}
      {showVideo && (
        <Button
          variant={isCamEnabled ? "primary" : "outline"}
          size="md"
          onClick={onToggleCam}
          title={isCamEnabled ? "Turn off camera" : "Turn on camera"}
        >
          {isCamEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
        </Button>
      )}

      {/* Screen Share Control */}
      {showScreenShare && (
        <Button
          variant={isScreenShareEnabled ? "primary" : "outline"}
          size="md"
          onClick={onToggleScreenShare}
          title={isScreenShareEnabled ? "Stop screen share" : "Start screen share"}
        >
          {isScreenShareEnabled ? <MonitorUp className="w-5 h-5" /> : <MonitorOff className="w-5 h-5" />}
        </Button>
      )}
    </div>
  );
};
