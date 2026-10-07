import { Button, Flex, FormControl, FormLabel, Input, Select } from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { LISTING_CONDITIONS } from '@/config/constants';
import type { ListingFilters } from '@/features/listings/types/listings.types';

type ListingFiltersBarProps = {
  value: ListingFilters;
  onChange: (filters: ListingFilters) => void;
};

/** Condition + price range, the same filters as the index view's FilterForm. */
export function ListingFiltersBar({ value, onChange }: ListingFiltersBarProps) {
  const { t } = useTranslation();
  const { register, handleSubmit, reset } = useForm<ListingFilters>({ values: value });
  const hasFilters = Boolean(value.condition || value.price_min || value.price_max);

  return (
    <Flex
      as="form"
      onSubmit={handleSubmit(onChange)}
      gap={3}
      align="flex-end"
      wrap="wrap"
      mb={6}
      p={4}
      bg="brand.surface"
      borderRadius="2xl"
      borderWidth="1px"
      borderColor="brand.border"
    >
      <FormControl w={{ base: 'full', sm: '180px' }}>
        <FormLabel>{t('listings.condition')}</FormLabel>
        <Select size="sm" {...register('condition')}>
          <option value="">{t('listings.anyCondition')}</option>
          {LISTING_CONDITIONS.map((condition) => (
            <option key={condition} value={condition}>
              {t(`conditions.${condition}`)}
            </option>
          ))}
        </Select>
      </FormControl>
      <FormControl w={{ base: 'calc(50% - 6px)', sm: '120px' }}>
        <FormLabel>{t('listings.priceMin')}</FormLabel>
        <Input
          size="sm"
          type="number"
          min={0}
          step="any"
          inputMode="decimal"
          {...register('price_min')}
        />
      </FormControl>
      <FormControl w={{ base: 'calc(50% - 6px)', sm: '120px' }}>
        <FormLabel>{t('listings.priceMax')}</FormLabel>
        <Input
          size="sm"
          type="number"
          min={0}
          step="any"
          inputMode="decimal"
          {...register('price_max')}
        />
      </FormControl>
      <Flex gap={2}>
        <Button type="submit" size="sm">
          {t('listings.applyFilters')}
        </Button>
        {hasFilters ? (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              reset({ condition: '', price_min: '', price_max: '' });
              onChange({});
            }}
          >
            {t('listings.clearFilters')}
          </Button>
        ) : null}
      </Flex>
    </Flex>
  );
}
