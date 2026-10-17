import { Button, IconButton, useToast } from '@chakra-ui/react';
import type { MouseEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { HiHeart, HiOutlineHeart } from 'react-icons/hi2';
import { useIsFavorite, useToggleFavorite } from '@/features/favorites/hooks/useFavorites';
import { useSessionStore } from '@/store/sessionStore';
import type { Listing } from '@/types/models';

type FavoriteButtonProps = {
  listing: Listing;
  /** `icon`: the round heart overlaid on a card; `button`: the labelled detail-page button. */
  variant?: 'icon' | 'button';
};

/** Hidden for guests and on the user's own listings. */
export function FavoriteButton({ listing, variant = 'icon' }: FavoriteButtonProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const currentUser = useSessionStore((s) => s.user);
  const isFavorite = useIsFavorite(listing.id);
  const toggle = useToggleFavorite();

  if (!currentUser || currentUser.id === listing.user_id) return null;

  const onClick = (event: MouseEvent) => {
    // On a card the button sits over the listing link.
    event.preventDefault();
    event.stopPropagation();
    toggle.mutate(
      { listing, isFavorite },
      {
        onSuccess: () =>
          toast({
            status: 'success',
            title: isFavorite ? t('favorites.removed') : t('favorites.added'),
            duration: 2000,
          }),
        onError: (err) => toast({ status: 'error', title: err.message }),
      },
    );
  };

  const label = isFavorite ? t('favorites.remove') : t('favorites.add');
  const icon = isFavorite ? <HiHeart /> : <HiOutlineHeart />;

  if (variant === 'button') {
    return (
      <Button variant="outline" leftIcon={icon} onClick={onClick} aria-pressed={isFavorite}>
        {isFavorite ? t('favorites.inFavorites') : t('favorites.add')}
      </Button>
    );
  }

  return (
    <IconButton
      aria-label={label}
      title={label}
      aria-pressed={isFavorite}
      icon={icon}
      onClick={onClick}
      size="sm"
      isRound
      bg="whiteAlpha.900"
      color={isFavorite ? 'red.500' : 'brand.heading'}
      fontSize="lg"
      boxShadow="card"
      _hover={{ bg: 'white', transform: 'scale(1.08)' }}
    />
  );
}
