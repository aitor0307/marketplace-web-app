import { extendTheme, type ThemeConfig } from '@chakra-ui/react';

const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: false,
};

/** Indigo scale; 500 is the primary color. */
const indigo = {
  50: '#eef2ff',
  100: '#e0e7ff',
  200: '#c7d2fe',
  300: '#a5b4fc',
  400: '#6366f1',
  500: '#4f46e5',
  600: '#4338ca',
  700: '#3730a3',
  800: '#312e81',
  900: '#1e1b4b',
};

/** Theme tokens: indigo as the primary color, slate greys for text and surfaces. */
const colors = {
  brand: {
    primary: '#4f46e5',
    ink: '#0f172a',
    accent: '#4f46e5',
    accentSoft: '#eef2ff',
    heading: '#0f172a',
    text: '#334155',
    muted: '#64748b',
    pageBg: '#f8fafc',
    surface: '#ffffff',
    surfaceMuted: '#f1f5f9',
    border: '#e2e8f0',
    danger: '#c53030',
  },
  primary: indigo,
  accent: indigo,
};

const fonts = {
  heading: `'DM Sans', sans-serif`,
  body: `'DM Sans', sans-serif`,
};

const radii = {
  xl: '1rem',
  '2xl': '1.25rem',
};

const shadows = {
  card: '0 1px 2px rgba(15, 23, 42, 0.06)',
  cardHover: '0 8px 24px rgba(15, 23, 42, 0.10)',
  focus: '0 0 0 3px rgba(79, 70, 229, 0.35)',
};

const styles = {
  global: {
    'html, body, #root': {
      minHeight: '100%',
    },
    body: {
      bg: 'brand.pageBg',
      color: 'brand.text',
      fontFamily: 'body',
      WebkitFontSmoothing: 'antialiased',
      MozOsxFontSmoothing: 'grayscale',
    },
    '::selection': {
      bg: 'accent.100',
      color: 'brand.heading',
    },
    '@keyframes fadeRise': {
      from: { opacity: 0, transform: 'translateY(8px)' },
      to: { opacity: 1, transform: 'translateY(0)' },
    },
  },
};

const fieldStyles = {
  bg: 'brand.surface',
  borderColor: 'brand.border',
  borderRadius: '12px',
  _hover: { borderColor: 'accent.500' },
  _focusVisible: { borderColor: 'accent.500', boxShadow: 'focus' },
};

const components = {
  Button: {
    baseStyle: {
      fontWeight: 600,
      borderRadius: '12px',
    },
    variants: {
      solid: {
        bg: 'brand.primary',
        color: 'white',
        _hover: { bg: 'primary.600', _disabled: { bg: 'brand.primary' } },
        _active: { bg: 'primary.700' },
      },
      accent: {
        bg: 'primary.50',
        color: 'primary.700',
        _hover: { bg: 'primary.100' },
        _active: { bg: 'primary.200' },
      },
      outline: {
        borderColor: 'brand.border',
        color: 'brand.ink',
        _hover: { bg: 'brand.surfaceMuted', borderColor: 'primary.400' },
      },
      ghost: {
        color: 'brand.ink',
        _hover: { bg: 'brand.surfaceMuted' },
      },
    },
    defaultProps: {
      variant: 'solid',
    },
  },
  Input: {
    variants: { outline: { field: fieldStyles } },
    defaultProps: { variant: 'outline' },
  },
  NumberInput: {
    variants: { outline: { field: fieldStyles } },
  },
  Select: {
    variants: { outline: { field: fieldStyles } },
  },
  Textarea: {
    variants: { outline: fieldStyles },
  },
  FormLabel: {
    baseStyle: {
      color: 'brand.heading',
      fontWeight: 500,
      fontSize: 'sm',
    },
  },
  Heading: {
    baseStyle: {
      color: 'brand.heading',
      letterSpacing: '-0.02em',
    },
  },
  Link: {
    baseStyle: {
      // A deeper shade than primary.500 reads better as body-size link text.
      color: 'primary.700',
      fontWeight: 500,
      _hover: { textDecoration: 'none', color: 'primary.800' },
    },
  },
};

export const theme = extendTheme({
  config,
  colors,
  fonts,
  radii,
  shadows,
  styles,
  components,
});

export type AppTheme = typeof theme;
