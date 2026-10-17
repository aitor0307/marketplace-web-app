import {
  Alert,
  AlertIcon,
  Avatar,
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  HStack,
  Input,
  Select,
  SimpleGrid,
  Stack,
  Text,
  useToast,
} from '@chakra-ui/react';
import { useRef, type ChangeEvent } from 'react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/Card';
import { Page } from '@/components/Page';
import { SPAIN_PROVINCES, paths } from '@/config/constants';
import { resolveAssetUrl } from '@/config/env';
import { authRules } from '@/features/auth/validation/auth.validation';
import { useUpdateAvatar, useUpdateProfile } from '@/features/users/hooks/useUsers';
import { useSessionStore } from '@/store/sessionStore';
import { applyApiError } from '@/utils/forms';

type EditProfileFormValues = {
  name: string;
  email: string;
  state: string;
  city: string;
};

const FIELDS = ['name', 'email', 'state', 'city'] as const;

/** Mirror MAX_AVATAR_BYTES / AVATAR_EXTENSIONS in app/config/base.py. */
const MAX_AVATAR_BYTES = 5 * 1024 * 1024;
const AVATAR_ACCEPT = 'image/jpeg,image/png,image/gif,image/webp';

export function EditProfileScreen() {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();
  // RequireAuth guarantees a user here.
  const user = useSessionStore((s) => s.user)!;
  const updateProfile = useUpdateProfile();
  const updateAvatar = useUpdateAvatar();
  const avatarInput = useRef<HTMLInputElement>(null);
  const rules = authRules(t);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isDirty },
  } = useForm<EditProfileFormValues>({
    defaultValues: {
      name: user.name ?? '',
      email: user.email ?? '',
      state: user.state ?? '',
      city: user.city ?? '',
    },
  });

  const onSubmit = handleSubmit((values) => {
    updateProfile.mutate(
      {
        name: values.name.trim(),
        email: values.email.trim(),
        state: values.state,
        city: values.city.trim(),
      },
      {
        onSuccess: (updated) => {
          toast({ status: 'success', title: t('profile.updated') });
          navigate(paths.user(updated.id));
        },
        onError: (error) => applyApiError(error, setError, t('profile.updateFailed'), FIELDS),
      },
    );
  });

  // The picture is saved on its own as soon as it's picked, not with the form.
  const onAvatarPicked = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = ''; // so picking the same file again still fires
    if (!file) return;
    if (file.size > MAX_AVATAR_BYTES) {
      toast({ status: 'error', title: t('profile.photoHint') });
      return;
    }
    updateAvatar.mutate(file, {
      onSuccess: () => toast({ status: 'success', title: t('profile.photoUpdated') }),
      onError: (error) =>
        toast({ status: 'error', title: t('profile.photoFailed'), description: error.message }),
    });
  };

  const onAvatarRemoved = () =>
    updateAvatar.mutate(null, {
      onSuccess: () => toast({ status: 'success', title: t('profile.photoRemoved') }),
      onError: () => toast({ status: 'error', title: t('profile.photoFailed') }),
    });

  // Keep a stored state that's not in the list selectable instead of silently changing it.
  const stateOptions =
    user.state && !(SPAIN_PROVINCES as readonly string[]).includes(user.state)
      ? [user.state, ...SPAIN_PROVINCES]
      : SPAIN_PROVINCES;

  return (
    <Page title={t('profile.editTitle')} narrow>
      <Card p={{ base: 5, md: 7 }}>
        <Stack as="form" spacing={5} onSubmit={onSubmit} noValidate>
          {errors.root?.message ? (
            <Alert status="error" borderRadius="12px" fontSize="sm">
              <AlertIcon />
              {errors.root.message}
            </Alert>
          ) : null}

          <FormControl>
            <FormLabel>{t('profile.photo')}</FormLabel>
            <HStack spacing={4} align="center">
              <Avatar
                size="xl"
                name={user.name ?? undefined}
                src={resolveAssetUrl(user.avatar_url)}
              />
              <Stack spacing={2}>
                <HStack spacing={2} wrap="wrap">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => avatarInput.current?.click()}
                    isLoading={updateAvatar.isPending}
                  >
                    {t('profile.changePhoto')}
                  </Button>
                  {user.avatar_src ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={onAvatarRemoved}
                      isDisabled={updateAvatar.isPending}
                    >
                      {t('profile.removePhoto')}
                    </Button>
                  ) : null}
                </HStack>
                <Text fontSize="xs" color="brand.muted">
                  {t('profile.photoHint')}
                </Text>
              </Stack>
              <input
                ref={avatarInput}
                type="file"
                accept={AVATAR_ACCEPT}
                hidden
                onChange={onAvatarPicked}
              />
            </HStack>
          </FormControl>

          <FormControl isInvalid={Boolean(errors.name)}>
            <FormLabel>{t('auth.name')}</FormLabel>
            <Input autoComplete="name" {...register('name', rules.name)} />
            <FormErrorMessage>{errors.name?.message}</FormErrorMessage>
          </FormControl>

          <FormControl isInvalid={Boolean(errors.email)}>
            <FormLabel>{t('auth.email')}</FormLabel>
            <Input type="email" autoComplete="email" {...register('email', rules.email)} />
            <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
          </FormControl>

          <SimpleGrid columns={{ base: 1, sm: 2 }} spacing={4}>
            <FormControl isInvalid={Boolean(errors.state)}>
              <FormLabel>{t('auth.state')}</FormLabel>
              <Select placeholder={t('auth.selectProvince')} {...register('state', rules.state)}>
                {stateOptions.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </Select>
              <FormErrorMessage>{errors.state?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={Boolean(errors.city)}>
              <FormLabel>{t('auth.city')}</FormLabel>
              <Input autoComplete="address-level2" {...register('city', rules.city)} />
              <FormErrorMessage>{errors.city?.message}</FormErrorMessage>
            </FormControl>
          </SimpleGrid>

          <HStack justify="flex-end" spacing={2} pt={2}>
            <Button variant="ghost" onClick={() => navigate(-1)}>
              {t('common.cancel')}
            </Button>
            <Button type="submit" isLoading={updateProfile.isPending} isDisabled={!isDirty}>
              {t('common.save')}
            </Button>
          </HStack>
        </Stack>
      </Card>
    </Page>
  );
}
