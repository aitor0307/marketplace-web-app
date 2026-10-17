import { Button } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { HiOutlineHeart } from 'react-icons/hi2';
import { Link as RouterLink } from 'react-router-dom';
import { EmptyStateCard } from '@/components/EmptyStateCard';
import { ErrorState } from '@/components/ErrorState';
import { Page } from '@/components/Page';
import { ROUTES } from '@/config/constants';
import { useMyFavorites } from '@/features/favorites/hooks/useFavorites';
import { ListingGrid } from '@/features/listings/components/ListingGrid';

/** The signed-in user's saved listings, most recently added first. */
export function FavoritesScreen() {
  const { t } = useTranslation();
  const { data: favorites, isLoading, isError, error, refetch } = useMyFavorites();

  return (
    <Page title={t('favorites.title')} subtitle={t('favorites.subtitle')}>
      {isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <ListingGrid
          listings={favorites}
          isLoading={isLoading}
          empty={
            <EmptyStateCard
              icon={HiOutlineHeart}
              title={t('favorites.empty')}
              description={t('favorites.emptyDesc')}
              action={
                <Button as={RouterLink} to={ROUTES.home} variant="accent" size="sm">
                  {t('favorites.browse')}
                </Button>
              }
            />
          }
        />
      )}
    </Page>
  );
}
