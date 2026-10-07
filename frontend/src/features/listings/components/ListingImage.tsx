import { Box, Center, Image, type BoxProps } from '@chakra-ui/react';
import { HiOutlinePhoto } from 'react-icons/hi2';
import { resolveAssetUrl } from '@/config/env';

type ListingImageProps = BoxProps & {
  src: string | null;
  alt: string;
};

export function ListingImage({ src, alt, ...props }: ListingImageProps) {
  const url = resolveAssetUrl(src);
  const placeholder = (
    <Center h="full" color="brand.muted">
      <HiOutlinePhoto size={32} />
    </Center>
  );
  return (
    <Box bg="brand.surfaceMuted" overflow="hidden" {...props}>
      {url ? (
        // fallback also covers files missing on disk, not just null image_url
        <Image src={url} alt={alt} w="full" h="full" objectFit="cover" fallback={placeholder} />
      ) : (
        placeholder
      )}
    </Box>
  );
}
