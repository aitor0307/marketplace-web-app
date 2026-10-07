import { extendTheme, type ThemeConfig } from '@chakra-ui/react';

const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: false,
};

/** Orange scale built around the reference brand color #E5702B (500). */
const orange = {
  50: '#fdf1ea',
  100: '#fadcc9',
  200: '#f5bf9e',
  300: '#f0a172',
  400: '#ea8750',
  500: '#e5702b',
  600: '#c95d1c',
  700: '#a44b17',
  800: '#7e3a12',
  900: '#58280c',
};

/** Brand tokens: #E5702B as the brand color, warm dark ink for text. */
const colors = {
  brand: {
    primary: '#e5702b',
    ink: '#2d2420',
    accent: '#e5702b',
    accentSoft: '#fdf1ea',
    heading: '#2d2420',
    text: '#3d332d',
    muted: '#857870',
    pageBg: '#faf7f5',
    surface: '#ffffff',
    surfaceMuted: '#f5efeb',
    border: '#ece2db',
    danger: '#c53030',
  },
  primary: orange,
  accent: orange,
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
  card: '0 1px 2px rgba(45, 36, 32, 0.06)',
  cardHover: '0 8px 24px rgba(45, 36, 32, 0.10)',
  focus: '0 0 0 3px rgba(229, 112, 43, 0.35)',
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
      // #E5702B on white is too light for body-size link text; use a deeper shade.
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
