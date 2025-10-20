/**
 * API client functions for R2C2 Voice Coach
 */

export interface Goal {
  goal_id: number;
  goal_text: string;
  goal_type: "start" | "stop" | "continue";
  specific_behavior: string;
  measurable_criteria: string;
  target_date?: string;
  action_steps: string[];
  is_completed: boolean;
  completed_at?: string;
}

export interface GoalCompleteResponse {
  success: boolean;
  goal_id: number;
  completed_at: string;
  message: string;
}

/**
 * Mark a development plan goal as completed
 * @param goalId - The ID of the goal to mark as complete
 * @returns Promise with the completion response
 */
export async function markGoalComplete(
  goalId: number
): Promise<GoalCompleteResponse> {
  const response = await fetch(`/api/goal/${goalId}/complete`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to mark goal ${goalId} as complete`
    );
  }

  return response.json();
}

/**
 * Get session details including development plan
 * @param sessionId - The session ID
 * @returns Promise with session details
 */
export async function getSessionDetail(sessionId: number) {
  const response = await fetch(`/api/session/${sessionId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch session ${sessionId}`
    );
  }

  return response.json();
}

/**
 * Get session history for a user
 * @param userId - The user ID
 * @returns Promise with session history
 */
export async function getSessionHistory(userId: string) {
  const response = await fetch(`/api/sessions/${userId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to fetch sessions for user ${userId}`
    );
  }

  return response.json();
}
