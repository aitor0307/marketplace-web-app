import { useTranslation } from 'react-i18next';
import { SKI_TAGS } from '@/config/constants';

/** Predefined ski tags are stored as slugs and shown translated; custom tags as typed. */
export function useTagLabel() {
  const { t } = useTranslation();
  return (tag: string) =>
    (SKI_TAGS as readonly string[]).includes(tag) ? t(`skiTags.${tag}`) : tag;
}
