import {
  Alert,
  AlertIcon,
  Button,
  FormControl,
  FormErrorMessage,
  FormHelperText,
  FormLabel,
  IconButton,
  Input,
  InputGroup,
  InputRightElement,
  Link,
  Select,
  SimpleGrid,
  Stack,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { Trans, useTranslation } from 'react-i18next';
import { HiOutlineSparkles } from 'react-icons/hi2';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { ROUTES, SPAIN_PROVINCES } from '@/config/constants';
import { AuthCard } from '@/features/auth/components/AuthCard';
import { useRegister } from '@/features/auth/hooks/useAuth';
import type { RegisterRequest } from '@/features/auth/types/auth.types';
import { authRules } from '@/features/auth/validation/auth.validation';
import { ApiError } from '@/types/api';
import { applyApiError } from '@/utils/forms';
import { randomUsername } from '@/utils/username';

type RegisterFormValues = RegisterRequest & { password2: string };

const FIELDS = ['name', 'email', 'password', 'state', 'city', 'registration_key'] as const;

export function RegisterScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const registerUser = useRegister();
  const rules = authRules(t);

  const {
    register,
    handleSubmit,
    setError,
    setValue,
    getValues,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    defaultValues: {
      name: '',
      email: '',
      password: '',
      password2: '',
      state: '',
      city: '',
      registration_key: '',
    },
  });

  const onSubmit = handleSubmit(({ password2: _password2, ...values }) => {
    registerUser.mutate(
      {
        ...values,
        name: values.name.trim(),
        email: values.email.trim(),
        city: values.city.trim(),
        registration_key: values.registration_key?.trim() || undefined,
      },
      {
        // A pending account's popup is shown by PendingApprovalDialog (MainLayout).
        onSuccess: () => navigate(ROUTES.home, { replace: true }),
        onError: (error) => {
          if (error instanceof ApiError && error.status === 409) {
            setError('email', { message: t('auth.emailTaken') });
            return;
          }
          applyApiError(error, setError, t('auth.registerFailed'), FIELDS);
        },
      },
    );
  });

  return (
    <AuthCard
      title={t('auth.registerTitle')}
      intro={t('auth.registerIntro')}
      footer={
        <Trans
          i18nKey="auth.haveAccount"
          components={{ cta: <Link as={RouterLink} to={ROUTES.login} /> }}
        />
      }
    >
      <Stack as="form" spacing={5} onSubmit={onSubmit} noValidate>
        {errors.root?.message ? (
          <Alert status="error" borderRadius="12px" fontSize="sm">
            <AlertIcon />
            {errors.root.message}
          </Alert>
        ) : null}

        <FormControl isInvalid={Boolean(errors.name)}>
          <FormLabel>{t('auth.name')}</FormLabel>
          <InputGroup>
            <Input autoComplete="nickname" pr={10} {...register('name', rules.name)} />
            <InputRightElement>
              <IconButton
                aria-label={t('auth.generateName')}
                title={t('auth.generateName')}
                icon={<HiOutlineSparkles />}
                size="sm"
                variant="ghost"
                onClick={() =>
                  setValue('name', randomUsername(i18n.language), {
                    shouldValidate: true,
                    shouldDirty: true,
                  })
                }
              />
            </InputRightElement>
          </InputGroup>
          <FormHelperText fontSize="xs">{t('auth.nameHelp')}</FormHelperText>
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
              {SPAIN_PROVINCES.map((state) => (
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

        <FormControl isInvalid={Boolean(errors.password)}>
          <FormLabel>{t('auth.password')}</FormLabel>
          <Input
            type="password"
            autoComplete="new-password"
            {...register('password', rules.password)}
          />
          <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
        </FormControl>

        <FormControl isInvalid={Boolean(errors.password2)}>
          <FormLabel>{t('auth.repeatPassword')}</FormLabel>
          <Input
            type="password"
            autoComplete="new-password"
            {...register('password2', {
              required: t('validation.required'),
              validate: (value) =>
                value === getValues('password') || t('validation.passwordMismatch'),
            })}
          />
          <FormErrorMessage>{errors.password2?.message}</FormErrorMessage>
        </FormControl>

        <FormControl isInvalid={Boolean(errors.registration_key)}>
          <FormLabel>{t('auth.registrationKey')}</FormLabel>
          <Input autoComplete="off" {...register('registration_key')} />
          <FormHelperText fontSize="xs">{t('auth.registrationKeyHelp')}</FormHelperText>
          <FormErrorMessage>{errors.registration_key?.message}</FormErrorMessage>
        </FormControl>

        <Button type="submit" size="lg" isLoading={registerUser.isPending}>
          {t('auth.createAccount')}
        </Button>
      </Stack>
    </AuthCard>
  );
}
