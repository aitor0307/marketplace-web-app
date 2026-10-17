import { apiClient } from '@/services/apiClient';
import type { SendMessageRequest } from '@/features/messages/types/messages.types';
import type { Message } from '@/types/models';

export const messagesApi = {
  /** Own id → all your messages; someone else's id → your conversation with them. */
  list(userId: number): Promise<Message[]> {
    return apiClient<{ messages: Message[] }>(`/api/v1/users/${userId}/messages`).then(
      (res) => res.messages,
    );
  },

  send(recipientId: number, payload: SendMessageRequest): Promise<Message> {
    return apiClient<{ message: Message }>(`/api/v1/users/${recipientId}/messages`, {
      method: 'POST',
      body: payload,
    }).then((res) => res.message);
  },
};
