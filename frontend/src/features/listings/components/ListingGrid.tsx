import { SimpleGrid, Skeleton } from '@chakra-ui/react';
import type { ReactNode } from 'react';
import { ListingCard } from '@/features/listings/components/ListingCard';
import type { Listing } from '@/types/models';

type ListingGridProps = {
  listings: Listing[] | undefined;
  isLoading: boolean;
  empty: ReactNode;
  showAuthor?: boolean;
};

const COLUMNS = { base: 1, sm: 2, md: 3, lg: 4 };

export function ListingGrid({ listings, isLoading, empty, showAuthor }: ListingGridProps) {
  if (isLoading) {
    return (
      <SimpleGrid columns={COLUMNS} spacing={5}>
        {Array.from({ length: 8 }, (_, i) => (
          <Skeleton key={i} h="300px" borderRadius="2xl" />
        ))}
      </SimpleGrid>
    );
  }

  if (!listings?.length) return <>{empty}</>;

  return (
    <SimpleGrid columns={COLUMNS} spacing={5}>
      {listings.map((listing) => (
        <ListingCard key={listing.id} listing={listing} showAuthor={showAuthor} />
      ))}
    </SimpleGrid>
  );
}
