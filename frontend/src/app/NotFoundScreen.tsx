import { Button } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { HiOutlineMapPin } from 'react-icons/hi2';
import { Link as RouterLink } from 'react-router-dom';
import { EmptyStateCard } from '@/components/EmptyStateCard';
import { Page } from '@/components/Page';
import { ROUTES } from '@/config/constants';

export function NotFoundScreen() {
  const { t } = useTranslation();
  return (
    <Page narrow>
      <EmptyStateCard
        icon={HiOutlineMapPin}
        title={t('notFound.title')}
        description={t('notFound.description')}
        action={
          <Button as={RouterLink} to={ROUTES.home} size="sm">
            {t('notFound.backHome')}
          </Button>
        }
      />
    </Page>
  );
}
