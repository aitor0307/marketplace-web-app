/** Mirrors SendMessagePayload in app/schemas/messages.py. */
export type SendMessageRequest = {
  subject: string;
  body: string;
  listing_id?: number;
};
