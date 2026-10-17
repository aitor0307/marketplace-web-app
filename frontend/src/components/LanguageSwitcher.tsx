import { Button, HStack } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';
import { LANGUAGES } from '@/config/constants';

export function LanguageSwitcher() {
  const { t, i18n } = useTranslation();

  return (
    <HStack
      spacing={0.5}
      p={0.5}
      borderRadius="10px"
      borderWidth="1px"
      borderColor="brand.border"
      aria-label={t('common.language')}
    >
      {LANGUAGES.map((code) => {
        const active = i18n.language === code;
        return (
          <Button
            key={code}
            size="xs"
            h="26px"
            minW="34px"
            borderRadius="8px"
            variant="ghost"
            fontWeight={active ? 700 : 500}
            bg={active ? 'primary.50' : 'transparent'}
            color={active ? 'primary.700' : 'brand.muted'}
            aria-pressed={active}
            onClick={() => void i18n.changeLanguage(code)}
          >
            {code.toUpperCase()}
          </Button>
        );
      })}
    </HStack>
  );
}
