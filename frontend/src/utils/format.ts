import i18n from '@/i18n';
import { PRICE_CURRENCY } from '@/config/constants';

export function formatPrice(value: number): string {
  return new Intl.NumberFormat(i18n.language, {
    style: 'currency',
    currency: PRICE_CURRENCY,
  }).format(value);
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat(i18n.language, { dateStyle: 'long', timeStyle: 'short' }).format(
    new Date(value),
  );
}

const RELATIVE_STEPS: [Intl.RelativeTimeFormatUnit, number][] = [
  ['year', 31_536_000],
  ['month', 2_592_000],
  ['week', 604_800],
  ['day', 86_400],
  ['hour', 3_600],
  ['minute', 60],
];

/** "3 days ago" — replaces flask-moment's fromNow() used by the Jinja views. */
export function formatRelativeTime(value: string): string {
  const seconds = Math.round((new Date(value).getTime() - Date.now()) / 1000);
  const rtf = new Intl.RelativeTimeFormat(i18n.language, { numeric: 'auto' });
  for (const [unit, size] of RELATIVE_STEPS) {
    if (Math.abs(seconds) >= size) return rtf.format(Math.round(seconds / size), unit);
  }
  return rtf.format(seconds, 'second');
}
