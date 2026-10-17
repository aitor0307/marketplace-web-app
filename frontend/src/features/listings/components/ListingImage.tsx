import { Box, Center, Image, type BoxProps } from '@chakra-ui/react';
import { HiOutlinePhoto } from 'react-icons/hi2';
import { resolveAssetUrl } from '@/config/env';

type ListingImageProps = BoxProps & {
  src: string | null;
  alt: string;
  /** `cover` crops to fill (cards, thumbnails); `contain` shows the whole image. */
  fit?: 'cover' | 'contain';
};

export function ListingImage({ src, alt, fit = 'cover', ...props }: ListingImageProps) {
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
        <Image src={url} alt={alt} w="full" h="full" objectFit={fit} fallback={placeholder} />
      ) : (
        placeholder
      )}
    </Box>
  );
}
