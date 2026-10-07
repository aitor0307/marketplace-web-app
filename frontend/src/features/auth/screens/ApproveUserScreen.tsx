import { Alert, AlertIcon, Avatar, Box, Button, HStack, Stack, Text } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { Card } from '@/components/Card';
import { ErrorState } from '@/components/ErrorState';
import { Loader } from '@/components/Loader';
import { Page } from '@/components/Page';
import { useApproval, useApproveUser } from '@/features/auth/hooks/useAuth';

/**
 * Opened from the approval email. Viewing it changes nothing: approving is
 * an explicit POST, so mail scanners prefetching the link can't approve.
 */
export function ApproveUserScreen() {
  const { t } = useTranslation();
  const token = useParams<{ token: string }>().token ?? '';
  const { data: user, isLoading, error } = useApproval(token);
  const approve = useApproveUser(token);

  if (isLoading) return <Loader fullScreen />;
  if (error || !user) {
    return (
      <Page narrow>
        <ErrorState error={error} />
      </Page>
    );
  }

  const isActive = user.status === 'active';

  return (
    <Page title={t('approval.title')} subtitle={t('approval.subtitle')} narrow>
      <Card>
        <Stack spacing={5}>
          <HStack spacing={3}>
            <Avatar size="lg" name={user.name ?? undefined} src={user.avatar_url ?? undefined} />
            <Box minW={0}>
              <Text fontSize="lg" fontWeight={700}>
                {user.name}
              </Text>
              <Text fontSize="sm" color="brand.muted">
                {user.email}
              </Text>
              {user.city || user.state ? (
                <Text fontSize="sm" color="brand.muted">
                  {[user.city, user.state].filter(Boolean).join(', ')}
                </Text>
              ) : null}
            </Box>
          </HStack>

          {approve.isError ? (
            <Alert status="error" borderRadius="12px" fontSize="sm">
              <AlertIcon />
              {approve.error.message || t('approval.failed')}
            </Alert>
          ) : null}

          {isActive ? (
            <Alert status="success" borderRadius="12px" fontSize="sm">
              <AlertIcon />
              {approve.isSuccess ? t('approval.approved') : t('approval.alreadyActive')}
            </Alert>
          ) : (
            <>
              <Text fontSize="sm" color="brand.muted">
                {t('approval.pendingDesc')}
              </Text>
              <Button size="lg" onClick={() => approve.mutate()} isLoading={approve.isPending}>
                {t('approval.approve')}
              </Button>
            </>
          )}
        </Stack>
      </Card>
    </Page>
  );
}
