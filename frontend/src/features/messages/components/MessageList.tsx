import { Avatar, Box, HStack, Link, Stack, Text } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { HiArrowLongRight } from 'react-icons/hi2';
import { Link as RouterLink } from 'react-router-dom';
import { paths } from '@/config/constants';
import type { Message, UserSummary } from '@/types/models';
import { formatDateTime } from '@/utils/format';

type MessageListProps = {
  messages: Message[];
  currentUserId: number;
};

function Party({ user, isYou }: { user: UserSummary | null; isYou: boolean }) {
  const { t } = useTranslation();
  if (isYou || !user) {
    return (
      <Text as="span" fontWeight={700} color="brand.heading">
        {t('messages.you')}
      </Text>
    );
  }
  return (
    <Link as={RouterLink} to={paths.user(user.id)}>
      {user.name}
    </Link>
  );
}

export function MessageList({ messages, currentUserId }: MessageListProps) {
  const { t } = useTranslation();

  return (
    <Stack spacing={0} divider={<Box borderBottomWidth="1px" borderColor="brand.border" />}>
      {messages.map((message) => {
        const sentByMe = message.sender_id === currentUserId;
        const counterpart = sentByMe ? message.recipient : message.sender;
        return (
          <HStack key={message.id} align="flex-start" spacing={3} py={4}>
            <Avatar
              size="sm"
              name={counterpart?.name ?? undefined}
              src={counterpart?.avatar_url ?? undefined}
            />
            <Box minW={0} flex="1">
              <HStack spacing={1.5} fontSize="sm" wrap="wrap">
                <Party user={message.sender} isYou={sentByMe} />
                <HiArrowLongRight />
                <Party user={message.recipient} isYou={!sentByMe} />
                <Text as="span" color="brand.muted">
                  · {formatDateTime(message.timestamp)}
                </Text>
                {message.listing ? (
                  <Text as="span" color="brand.muted">
                    · {t('messages.re')}{' '}
                    <Link as={RouterLink} to={paths.listing(message.listing.id)}>
                      {message.listing.title}
                    </Link>
                  </Text>
                ) : null}
              </HStack>
              <Text mt={1} fontWeight={700} color="brand.heading">
                {message.subject}
              </Text>
              <Text mt={0.5} whiteSpace="pre-wrap" color="brand.text">
                {message.body}
              </Text>
            </Box>
          </HStack>
        );
      })}
    </Stack>
  );
}
