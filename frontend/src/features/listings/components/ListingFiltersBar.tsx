import {
  Button,
  Flex,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
} from '@chakra-ui/react';
import { useEffect, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { HiOutlineMagnifyingGlass } from 'react-icons/hi2';
import { LISTING_CONDITIONS, SKI_TAGS } from '@/config/constants';
import { useTagLabel } from '@/features/listings/hooks/useTagLabel';
import type { ListingFilters } from '@/features/listings/types/listings.types';

/** How long typing has to pause before the search runs. */
const SEARCH_DEBOUNCE_MS = 300;

type ListingFiltersBarProps = {
  value: ListingFilters;
  onChange: (filters: ListingFilters) => void;
};

/**
 * Search box (applies as you type) + condition, ski tag and price range
 * (apply on submit). All of them combine.
 */
export function ListingFiltersBar({ value, onChange }: ListingFiltersBarProps) {
  const { t } = useTranslation();
  const tagLabel = useTagLabel();
  const { register, handleSubmit, reset } = useForm<ListingFilters>({ values: value });
  const hasFilters = Boolean(value.condition || value.tag || value.price_min || value.price_max);

  const [search, setSearch] = useState(value.q ?? '');
  // The last search we pushed into the URL: lets the URL win when it changes
  // from elsewhere (back button, a shared link) without clobbering text the
  // user is still typing while their previous search loads.
  const lastSubmittedSearch = useRef(value.q ?? '');

  useEffect(() => {
    const urlSearch = value.q ?? '';
    if (urlSearch !== lastSubmittedSearch.current) {
      lastSubmittedSearch.current = urlSearch;
      setSearch(urlSearch);
    }
  }, [value.q]);

  useEffect(() => {
    const next = search.trim();
    if (next === lastSubmittedSearch.current) return;
    const timeout = setTimeout(() => {
      lastSubmittedSearch.current = next;
      onChange({ ...value, q: next });
    }, SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timeout);
  }, [search, value, onChange]);

  return (
    <Flex
      as="form"
      onSubmit={handleSubmit((filters) => onChange({ ...filters, q: search.trim() }))}
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
      <FormControl w="full">
        <FormLabel srOnly>{t('listings.search')}</FormLabel>
        <InputGroup>
          <InputLeftElement pointerEvents="none" color="brand.muted">
            <HiOutlineMagnifyingGlass />
          </InputLeftElement>
          <Input
            type="search"
            enterKeyHint="search"
            maxLength={100}
            placeholder={t('listings.searchPlaceholder')}
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </InputGroup>
      </FormControl>
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
      <FormControl w={{ base: 'full', sm: '200px' }}>
        <FormLabel>{t('listings.tag')}</FormLabel>
        <Select size="sm" {...register('tag')}>
          <option value="">{t('listings.anyTag')}</option>
          {SKI_TAGS.map((tag) => (
            <option key={tag} value={tag}>
              {tagLabel(tag)}
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
              reset({ condition: '', tag: '', price_min: '', price_max: '' });
              // "Clear" resets the filters; the search box has its own clear.
              onChange({ q: search.trim() });
            }}
          >
            {t('listings.clearFilters')}
          </Button>
        ) : null}
      </Flex>
    </Flex>
  );
}
