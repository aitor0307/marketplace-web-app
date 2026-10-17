import { apiClient } from '@/services/apiClient';

/** Mirrors FeedbackKind in app/schemas/feedback.py. */
export const FEEDBACK_KINDS = ['bug', 'improvement'] as const;
export type FeedbackKind = (typeof FEEDBACK_KINDS)[number];

/** Mirrors SendFeedbackPayload in app/schemas/feedback.py. */
export type SendFeedbackRequest = {
  kind: FeedbackKind;
  message: string;
  page?: string;
};

export const feedbackApi = {
  /** Emailed to the admin (FEEDBACK_EMAIL); replies go to the user. */
  send(payload: SendFeedbackRequest): Promise<{ sent: boolean }> {
    return apiClient('/api/v1/feedback', { method: 'POST', body: payload });
  },
};
