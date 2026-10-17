import { Button } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { HiOutlineExclamationTriangle } from 'react-icons/hi2';
import { EmptyStateCard } from '@/components/EmptyStateCard';

type ErrorStateProps = {
  error?: unknown;
  onRetry?: () => void;
};

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  const { t } = useTranslation();
  return (
    <EmptyStateCard
      icon={HiOutlineExclamationTriangle}
      title={t('common.error')}
      description={error instanceof Error ? error.message : undefined}
      action={
        onRetry ? (
          <Button size="sm" variant="outline" onClick={onRetry}>
            {t('common.retry')}
          </Button>
        ) : undefined
      }
    />
  );
}
