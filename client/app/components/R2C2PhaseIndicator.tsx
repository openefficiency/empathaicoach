"use client";

import React from "react";
import { Card, CardContent } from "@pipecat-ai/voice-ui-kit";
import { Heart, MessageCircle, BookOpen, Target } from "lucide-react";

export type R2C2Phase = "relationship" | "reaction" | "content" | "coaching";

interface R2C2PhaseIndicatorProps {
  currentPhase: R2C2Phase;
  phaseProgress?: number; // 0-100
  showDescription?: boolean;
}

interface PhaseConfig {
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  borderColor: string;
}

const PHASE_CONFIGS: Record<R2C2Phase, PhaseConfig> = {
  relationship: {
    name: "Relationship Building",
    description: "Creating a safe space and building rapport",
    icon: <Heart className="w-5 h-5" />,
    color: "text-blue-600 dark:text-blue-400",
    bgColor: "bg-blue-50 dark:bg-blue-900/20",
    borderColor: "border-blue-200 dark:border-blue-800",
  },
  reaction: {
    name: "Reaction Exploration",
    description: "Processing emotional responses to feedback",
    icon: <MessageCircle className="w-5 h-5" />,
    color: "text-purple-600 dark:text-purple-400",
    bgColor: "bg-purple-50 dark:bg-purple-900/20",
    borderColor: "border-purple-200 dark:border-purple-800",
  },
  content: {
    name: "Content Discussion",
    description: "Understanding feedback themes and patterns",
    icon: <BookOpen className="w-5 h-5" />,
    color: "text-amber-600 dark:text-amber-400",
    bgColor: "bg-amber-50 dark:bg-amber-900/20",
    borderColor: "border-amber-200 dark:border-amber-800",
  },
  coaching: {
    name: "Coaching for Change",
    description: "Creating actionable development plans",
    icon: <Target className="w-5 h-5" />,
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-50 dark:bg-green-900/20",
    borderColor: "border-green-200 dark:border-green-800",
  },
};

export const R2C2PhaseIndicator: React.FC<R2C2PhaseIndicatorProps> = ({
  currentPhase,
  phaseProgress = 0,
  showDescription = true,
}) => {
  const [isTransitioning, setIsTransitioning] = React.useState(false);
  const prevPhaseRef = React.useRef<R2C2Phase>(currentPhase);

  // Detect phase changes and trigger animation
  React.useEffect(() => {
    if (prevPhaseRef.current !== currentPhase) {
      setIsTransitioning(true);
      const timer = setTimeout(() => {
        setIsTransitioning(false);
      }, 500);
      prevPhaseRef.current = currentPhase;
      return () => clearTimeout(timer);
    }
  }, [currentPhase]);

  const config = PHASE_CONFIGS[currentPhase];
  const phases: R2C2Phase[] = ["relationship", "reaction", "content", "coaching"];
  const currentPhaseIndex = phases.indexOf(currentPhase);

  return (
    <Card 
      className={`${config.borderColor} border-2 transition-all duration-500 ${
        isTransitioning ? 'scale-105 shadow-lg' : 'scale-100'
      }`}
    >
      <CardContent className={`${config.bgColor} pt-4 pb-4`}>
        <div className="space-y-3">
          {/* Current Phase Header */}
          <div className="flex items-center gap-3">
            <div className={`${config.color} flex-shrink-0`}>
              {config.icon}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className={`text-lg font-semibold ${config.color}`}>
                {config.name}
              </h3>
              {showDescription && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                  {config.description}
                </p>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          {phaseProgress > 0 && (
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full ${config.color.replace('text-', 'bg-')} transition-all duration-300 ease-out`}
                style={{ width: `${Math.min(phaseProgress, 100)}%` }}
              />
            </div>
          )}

          {/* Phase Timeline */}
          <div className="flex items-center justify-between gap-2 pt-2">
            {phases.map((phase, index) => {
              const phaseConfig = PHASE_CONFIGS[phase];
              const isActive = index === currentPhaseIndex;
              const isCompleted = index < currentPhaseIndex;
              
              return (
                <div
                  key={phase}
                  className="flex flex-col items-center gap-1 flex-1"
                  title={phaseConfig.name}
                >
                  {/* Phase Dot */}
                  <div
                    className={`w-3 h-3 rounded-full transition-all duration-300 ${
                      isActive
                        ? `${phaseConfig.color.replace('text-', 'bg-')} ring-2 ring-offset-2 ${phaseConfig.color.replace('text-', 'ring-')}`
                        : isCompleted
                        ? `${phaseConfig.color.replace('text-', 'bg-')} opacity-60`
                        : "bg-gray-300 dark:bg-gray-600"
                    }`}
                  />
                  
                  {/* Phase Label (hidden on small screens) */}
                  <span
                    className={`text-xs hidden sm:block text-center ${
                      isActive
                        ? `${phaseConfig.color} font-medium`
                        : isCompleted
                        ? "text-gray-600 dark:text-gray-400"
                        : "text-gray-400 dark:text-gray-500"
                    }`}
                  >
                    {phaseConfig.name.split(" ")[0]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
