import {
  Alert,
  AlertIcon,
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  Link,
  Stack,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { Trans, useTranslation } from 'react-i18next';
import { Link as RouterLink, useLocation, useNavigate, type Location } from 'react-router-dom';
import { ROUTES } from '@/config/constants';
import { AuthCard } from '@/features/auth/components/AuthCard';
import { useLogin } from '@/features/auth/hooks/useAuth';
import type { LoginRequest } from '@/features/auth/types/auth.types';
import { authRules } from '@/features/auth/validation/auth.validation';
import { ApiError } from '@/types/api';

export function LoginScreen() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const login = useLogin();
  const rules = authRules(t);

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<LoginRequest>({ defaultValues: { email: '', password: '' } });

  const onSubmit = handleSubmit((values) => {
    login.mutate(
      { email: values.email.trim(), password: values.password },
      {
        onSuccess: () => {
          const from = (location.state as { from?: Location } | null)?.from;
          navigate(from ? `${from.pathname}${from.search}` : ROUTES.home, { replace: true });
        },
        onError: (error) =>
          setError('root', {
            message:
              error instanceof ApiError && error.status === 401
                ? t('auth.invalidCredentials')
                : t('auth.loginFailed'),
          }),
      },
    );
  });

  return (
    <AuthCard
      title={t('auth.loginTitle')}
      intro={t('auth.loginIntro')}
      footer={
        <Trans
          i18nKey="auth.noAccount"
          components={{ cta: <Link as={RouterLink} to={ROUTES.register} /> }}
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

        <FormControl isInvalid={Boolean(errors.email)}>
          <FormLabel>{t('auth.email')}</FormLabel>
          <Input type="email" autoComplete="email" {...register('email', rules.email)} />
          <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
        </FormControl>

        <FormControl isInvalid={Boolean(errors.password)}>
          <FormLabel>{t('auth.password')}</FormLabel>
          <Input
            type="password"
            autoComplete="current-password"
            {...register('password', { required: t('validation.required') })}
          />
          <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
        </FormControl>

        <Button type="submit" size="lg" isLoading={login.isPending}>
          {t('auth.signIn')}
        </Button>
      </Stack>
    </AuthCard>
  );
}
