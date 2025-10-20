"use client";

import { useEffect, useState } from "react";
import { usePipecatEventStream } from "@pipecat-ai/voice-ui-kit";

export type R2C2Phase = "relationship" | "reaction" | "content" | "coaching";

interface PhaseTransitionEvent {
  from_phase: R2C2Phase;
  to_phase: R2C2Phase;
  timestamp: string;
  time_in_previous_phase: number;
}

interface R2C2PhaseState {
  currentPhase: R2C2Phase;
  phaseProgress: number;
  lastTransition: PhaseTransitionEvent | null;
  phaseStartTime: Date | null;
}

export const useR2C2PhaseEvents = () => {
  const { events } = usePipecatEventStream({
    maxEvents: 100,
    ignoreEvents: [],
  });
  
  const [phaseState, setPhaseState] = useState<R2C2PhaseState>({
    currentPhase: "relationship",
    phaseProgress: 0,
    lastTransition: null,
    phaseStartTime: new Date(),
  });

  // Listen for R2C2 phase transition events
  useEffect(() => {
    if (events.length === 0) return;

    // Get the most recent event
    const latestEvent = events[events.length - 1];
    
    try {
      // Check if this is an R2C2 phase transition event
      if (latestEvent.type === "r2c2-phase-transition" && latestEvent.data) {
        const transitionData = latestEvent.data as PhaseTransitionEvent;
        
        console.log("R2C2 Phase Transition:", transitionData);
        
        setPhaseState((prev) => ({
          ...prev,
          currentPhase: transitionData.to_phase,
          lastTransition: transitionData,
          phaseStartTime: new Date(),
          phaseProgress: 0, // Reset progress on phase change
        }));
      }
    } catch (error) {
      console.error("Error handling R2C2 phase event:", error);
    }
  }, [events]);

  // Calculate phase progress based on time
  useEffect(() => {
    if (!phaseState.phaseStartTime) return;

    const updateProgress = () => {
      const now = new Date();
      const elapsed = (now.getTime() - phaseState.phaseStartTime!.getTime()) / 1000;
      
      // Estimate progress based on typical phase durations
      const phaseDurations: Record<R2C2Phase, number> = {
        relationship: 120, // 2 minutes
        reaction: 180,     // 3 minutes
        content: 240,      // 4 minutes
        coaching: 300,     // 5 minutes
      };
      
      const expectedDuration = phaseDurations[phaseState.currentPhase];
      const progress = Math.min((elapsed / expectedDuration) * 100, 100);
      
      setPhaseState((prev) => ({
        ...prev,
        phaseProgress: progress,
      }));
    };

    // Update progress every second
    const interval = setInterval(updateProgress, 1000);
    updateProgress(); // Initial update

    return () => clearInterval(interval);
  }, [phaseState.currentPhase, phaseState.phaseStartTime]);

  return phaseState;
};
