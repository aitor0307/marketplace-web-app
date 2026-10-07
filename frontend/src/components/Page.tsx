import { Box, Flex, Heading, Text, type BoxProps } from '@chakra-ui/react';
import type { ReactNode } from 'react';

export type PageProps = BoxProps & {
  title?: string;
  subtitle?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  /** Narrow column for forms. */
  narrow?: boolean;
};

/** Standard page frame: title row + content column. Replaces base.html's title block. */
export function Page({ title, subtitle, actions, children, narrow = false, ...props }: PageProps) {
  return (
    <Box
      as="main"
      w="full"
      maxW={narrow ? '560px' : '1200px'}
      mx="auto"
      px={{ base: 4, md: 8 }}
      py={{ base: 6, md: 10 }}
      {...props}
    >
      {title ? (
        <Flex
          align={{ base: 'flex-start', md: 'center' }}
          justify="space-between"
          direction={{ base: 'column', md: 'row' }}
          gap={3}
          mb={6}
          opacity={0}
          animation="fadeRise 320ms ease-out forwards"
        >
          <Box minW={0}>
            <Heading as="h1" size="lg">
              {title}
            </Heading>
            {subtitle ? (
              <Text mt={1} fontSize="sm" color="brand.muted">
                {subtitle}
              </Text>
            ) : null}
          </Box>
          {actions}
        </Flex>
      ) : null}
      {children}
    </Box>
  );
}
