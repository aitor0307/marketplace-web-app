import {
  Alert,
  AlertDescription,
  AlertIcon,
  AlertTitle,
  Badge,
  Box,
  Button,
  FormControl,
  FormErrorMessage,
  FormHelperText,
  FormLabel,
  IconButton,
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
import { useEffect, useMemo, type ChangeEvent } from 'react';
import { useController, useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { HiOutlinePhoto, HiXMark } from 'react-icons/hi2';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/Card';
import { Page } from '@/components/Page';
import {
  LISTING_CONDITIONS,
  MAX_LISTING_IMAGES,
  paths,
  type ListingCondition,
} from '@/config/constants';
import { useRefreshPendingUser } from '@/features/auth';
import { useCreateListing } from '@/features/listings/hooks/useListings';
import { applyApiError } from '@/utils/forms';

type NewListingFormValues = {
  title: string;
  body: string;
  condition: ListingCondition;
  price: string;
  tags: string;
  images: File[];
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
  const isPending = useRefreshPendingUser();

  const {
    register,
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<NewListingFormValues>({
    defaultValues: { title: '', body: '', condition: 'New', price: '', tags: '', images: [] },
  });

  // Not a registered <input>: picking files again appends to the selection
  // instead of replacing it, and each picked file can be removed on its own.
  const { field: imagesField } = useController({
    name: 'images',
    control,
    rules: {
      validate: (files) => {
        if (files.length === 0) return t('newListing.imageRequired');
        if (files.length > MAX_LISTING_IMAGES)
          return t('newListing.imagesMax', { count: MAX_LISTING_IMAGES });
        return true;
      },
    },
  });
  const imageFiles = imagesField.value;

  const previewUrls = useMemo(
    () => imageFiles.map((file) => URL.createObjectURL(file)),
    [imageFiles],
  );
  useEffect(() => () => previewUrls.forEach((url) => URL.revokeObjectURL(url)), [previewUrls]);

  const onAddImages = (event: ChangeEvent<HTMLInputElement>) => {
    const picked = Array.from(event.target.files ?? []);
    // Clear it so picking the same file again still fires onChange.
    event.target.value = '';
    if (picked.length) imagesField.onChange([...imageFiles, ...picked]);
  };
  const onRemoveImage = (index: number) =>
    imagesField.onChange(imageFiles.filter((_file, i) => i !== index));

  const onSubmit = handleSubmit((values) => {
    createListing.mutate(
      {
        title: values.title.trim(),
        body: values.body.trim(),
        condition: values.condition,
        price: Number(values.price),
        tags: parseTags(values.tags),
        images: values.images,
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

  if (isPending) {
    return (
      <Page title={t('newListing.title')} narrow>
        <Alert status="info" borderRadius="12px" alignItems="flex-start">
          <AlertIcon />
          <Box>
            <AlertTitle>{t('newListing.pendingTitle')}</AlertTitle>
            <AlertDescription fontSize="sm">{t('newListing.pendingDesc')}</AlertDescription>
          </Box>
        </Alert>
      </Page>
    );
  }

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

          <FormControl isInvalid={Boolean(errors.images)}>
            <FormLabel>{t('newListing.image')}</FormLabel>
            {previewUrls.length ? (
              <SimpleGrid columns={{ base: 3, sm: 4 }} spacing={3} mb={3}>
                {previewUrls.map((url, index) => (
                  <Box
                    key={url}
                    position="relative"
                    borderRadius="xl"
                    overflow="hidden"
                    borderWidth="1px"
                    borderColor="brand.border"
                  >
                    <Image src={url} alt="" w="full" h="96px" objectFit="cover" />
                    {index === 0 ? (
                      <Badge
                        position="absolute"
                        bottom={1}
                        left={1}
                        bg="brand.primary"
                        color="white"
                        borderRadius="6px"
                        textTransform="none"
                      >
                        {t('newListing.cover')}
                      </Badge>
                    ) : null}
                    <IconButton
                      aria-label={t('newListing.removeImage')}
                      icon={<HiXMark />}
                      size="xs"
                      isRound
                      position="absolute"
                      top={1}
                      right={1}
                      onClick={() => onRemoveImage(index)}
                    />
                  </Box>
                ))}
              </SimpleGrid>
            ) : null}
            <Button
              as="label"
              variant="outline"
              leftIcon={<HiOutlinePhoto />}
              cursor="pointer"
              isDisabled={imageFiles.length >= MAX_LISTING_IMAGES}
            >
              {t('newListing.addImages')}
              <Input
                ref={imagesField.ref}
                type="file"
                accept="image/*"
                multiple
                display="none"
                onChange={onAddImages}
                onBlur={imagesField.onBlur}
                isDisabled={imageFiles.length >= MAX_LISTING_IMAGES}
              />
            </Button>
            <FormHelperText fontSize="xs">
              {t('newListing.imagesHelp', { count: MAX_LISTING_IMAGES })}
            </FormHelperText>
            <FormErrorMessage>{errors.images?.message}</FormErrorMessage>
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
