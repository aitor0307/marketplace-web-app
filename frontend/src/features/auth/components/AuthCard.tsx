import { Box, Flex, Heading, Image, Text, VStack } from '@chakra-ui/react';
import type { ReactNode } from 'react';

type AuthCardProps = {
  title: string;
  intro: string;
  children: ReactNode;
  footer: ReactNode;
};

export function AuthCard({ title, intro, children, footer }: AuthCardProps) {
  return (
    <Flex justify="center" px={4} py={{ base: 8, md: 16 }}>
      <Box w="full" maxW="440px" opacity={0} animation="fadeRise 360ms ease-out forwards">
        <VStack spacing={3} textAlign="center" mb={8}>
          <Flex
            w="56px"
            h="56px"
            align="center"
            justify="center"
            borderRadius="18px"
            bg="brand.ink"
          >
            <Image src="/logo.png" alt="" boxSize="30px" objectFit="contain" />
          </Flex>
          <Heading as="h1" size="lg">
            {title}
          </Heading>
          <Text fontSize="sm" color="brand.muted" maxW="340px">
            {intro}
          </Text>
        </VStack>
        <Box
          bg="brand.surface"
          borderRadius="2xl"
          borderWidth="1px"
          borderColor="brand.border"
          boxShadow="card"
          p={{ base: 6, sm: 8 }}
        >
          {children}
        </Box>
        <Text mt={6} fontSize="sm" color="brand.muted" textAlign="center">
          {footer}
        </Text>
      </Box>
    </Flex>
  );
}
