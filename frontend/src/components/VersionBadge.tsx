import { Text } from '@chakra-ui/react';
import { env } from '@/config/env';

/** The build's release (its deploy date) in the bottom-left corner, out of the way. */
export function VersionBadge() {
  return (
    <Text
      position="fixed"
      bottom={2}
      left={3}
      zIndex={10}
      fontSize="2xs"
      color="brand.muted"
      opacity={0.7}
      pointerEvents="none"
      userSelect="none"
      aria-hidden
    >
      v{env.release}
    </Text>
  );
}
