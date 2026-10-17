import { Flex, Text, VStack } from '@chakra-ui/react';
import type { ReactNode } from 'react';
import type { IconType } from 'react-icons';

type EmptyStateCardProps = {
  icon?: IconType;
  title: string;
  description?: string;
  action?: ReactNode;
};

export function EmptyStateCard({ icon: Icon, title, description, action }: EmptyStateCardProps) {
  return (
    <VStack
      spacing={3}
      py={12}
      px={6}
      bg="brand.surface"
      borderRadius="2xl"
      borderWidth="1px"
      borderColor="brand.border"
      textAlign="center"
    >
      {Icon ? (
        <Flex
          w={14}
          h={14}
          align="center"
          justify="center"
          borderRadius="xl"
          bg="accent.50"
          color="accent.700"
        >
          <Icon size={26} />
        </Flex>
      ) : null}
      <Text fontSize="md" fontWeight={700} color="brand.heading">
        {title}
      </Text>
      {description ? (
        <Text fontSize="sm" color="brand.muted" maxW="sm" lineHeight="1.6">
          {description}
        </Text>
      ) : null}
      {action}
    </VStack>
  );
}
