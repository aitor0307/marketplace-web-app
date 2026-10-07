import { Box, type BoxProps } from '@chakra-ui/react';
import type { ReactNode } from 'react';

type StaggerProps = BoxProps & {
  children: ReactNode;
  step?: number;
};

/** Staggered fade-rise on direct children. */
export function Stagger({ children, step = 45, ...props }: StaggerProps) {
  return (
    <Box
      sx={{
        '& > *': {
          opacity: 0,
          animation: 'fadeRise 320ms ease-out forwards',
        },
        ...Object.fromEntries(
          Array.from({ length: 12 }, (_, i) => [
            `& > *:nth-of-type(${i + 1})`,
            { animationDelay: `${i * step}ms` },
          ]),
        ),
      }}
      {...props}
    >
      {children}
    </Box>
  );
}
