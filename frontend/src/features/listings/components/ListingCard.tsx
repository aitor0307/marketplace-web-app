import { Badge, Box, Flex, LinkBox, LinkOverlay, Text } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import { UserChip } from '@/components/UserChip';
import { paths } from '@/config/constants';
import { ListingImage } from '@/features/listings/components/ListingImage';
import type { Listing } from '@/types/models';
import { formatPrice, formatRelativeTime } from '@/utils/format';

type ListingCardProps = {
  listing: Listing;
  /** The index shows who's selling; a profile page already knows. */
  showAuthor?: boolean;
};

export function ListingCard({ listing, showAuthor = true }: ListingCardProps) {
  const { t } = useTranslation();

  return (
    <LinkBox
      as="article"
      bg="brand.surface"
      borderRadius="2xl"
      borderWidth="1px"
      borderColor="brand.border"
      overflow="hidden"
      boxShadow="card"
      transition="box-shadow 0.2s ease, transform 0.2s ease"
      _hover={{ boxShadow: 'cardHover', transform: 'translateY(-2px)' }}
      display="flex"
      flexDir="column"
    >
      <Box position="relative">
        <ListingImage src={listing.image_url} alt={listing.title} h="180px" />
        <Badge
          position="absolute"
          top={3}
          left={3}
          bg="brand.primary"
          color="white"
          px={2.5}
          py={1}
          borderRadius="8px"
          fontSize="sm"
          textTransform="none"
        >
          {formatPrice(listing.price)}
        </Badge>
      </Box>
      <Flex direction="column" p={4} gap={1} flex="1">
        <Text
          fontSize="xs"
          fontWeight={700}
          color="accent.700"
          textTransform="uppercase"
          letterSpacing="0.04em"
        >
          {t(`conditions.${listing.condition}`, { defaultValue: listing.condition })}
        </Text>
        <LinkOverlay as={RouterLink} to={paths.listing(listing.id)}>
          <Text fontWeight={600} color="brand.heading" noOfLines={2}>
            {listing.title}
          </Text>
        </LinkOverlay>
        <Text fontSize="xs" color="brand.muted">
          {t('listings.posted', { when: formatRelativeTime(listing.timestamp) })}
        </Text>
        {showAuthor && listing.author ? (
          // Its own link above the overlay, like the views' separate author anchor.
          <Box mt="auto" pt={3} position="relative" zIndex={1}>
            <UserChip user={listing.author} size="xs" />
          </Box>
        ) : null}
      </Flex>
    </LinkBox>
  );
}
