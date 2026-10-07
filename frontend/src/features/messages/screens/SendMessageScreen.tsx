import {
  Alert,
  AlertIcon,
  Box,
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  HStack,
  Input,
  Link,
  Stack,
  Text,
  Textarea,
  useToast,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import {
  Link as RouterLink,
  Navigate,
  useNavigate,
  useParams,
  useSearchParams,
} from 'react-router-dom';
import { NotFoundScreen } from '@/app/NotFoundScreen';
import { Card } from '@/components/Card';
import { Loader } from '@/components/Loader';
import { Page } from '@/components/Page';
import { UserChip } from '@/components/UserChip';
import { paths } from '@/config/constants';
import { useListing } from '@/features/listings/hooks/useListings';
import { useSendMessage } from '@/features/messages/hooks/useMessages';
import type { SendMessageRequest } from '@/features/messages/types/messages.types';
import { useUser } from '@/features/users/hooks/useUsers';
import { useSessionStore } from '@/store/sessionStore';
import { applyApiError } from '@/utils/forms';

type SendMessageFormValues = Pick<SendMessageRequest, 'subject' | 'body'>;

const FIELDS = ['subject', 'body'] as const;

/** Replaces the message view: /users/:userId/message?listingId=… */
export function SendMessageScreen() {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();
  const recipientId = Number(useParams<{ userId: string }>().userId);
  const [searchParams] = useSearchParams();
  const listingIdParam = searchParams.get('listingId');
  const listingId = listingIdParam ? Number(listingIdParam) : undefined;
  const currentUserId = useSessionStore((s) => s.user?.id);

  const recipient = useUser(recipientId);
  const listing = useListing(listingId ?? Number.NaN);
  const sendMessage = useSendMessage(recipientId);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<SendMessageFormValues>({ defaultValues: { subject: '', body: '' } });

  if (recipientId === currentUserId) return <Navigate to={paths.user(recipientId)} replace />;
  if (recipient.isLoading) return <Loader fullScreen />;
  if (!recipient.data) return <NotFoundScreen />;

  const onSubmit = handleSubmit((values) => {
    sendMessage.mutate(
      { subject: values.subject.trim(), body: values.body.trim(), listing_id: listingId },
      {
        onSuccess: () => {
          toast({ status: 'success', title: t('messages.sent') });
          navigate(paths.user(recipientId));
        },
        onError: (error) => applyApiError(error, setError, t('messages.failed'), FIELDS),
      },
    );
  });

  return (
    <Page title={t('messages.title')} narrow>
      <Card p={{ base: 5, md: 7 }}>
        <Stack spacing={5}>
          <HStack justify="space-between" wrap="wrap" gap={2}>
            <Text fontSize="sm" color="brand.muted">
              {t('messages.to')}
            </Text>
            <UserChip user={recipient.data} showLocation />
          </HStack>
          {listing.data ? (
            <Box px={4} py={3} bg="accent.50" borderRadius="xl" fontSize="sm">
              {t('messages.about')}{' '}
              <Link as={RouterLink} to={paths.listing(listing.data.id)} fontWeight={700}>
                {listing.data.title}
              </Link>
            </Box>
          ) : null}

          <Stack as="form" spacing={5} onSubmit={onSubmit} noValidate>
            {errors.root?.message ? (
              <Alert status="error" borderRadius="12px" fontSize="sm">
                <AlertIcon />
                {errors.root.message}
              </Alert>
            ) : null}

            <FormControl isInvalid={Boolean(errors.subject)}>
              <FormLabel>{t('messages.subject')}</FormLabel>
              <Input
                {...register('subject', {
                  required: t('validation.required'),
                  maxLength: { value: 140, message: t('validation.maxLength', { count: 140 }) },
                })}
              />
              <FormErrorMessage>{errors.subject?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={Boolean(errors.body)}>
              <FormLabel>{t('messages.body')}</FormLabel>
              <Textarea
                rows={6}
                {...register('body', {
                  required: t('validation.required'),
                  maxLength: { value: 1000, message: t('validation.maxLength', { count: 1000 }) },
                })}
              />
              <FormErrorMessage>{errors.body?.message}</FormErrorMessage>
            </FormControl>

            <Button type="submit" size="lg" isLoading={sendMessage.isPending}>
              {t('messages.send')}
            </Button>
          </Stack>
        </Stack>
      </Card>
    </Page>
  );
}
