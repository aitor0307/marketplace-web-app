import { Avatar, HStack, Link, Text } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { paths } from '@/config/constants';
import type { UserSummary } from '@/types/models';

type UserChipProps = {
  user: UserSummary;
  size?: 'xs' | 'sm' | 'md';
  showLocation?: boolean;
};

export function UserChip({ user, size = 'sm', showLocation = false }: UserChipProps) {
  return (
    <Link as={RouterLink} to={paths.user(user.id)} display="inline-flex" color="inherit">
      <HStack spacing={2} minW={0}>
        <Avatar size={size} name={user.name ?? undefined} src={user.avatar_url ?? undefined} />
        <Text fontSize="sm" fontWeight={600} color="brand.heading" noOfLines={1}>
          {user.name}
          {showLocation && (user.city || user.state) ? (
            <Text as="span" fontWeight={400} color="brand.muted">
              {' · '}
              {[user.city, user.state].filter(Boolean).join(', ')}
            </Text>
          ) : null}
        </Text>
      </HStack>
    </Link>
  );
}
