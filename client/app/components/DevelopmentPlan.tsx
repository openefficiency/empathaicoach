"use client";

/**
 * DevelopmentPlan Component
 * 
 * Displays and manages development plan goals created during the R2C2 coaching phase.
 * 
 * Features:
 * - Display goals with type indicators (start/stop/continue)
 * - Show action steps, success criteria, and target dates
 * - Mark goals as complete with API integration
 * - Edit goals during coaching phase (when editable=true)
 * - Visual feedback for completion status
 * - Loading states during API calls
 * 
 * Requirements satisfied:
 * - 6.2: Display goals with type (start/stop/continue)
 * - 6.3: Show action steps and target dates
 * - 6.4: Add checkboxes for marking goals complete
 * - 6.5: Make goals editable during coaching phase
 * - 13.4: Integrate with goal completion API
 * 
 * Usage:
 * ```tsx
 * import { DevelopmentPlan } from './components/DevelopmentPlan';
 * 
 * <DevelopmentPlan
 *   goals={developmentPlanGoals}
 *   onGoalComplete={(goalId, completedAt) => {
 *     // Update local state with completion
 *     updateGoalInState(goalId, { is_completed: true, completed_at: completedAt });
 *   }}
 *   editable={currentPhase === 'coaching'}
 *   onGoalUpdate={(updatedGoal) => {
 *     // Handle goal updates during editing
 *     updateGoalInState(updatedGoal.goal_id, updatedGoal);
 *   }}
 * />
 * ```
 */

import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
} from "@pipecat-ai/voice-ui-kit";
import {
  CheckCircle2,
  Circle,
  Calendar,
  Target,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Edit2,
  Save,
  X,
  Loader2,
} from "lucide-react";
import { markGoalComplete, type Goal } from "../lib/api";

interface DevelopmentPlanProps {
  goals: Goal[];
  onGoalComplete?: (goalId: number, completedAt: string) => void;
  editable?: boolean;
  onGoalUpdate?: (goal: Goal) => void;
}

export type { Goal };

export const DevelopmentPlan: React.FC<DevelopmentPlanProps> = ({
  goals,
  onGoalComplete,
  editable = false,
  onGoalUpdate,
}) => {
  const [editingGoalId, setEditingGoalId] = useState<number | null>(null);
  const [editedGoal, setEditedGoal] = useState<Goal | null>(null);
  const [completingGoalId, setCompletingGoalId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getGoalTypeIcon = (type: string) => {
    switch (type) {
      case "start":
        return <TrendingUp className="h-5 w-5 text-green-600" />;
      case "stop":
        return <TrendingDown className="h-5 w-5 text-red-600" />;
      case "continue":
        return <ArrowRight className="h-5 w-5 text-blue-600" />;
      default:
        return <Target className="h-5 w-5 text-gray-600" />;
    }
  };

  const getGoalTypeColor = (type: string) => {
    switch (type) {
      case "start":
        return "bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800";
      case "stop":
        return "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800";
      case "continue":
        return "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800";
      default:
        return "bg-gray-50 border-gray-200 dark:bg-gray-900/20 dark:border-gray-800";
    }
  };

  const getGoalTypeLabel = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1);
  };

  const handleCheckboxChange = async (goalId: number, isCompleted: boolean) => {
    if (isCompleted) return; // Already completed
    
    setCompletingGoalId(goalId);
    setError(null);
    
    try {
      // Call the API to mark the goal as complete
      const response = await markGoalComplete(goalId);
      
      // Notify parent component with the completion timestamp
      if (onGoalComplete) {
        onGoalComplete(goalId, response.completed_at);
      }
    } catch (err) {
      console.error("Failed to mark goal as complete:", err);
      setError(err instanceof Error ? err.message : "Failed to mark goal as complete");
    } finally {
      setCompletingGoalId(null);
    }
  };

  const handleEditClick = (goal: Goal) => {
    setEditingGoalId(goal.goal_id);
    setEditedGoal({ ...goal });
  };

  const handleSaveClick = () => {
    if (editedGoal && onGoalUpdate) {
      onGoalUpdate(editedGoal);
    }
    setEditingGoalId(null);
    setEditedGoal(null);
  };

  const handleCancelClick = () => {
    setEditingGoalId(null);
    setEditedGoal(null);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "No date set";
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateString;
    }
  };

  if (goals.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Development Plan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Target className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p className="text-lg font-medium">No goals yet</p>
            <p className="text-sm mt-1">
              Your development plan will appear here during the coaching phase
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5" />
          Development Plan
          <span className="ml-auto text-sm font-normal text-gray-500">
            {goals.filter((g) => g.is_completed).length} of {goals.length}{" "}
            completed
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}
        <div className="space-y-4">
          {goals.map((goal) => {
            const isEditing = editingGoalId === goal.goal_id;
            const displayGoal = isEditing && editedGoal ? editedGoal : goal;

            return (
              <div
                key={goal.goal_id}
                className={`border rounded-lg p-4 transition-all ${getGoalTypeColor(
                  goal.goal_type
                )} ${
                  goal.is_completed ? "opacity-60" : ""
                }`}
              >
                {/* Goal Header */}
                <div className="flex items-start gap-3 mb-3">
                  <button
                    onClick={() =>
                      handleCheckboxChange(goal.goal_id, goal.is_completed)
                    }
                    disabled={goal.is_completed || completingGoalId === goal.goal_id}
                    className="mt-1 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded disabled:cursor-not-allowed"
                    aria-label={
                      goal.is_completed
                        ? "Goal completed"
                        : "Mark goal as complete"
                    }
                  >
                    {completingGoalId === goal.goal_id ? (
                      <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
                    ) : goal.is_completed ? (
                      <CheckCircle2 className="h-6 w-6 text-green-600" />
                    ) : (
                      <Circle className="h-6 w-6 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>

                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getGoalTypeIcon(goal.goal_type)}
                      <span className="font-semibold text-sm uppercase tracking-wide">
                        {getGoalTypeLabel(goal.goal_type)}
                      </span>
                      {editable && !goal.is_completed && !isEditing && (
                        <button
                          onClick={() => handleEditClick(goal)}
                          className="ml-auto p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                          aria-label="Edit goal"
                        >
                          <Edit2 className="h-4 w-4" />
                        </button>
                      )}
                      {isEditing && (
                        <div className="ml-auto flex gap-1">
                          <button
                            onClick={handleSaveClick}
                            className="p-1 hover:bg-green-200 dark:hover:bg-green-700 rounded"
                            aria-label="Save changes"
                          >
                            <Save className="h-4 w-4 text-green-600" />
                          </button>
                          <button
                            onClick={handleCancelClick}
                            className="p-1 hover:bg-red-200 dark:hover:bg-red-700 rounded"
                            aria-label="Cancel editing"
                          >
                            <X className="h-4 w-4 text-red-600" />
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Goal Text */}
                    {isEditing ? (
                      <textarea
                        value={displayGoal.goal_text}
                        onChange={(e) =>
                          setEditedGoal({
                            ...displayGoal,
                            goal_text: e.target.value,
                          })
                        }
                        className="w-full p-2 border rounded text-lg font-medium mb-2 dark:bg-gray-800 dark:border-gray-600"
                        rows={2}
                      />
                    ) : (
                      <p
                        className={`text-lg font-medium mb-2 ${
                          goal.is_completed ? "line-through" : ""
                        }`}
                      >
                        {displayGoal.goal_text}
                      </p>
                    )}

                    {/* Specific Behavior */}
                    <div className="mb-2">
                      <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Specific Behavior:
                      </p>
                      {isEditing ? (
                        <textarea
                          value={displayGoal.specific_behavior}
                          onChange={(e) =>
                            setEditedGoal({
                              ...displayGoal,
                              specific_behavior: e.target.value,
                            })
                          }
                          className="w-full p-2 border rounded text-sm dark:bg-gray-800 dark:border-gray-600"
                          rows={2}
                        />
                      ) : (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {displayGoal.specific_behavior}
                        </p>
                      )}
                    </div>

                    {/* Measurable Criteria */}
                    <div className="mb-2">
                      <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                        Success Criteria:
                      </p>
                      {isEditing ? (
                        <textarea
                          value={displayGoal.measurable_criteria}
                          onChange={(e) =>
                            setEditedGoal({
                              ...displayGoal,
                              measurable_criteria: e.target.value,
                            })
                          }
                          className="w-full p-2 border rounded text-sm dark:bg-gray-800 dark:border-gray-600"
                          rows={2}
                        />
                      ) : (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {displayGoal.measurable_criteria}
                        </p>
                      )}
                    </div>

                    {/* Action Steps */}
                    {displayGoal.action_steps.length > 0 && (
                      <div className="mb-2">
                        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
                          Action Steps:
                        </p>
                        <ul className="list-disc list-inside space-y-1">
                          {displayGoal.action_steps.map((step, index) => (
                            <li
                              key={index}
                              className="text-sm text-gray-600 dark:text-gray-400"
                            >
                              {step}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Target Date */}
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mt-3">
                      <Calendar className="h-4 w-4" />
                      <span>
                        Target: {formatDate(displayGoal.target_date)}
                      </span>
                    </div>

                    {/* Completion Date */}
                    {goal.is_completed && goal.completed_at && (
                      <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400 mt-1">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>
                          Completed: {formatDate(goal.completed_at)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
