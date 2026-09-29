import {
  Alert,
  AlertIcon,
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  HStack,
  Input,
  Select,
  SimpleGrid,
  Stack,
  useToast,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/Card';
import { Page } from '@/components/Page';
import { STATE_OPTIONS, paths } from '@/config/constants';
import { authRules } from '@/features/auth/validation/auth.validation';
import { useUpdateProfile } from '@/features/users/hooks/useUsers';
import { useSessionStore } from '@/store/sessionStore';
import { applyApiError } from '@/utils/forms';

type EditProfileFormValues = {
  name: string;
  email: string;
  state: string;
  city: string;
};

const FIELDS = ['name', 'email', 'state', 'city'] as const;

export function EditProfileScreen() {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();
  // RequireAuth guarantees a user here.
  const user = useSessionStore((s) => s.user)!;
  const updateProfile = useUpdateProfile();
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
      state: user.state ?? STATE_OPTIONS[0],
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

  // Keep a stored state that's not in the list selectable instead of silently changing it.
  const stateOptions =
    user.state && !(STATE_OPTIONS as readonly string[]).includes(user.state)
      ? [user.state, ...STATE_OPTIONS]
      : STATE_OPTIONS;

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
              <Select {...register('state', rules.state)}>
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
