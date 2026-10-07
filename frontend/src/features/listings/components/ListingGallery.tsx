import { Box, HStack, type BoxProps } from '@chakra-ui/react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ListingImage } from '@/features/listings/components/ListingImage';

type ListingGalleryProps = {
  srcs: string[];
  alt: string;
  h: BoxProps['h'];
};

/** Main image plus a thumbnail strip; the strip only shows with 2+ images. */
export function ListingGallery({ srcs, alt, h }: ListingGalleryProps) {
  const { t } = useTranslation();
  const [activeIndex, setActiveIndex] = useState(0);

  // A refetch may return fewer images than the index we were on.
  useEffect(() => {
    if (activeIndex >= srcs.length) setActiveIndex(0);
  }, [activeIndex, srcs.length]);

  return (
    <Box>
      <ListingImage src={srcs[activeIndex] ?? null} alt={alt} h={h} />
      {srcs.length > 1 ? (
        <HStack spacing={2} px={{ base: 5, md: 7 }} pt={4} overflowX="auto">
          {srcs.map((src, index) => (
            <Box
              key={src}
              as="button"
              type="button"
              flexShrink={0}
              borderRadius="lg"
              overflow="hidden"
              borderWidth="2px"
              borderColor={index === activeIndex ? 'brand.primary' : 'transparent'}
              opacity={index === activeIndex ? 1 : 0.7}
              _hover={{ opacity: 1 }}
              aria-label={t('listings.showImage', { index: index + 1 })}
              aria-current={index === activeIndex}
              onClick={() => setActiveIndex(index)}
            >
              <ListingImage src={src} alt="" w="72px" h="72px" />
            </Box>
          ))}
        </HStack>
      ) : null}
    </Box>
  );
}
