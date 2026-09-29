import {
  Alert,
  AlertIcon,
  Box,
  Button,
  FormControl,
  FormErrorMessage,
  FormHelperText,
  FormLabel,
  Image,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  SimpleGrid,
  Stack,
  Textarea,
  useToast,
} from '@chakra-ui/react';
import { useEffect, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/Card';
import { Page } from '@/components/Page';
import { LISTING_CONDITIONS, paths, type ListingCondition } from '@/config/constants';
import { useCreateListing } from '@/features/listings/hooks/useListings';
import { applyApiError } from '@/utils/forms';

type NewListingFormValues = {
  title: string;
  body: string;
  condition: ListingCondition;
  price: string;
  tags: string;
  image: FileList;
};

const FIELDS = ['title', 'body', 'condition', 'price', 'tags'] as const;

/** "red, fast ,bike" → ["red", "fast", "bike"], like TagListField in app/forms.py. */
function parseTags(raw: string): string[] {
  return raw
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean);
}

export function NewListingScreen() {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();
  const createListing = useCreateListing();

  const {
    register,
    handleSubmit,
    setError,
    watch,
    formState: { errors },
  } = useForm<NewListingFormValues>({
    defaultValues: { title: '', body: '', condition: 'New', price: '', tags: '' },
  });

  const imageFiles = watch('image');
  const previewUrl = useMemo(
    () => (imageFiles?.[0] ? URL.createObjectURL(imageFiles[0]) : undefined),
    [imageFiles],
  );
  useEffect(
    () => () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    },
    [previewUrl],
  );

  const onSubmit = handleSubmit((values) => {
    createListing.mutate(
      {
        title: values.title.trim(),
        body: values.body.trim(),
        condition: values.condition,
        price: Number(values.price),
        tags: parseTags(values.tags),
        image: values.image[0],
      },
      {
        onSuccess: (listing) => {
          toast({ status: 'success', title: t('newListing.created') });
          navigate(paths.listing(listing.id), { replace: true });
        },
        onError: (error) => applyApiError(error, setError, t('newListing.failed'), FIELDS),
      },
    );
  });

  return (
    <Page title={t('newListing.title')} subtitle={t('newListing.subtitle')} narrow>
      <Card p={{ base: 5, md: 7 }}>
        <Stack as="form" spacing={5} onSubmit={onSubmit} noValidate>
          {errors.root?.message ? (
            <Alert status="error" borderRadius="12px" fontSize="sm">
              <AlertIcon />
              {errors.root.message}
            </Alert>
          ) : null}

          <FormControl isInvalid={Boolean(errors.image)}>
            <FormLabel>{t('newListing.image')}</FormLabel>
            {previewUrl ? (
              <Box
                mb={3}
                borderRadius="xl"
                overflow="hidden"
                borderWidth="1px"
                borderColor="brand.border"
              >
                <Image src={previewUrl} alt="" maxH="240px" w="full" objectFit="cover" />
              </Box>
            ) : null}
            <Input
              type="file"
              accept="image/*"
              p={1.5}
              {...register('image', {
                validate: (files) => (files && files.length > 0) || t('newListing.imageRequired'),
              })}
            />
            <FormErrorMessage>{errors.image?.message}</FormErrorMessage>
          </FormControl>

          <FormControl isInvalid={Boolean(errors.title)}>
            <FormLabel>{t('newListing.listingTitle')}</FormLabel>
            <Input
              {...register('title', {
                required: t('validation.required'),
                maxLength: { value: 140, message: t('validation.maxLength', { count: 140 }) },
              })}
            />
            <FormErrorMessage>{errors.title?.message}</FormErrorMessage>
          </FormControl>

          <FormControl isInvalid={Boolean(errors.body)}>
            <FormLabel>{t('newListing.details')}</FormLabel>
            <Textarea
              rows={5}
              {...register('body', {
                required: t('validation.required'),
                maxLength: { value: 1000, message: t('validation.maxLength', { count: 1000 }) },
              })}
            />
            <FormErrorMessage>{errors.body?.message}</FormErrorMessage>
          </FormControl>

          <SimpleGrid columns={{ base: 1, sm: 2 }} spacing={4}>
            <FormControl isInvalid={Boolean(errors.price)}>
              <FormLabel>{t('newListing.price')}</FormLabel>
              <InputGroup>
                <InputLeftElement pointerEvents="none" color="brand.muted">
                  €
                </InputLeftElement>
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  inputMode="decimal"
                  {...register('price', {
                    required: t('validation.required'),
                    validate: (value) => Number(value) > 0 || t('validation.positive'),
                  })}
                />
              </InputGroup>
              <FormErrorMessage>{errors.price?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={Boolean(errors.condition)}>
              <FormLabel>{t('listings.condition')}</FormLabel>
              <Select {...register('condition')}>
                {LISTING_CONDITIONS.map((condition) => (
                  <option key={condition} value={condition}>
                    {t(`conditions.${condition}`)}
                  </option>
                ))}
              </Select>
              <FormErrorMessage>{errors.condition?.message}</FormErrorMessage>
            </FormControl>
          </SimpleGrid>

          <FormControl isInvalid={Boolean(errors.tags)}>
            <FormLabel>{t('newListing.tags')}</FormLabel>
            <Input placeholder={t('newListing.tagsPlaceholder')} {...register('tags')} />
            <FormHelperText fontSize="xs">{t('newListing.tagsHelp')}</FormHelperText>
            <FormErrorMessage>{errors.tags?.message}</FormErrorMessage>
          </FormControl>

          <Button type="submit" size="lg" isLoading={createListing.isPending}>
            {t('newListing.submit')}
          </Button>
        </Stack>
      </Card>
    </Page>
  );
}
