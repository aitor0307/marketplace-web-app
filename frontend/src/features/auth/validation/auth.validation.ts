import type { TFunction } from 'i18next';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** react-hook-form rule sets mirroring RegisterPayload's constraints. */
export function authRules(t: TFunction) {
  return {
    name: {
      required: t('validation.required'),
      maxLength: { value: 30, message: t('validation.maxLength', { count: 30 }) },
    },
    email: {
      required: t('validation.required'),
      pattern: { value: EMAIL_RE, message: t('validation.email') },
    },
    password: {
      required: t('validation.required'),
      minLength: { value: 6, message: t('validation.minLength', { count: 6 }) },
    },
    state: { required: t('validation.required') },
    city: {
      required: t('validation.required'),
      maxLength: { value: 50, message: t('validation.maxLength', { count: 50 }) },
    },
  };
}
