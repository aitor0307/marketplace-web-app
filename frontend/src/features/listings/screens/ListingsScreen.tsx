import { Button } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { HiOutlineShoppingBag } from 'react-icons/hi2';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import { EmptyStateCard } from '@/components/EmptyStateCard';
import { ErrorState } from '@/components/ErrorState';
import { Page } from '@/components/Page';
import { ROUTES, type ListingCondition } from '@/config/constants';
import { ListingFiltersBar } from '@/features/listings/components/ListingFiltersBar';
import { ListingGrid } from '@/features/listings/components/ListingGrid';
import { useListings } from '@/features/listings/hooks/useListings';
import type { ListingFilters } from '@/features/listings/types/listings.types';

/** Replaces the index view. Filters live in the URL so results are shareable. */
export function ListingsScreen() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  const filters: ListingFilters = {
    condition: (searchParams.get('condition') ?? '') as ListingCondition | '',
    price_min: searchParams.get('price_min') ?? '',
    price_max: searchParams.get('price_max') ?? '',
  };
  const { data: listings, isLoading, isError, error, refetch } = useListings(filters);

  const onFiltersChange = (next: ListingFilters) => {
    const params = new URLSearchParams();
    Object.entries(next).forEach(([key, value]) => {
      if (value) params.set(key, String(value));
    });
    setSearchParams(params);
  };

  return (
    <Page
      title={t('listings.title')}
      subtitle={t('listings.subtitle')}
      actions={
        <Button as={RouterLink} to={ROUTES.newListing} variant="accent">
          {t('listings.sellSomething')}
        </Button>
      }
    >
      <ListingFiltersBar value={filters} onChange={onFiltersChange} />
      {isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <ListingGrid
          listings={listings}
          isLoading={isLoading}
          empty={
            <EmptyStateCard
              icon={HiOutlineShoppingBag}
              title={t('listings.empty')}
              description={t('listings.emptyDesc')}
            />
          }
        />
      )}
    </Page>
  );
}
