import {
  Avatar,
  Badge,
  Box,
  Button,
  Grid,
  Heading,
  HStack,
  Link,
  Stack,
  Tag,
  Text,
  Wrap,
  useDisclosure,
  useToast,
} from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import {
  HiOutlineChatBubbleLeftRight,
  HiOutlineHeart,
  HiHeart,
  HiOutlineTrash,
} from 'react-icons/hi2';
import { Link as RouterLink, useNavigate, useParams } from 'react-router-dom';
import { Card } from '@/components/Card';
import { ConfirmDialog } from '@/components/ConfirmDialog';
import { ErrorState } from '@/components/ErrorState';
import { Loader } from '@/components/Loader';
import { Page } from '@/components/Page';
import { ROUTES, paths } from '@/config/constants';
import { useAddFavorite, useMyFavorites } from '@/features/favorites';
import { ListingImage } from '@/features/listings/components/ListingImage';
import { useDeleteListing, useListing } from '@/features/listings/hooks/useListings';
import { useSessionStore } from '@/store/sessionStore';
import { ApiError } from '@/types/api';
import { formatPrice, formatRelativeTime } from '@/utils/format';
import { NotFoundScreen } from '@/app/NotFoundScreen';

export function ListingDetailScreen() {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();
  const listingId = Number(useParams<{ listingId: string }>().listingId);
  const currentUser = useSessionStore((s) => s.user);
  const confirmDelete = useDisclosure();

  const { data: listing, isLoading, isError, error, refetch } = useListing(listingId);
  const { data: favorites } = useMyFavorites();
  const addFavorite = useAddFavorite();
  const deleteListing = useDeleteListing();

  if (isLoading) return <Loader fullScreen />;
  if (!Number.isFinite(listingId) || (error instanceof ApiError && error.status === 404))
    return <NotFoundScreen />;
  if (isError || !listing) {
    return (
      <Page>
        <ErrorState error={error} onRetry={() => void refetch()} />
      </Page>
    );
  }

  const author = listing.author;
  const isOwner = currentUser?.id === listing.user_id;
  const isFavorite = favorites?.some((fav) => fav.id === listing.id) ?? false;

  const onFavorite = () =>
    addFavorite.mutate(listing.id, {
      onSuccess: ({ created }) =>
        toast({
          status: 'success',
          title: created ? t('favorites.added') : t('favorites.already'),
        }),
      onError: (err) => toast({ status: 'error', title: err.message }),
    });

  const onDelete = () =>
    deleteListing.mutate(listing.id, {
      onSuccess: () => {
        toast({ status: 'success', title: t('listings.deleted') });
        navigate(ROUTES.home, { replace: true });
      },
      onError: (err) => {
        confirmDelete.onClose();
        toast({ status: 'error', title: err.message });
      },
    });

  return (
    <Page>
      <Grid
        templateColumns={{ base: '1fr', lg: 'minmax(0, 2fr) minmax(280px, 1fr)' }}
        gap={6}
        alignItems="start"
      >
        <Card p={0} overflow="hidden">
          <ListingImage
            src={listing.image_url}
            alt={listing.title}
            h={{ base: '260px', md: '420px' }}
          />
          <Stack spacing={4} p={{ base: 5, md: 7 }}>
            <HStack spacing={2} wrap="wrap">
              <Badge
                bg="brand.primary"
                color="white"
                px={3}
                py={1}
                borderRadius="8px"
                fontSize="md"
                textTransform="none"
              >
                {formatPrice(listing.price)}
              </Badge>
              <Badge
                bg="accent.50"
                color="accent.800"
                px={3}
                py={1}
                borderRadius="8px"
                textTransform="none"
              >
                {t(`conditions.${listing.condition}`, { defaultValue: listing.condition })}
              </Badge>
            </HStack>
            <Box>
              <Heading as="h1" size="lg">
                {listing.title}
              </Heading>
              <Text mt={1} fontSize="sm" color="brand.muted">
                {t('listings.posted', { when: formatRelativeTime(listing.timestamp) })}
              </Text>
            </Box>
            <Text whiteSpace="pre-wrap" lineHeight="1.7">
              {listing.body}
            </Text>
            {listing.tags.length ? (
              <Wrap spacing={2}>
                {listing.tags.map((tag) => (
                  <Tag
                    key={tag}
                    size="sm"
                    borderRadius="full"
                    bg="brand.surfaceMuted"
                    color="brand.text"
                  >
                    #{tag}
                  </Tag>
                ))}
              </Wrap>
            ) : null}
            {isOwner ? (
              <Box pt={2}>
                <Button
                  size="sm"
                  variant="outline"
                  color="brand.danger"
                  leftIcon={<HiOutlineTrash />}
                  onClick={confirmDelete.onOpen}
                >
                  {t('listings.delete')}
                </Button>
              </Box>
            ) : null}
          </Stack>
        </Card>

        <Stack spacing={4} position={{ lg: 'sticky' }} top={{ lg: '88px' }}>
          {author ? (
            <Card>
              <Text
                fontSize="xs"
                fontWeight={700}
                color="brand.muted"
                textTransform="uppercase"
                letterSpacing="0.04em"
                mb={3}
              >
                {t('listings.postedBy')}
              </Text>
              <HStack spacing={3} align="center">
                <Avatar
                  size="lg"
                  name={author.name ?? undefined}
                  src={author.avatar_url ?? undefined}
                />
                <Box minW={0}>
                  <Link as={RouterLink} to={paths.user(author.id)} fontSize="lg" fontWeight={700}>
                    {author.name}
                  </Link>
                  {author.city || author.state ? (
                    <Text fontSize="sm" color="brand.muted">
                      {[author.city, author.state].filter(Boolean).join(', ')}
                    </Text>
                  ) : null}
                </Box>
              </HStack>
              {!isOwner ? (
                <Button
                  as={RouterLink}
                  to={paths.sendMessage(author.id, listing.id)}
                  mt={5}
                  w="full"
                  leftIcon={<HiOutlineChatBubbleLeftRight />}
                >
                  {t('listings.messageSeller')}
                </Button>
              ) : null}
            </Card>
          ) : null}

          {currentUser && !isOwner ? (
            <Button
              variant="outline"
              leftIcon={isFavorite ? <HiHeart /> : <HiOutlineHeart />}
              onClick={onFavorite}
              isLoading={addFavorite.isPending}
              isDisabled={isFavorite}
            >
              {isFavorite ? t('favorites.inFavorites') : t('favorites.add')}
            </Button>
          ) : null}
        </Stack>
      </Grid>

      <ConfirmDialog
        isOpen={confirmDelete.isOpen}
        onClose={confirmDelete.onClose}
        onConfirm={onDelete}
        isLoading={deleteListing.isPending}
        title={t('listings.deleteTitle')}
        description={t('listings.deleteDesc')}
        confirmLabel={t('listings.delete')}
      />
    </Page>
  );
}
