import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { messagesApi } from '@/features/messages/api/messages.api';
import type { SendMessageRequest } from '@/features/messages/types/messages.types';
import { useSessionStore } from '@/store/sessionStore';

export const messageKeys = {
  withUser: (userId: number) => ['users', userId, 'messages'] as const,
};

export function useMessages(userId: number) {
  const isAuthenticated = useSessionStore((s) => s.isAuthenticated);
  return useQuery({
    queryKey: messageKeys.withUser(userId),
    queryFn: () => messagesApi.list(userId),
    enabled: isAuthenticated && Number.isFinite(userId),
  });
}

export function useSendMessage(recipientId: number) {
  const queryClient = useQueryClient();
  const currentUserId = useSessionStore((s) => s.user?.id);

  return useMutation({
    mutationFn: (payload: SendMessageRequest) => messagesApi.send(recipientId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: messageKeys.withUser(recipientId) });
      if (currentUserId !== undefined) {
        void queryClient.invalidateQueries({ queryKey: messageKeys.withUser(currentUserId) });
      }
    },
  });
}
