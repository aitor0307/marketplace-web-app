import { Box, type BoxProps } from '@chakra-ui/react';
import type { ReactNode } from 'react';

export type CardProps = BoxProps & {
  children: ReactNode;
};

export function Card({ children, ...props }: CardProps) {
  return (
    <Box
      bg="brand.surface"
      borderRadius="2xl"
      p={5}
      borderWidth="1px"
      borderColor="brand.border"
      boxShadow="card"
      {...props}
    >
      {children}
    </Box>
  );
}
