import {
  Avatar,
  Box,
  Button,
  Flex,
  Heading,
  Link,
  Stack,
  Text,
  Wrap,
  WrapItem,
} from '@chakra-ui/react';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import {
  HiOutlineChatBubbleLeftRight,
  HiOutlineMapPin,
  HiOutlinePencilSquare,
  HiOutlineShoppingBag,
} from 'react-icons/hi2';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { NotFoundScreen } from '@/app/NotFoundScreen';
import { Card } from '@/components/Card';
import { EmptyStateCard } from '@/components/EmptyStateCard';
import { ErrorState } from '@/components/ErrorState';
import { Loader } from '@/components/Loader';
import { Page } from '@/components/Page';
import { ROUTES, paths } from '@/config/constants';
import { useMyFavorites } from '@/features/favorites';
import { ListingGrid } from '@/features/listings';
import { MessageList } from '@/features/messages/components/MessageList';
import { useMessages } from '@/features/messages/hooks/useMessages';
import { useUser, useUserListings } from '@/features/users/hooks/useUsers';
import { useSessionStore } from '@/store/sessionStore';
import { ApiError } from '@/types/api';
import { formatDateTime } from '@/utils/format';

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Box as="section" mt={10}>
      <Heading as="h2" size="md" mb={4}>
        {title}
      </Heading>
      {children}
    </Box>
  );
}

/** Replaces the user view: profile card, own favorites, messages, listings. */
export function UserProfileScreen() {
  const { t } = useTranslation();
  const userId = Number(useParams<{ userId: string }>().userId);
  const currentUser = useSessionStore((s) => s.user);
  const isSelf = currentUser?.id === userId;

  const { data: user, isLoading, isError, error, refetch } = useUser(userId);
  const listings = useUserListings(userId);
  const messages = useMessages(userId);
  const favorites = useMyFavorites();

  if (isLoading) return <Loader fullScreen />;
  if (!Number.isFinite(userId) || (error instanceof ApiError && error.status === 404))
    return <NotFoundScreen />;
  if (isError || !user) {
    return (
      <Page>
        <ErrorState error={error} onRetry={() => void refetch()} />
      </Page>
    );
  }

  const location = [user.city, user.state].filter(Boolean).join(', ');

  return (
    <Page>
      <Card p={{ base: 5, md: 8 }}>
        <Flex
          direction={{ base: 'column', sm: 'row' }}
          gap={6}
          align={{ base: 'flex-start', sm: 'center' }}
        >
          <Avatar size="2xl" name={user.name ?? undefined} src={user.avatar_url ?? undefined} />
          <Stack spacing={1} flex="1" minW={0}>
            <Heading as="h1" size="lg">
              {user.name}
            </Heading>
            {location ? (
              <Flex align="center" gap={1.5} color="brand.muted" fontSize="sm">
                <HiOutlineMapPin />
                {location}
              </Flex>
            ) : null}
            {user.last_seen ? (
              <Text fontSize="sm" color="brand.muted">
                {t('profile.lastSeen', { when: formatDateTime(user.last_seen) })}
              </Text>
            ) : null}
          </Stack>
          {isSelf ? (
            <Button
              as={RouterLink}
              to={ROUTES.editProfile}
              variant="outline"
              leftIcon={<HiOutlinePencilSquare />}
            >
              {t('profile.edit')}
            </Button>
          ) : (
            <Button
              as={RouterLink}
              to={paths.sendMessage(user.id)}
              leftIcon={<HiOutlineChatBubbleLeftRight />}
            >
              {t('profile.message', { name: user.name })}
            </Button>
          )}
        </Flex>
      </Card>

      {isSelf && favorites.data?.length ? (
        <Section title={t('profile.myFavorites')}>
          <Wrap spacing={2}>
            {favorites.data.map((listing) => (
              <WrapItem key={listing.id}>
                <Link
                  as={RouterLink}
                  to={paths.listing(listing.id)}
                  px={3}
                  py={1.5}
                  borderRadius="full"
                  bg="accent.50"
                  fontSize="sm"
                >
                  {listing.title}
                </Link>
              </WrapItem>
            ))}
          </Wrap>
        </Section>
      ) : null}

      {messages.data?.length && currentUser ? (
        <Section
          title={isSelf ? t('profile.myMessages') : t('profile.messagesWith', { name: user.name })}
        >
          <Card py={1}>
            <MessageList messages={messages.data} currentUserId={currentUser.id} />
          </Card>
        </Section>
      ) : null}

      <Section
        title={isSelf ? t('profile.myListings') : t('profile.userListings', { name: user.name })}
      >
        <ListingGrid
          listings={listings.data}
          isLoading={listings.isLoading}
          showAuthor={false}
          empty={
            <EmptyStateCard
              icon={HiOutlineShoppingBag}
              title={t('profile.noListings')}
              action={
                isSelf ? (
                  <Button as={RouterLink} to={ROUTES.newListing} size="sm" variant="accent">
                    {t('listings.sellSomething')}
                  </Button>
                ) : undefined
              }
            />
          }
        />
      </Section>
    </Page>
  );
}
