import { Box, HStack, Icon, useDisclosure, type BoxProps } from '@chakra-ui/react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { HiOutlineArrowsPointingOut } from 'react-icons/hi2';
import { ImageLightbox } from '@/features/listings/components/ImageLightbox';
import { ListingImage } from '@/features/listings/components/ListingImage';

type ListingGalleryProps = {
  srcs: string[];
  alt: string;
  h: BoxProps['h'];
};

/**
 * Main image plus a thumbnail strip (only with 2+ images). Clicking the main
 * image opens it full screen, uncropped.
 */
export function ListingGallery({ srcs, alt, h }: ListingGalleryProps) {
  const { t } = useTranslation();
  const [activeIndex, setActiveIndex] = useState(0);
  const lightbox = useDisclosure();
  const hasImage = Boolean(srcs[activeIndex]);

  // A refetch may return fewer images than the index we were on.
  useEffect(() => {
    if (activeIndex >= srcs.length) setActiveIndex(0);
  }, [activeIndex, srcs.length]);

  return (
    <Box>
      <Box
        as="button"
        type="button"
        display="block"
        w="full"
        position="relative"
        cursor={hasImage ? 'zoom-in' : 'default'}
        disabled={!hasImage}
        data-group
        aria-label={t('listings.openImage')}
        onClick={lightbox.onOpen}
      >
        <ListingImage src={srcs[activeIndex] ?? null} alt={alt} h={h} fit="contain" />
        {hasImage ? (
          <Icon
            as={HiOutlineArrowsPointingOut}
            position="absolute"
            bottom={3}
            right={3}
            boxSize={9}
            p={2}
            borderRadius="full"
            bg="blackAlpha.600"
            color="white"
            opacity={0.8}
            transition="opacity 0.2s ease"
            _groupHover={{ opacity: 1 }}
          />
        ) : null}
      </Box>
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
      <ImageLightbox
        srcs={srcs}
        alt={alt}
        index={activeIndex}
        isOpen={lightbox.isOpen}
        onClose={lightbox.onClose}
        onIndexChange={setActiveIndex}
      />
    </Box>
  );
}
