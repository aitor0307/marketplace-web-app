import {
  Center,
  Flex,
  IconButton,
  Image,
  Modal,
  ModalContent,
  ModalOverlay,
  Text,
} from '@chakra-ui/react';
import { useEffect, useRef, useState, type MouseEvent, type TouchEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { HiChevronLeft, HiChevronRight, HiXMark } from 'react-icons/hi2';
import { resolveAssetUrl } from '@/config/env';

type ImageLightboxProps = {
  srcs: string[];
  alt: string;
  index: number;
  isOpen: boolean;
  onClose: () => void;
  onIndexChange: (index: number) => void;
};

/** Horizontal swipe distance (px) that counts as next/previous on touch screens. */
const SWIPE_THRESHOLD = 50;

const navButtonProps = {
  isRound: true,
  size: 'lg',
  fontSize: '2xl',
  bg: 'blackAlpha.600',
  color: 'white',
  _hover: { bg: 'blackAlpha.800' },
  position: 'absolute',
  top: '50%',
  transform: 'translateY(-50%)',
  zIndex: 1,
} as const;

/** How far a double click zooms into the image. */
const ZOOM_SCALE = 2.5;

/** Full-screen, uncropped view of a listing's images; double click zooms. */
export function ImageLightbox({
  srcs,
  alt,
  index,
  isOpen,
  onClose,
  onIndexChange,
}: ImageLightboxProps) {
  const { t } = useTranslation();
  const touchStartX = useRef<number | null>(null);
  const hasMany = srcs.length > 1;
  // Zoom origin as % of the image, so the clicked point stays under the cursor.
  const [zoom, setZoom] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => setZoom(null), [index, isOpen]);

  const onDoubleClick = (event: MouseEvent<HTMLImageElement>) => {
    if (zoom) return setZoom(null);
    const rect = event.currentTarget.getBoundingClientRect();
    setZoom({
      x: ((event.clientX - rect.left) / rect.width) * 100,
      y: ((event.clientY - rect.top) / rect.height) * 100,
    });
  };

  const go = (step: number) => onIndexChange((index + step + srcs.length) % srcs.length);

  useEffect(() => {
    if (!isOpen || !hasMany) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft') onIndexChange((index - 1 + srcs.length) % srcs.length);
      if (event.key === 'ArrowRight') onIndexChange((index + 1) % srcs.length);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, hasMany, index, srcs.length, onIndexChange]);

  const onTouchStart = (event: TouchEvent) => {
    touchStartX.current = event.touches[0]?.clientX ?? null;
  };
  const onTouchEnd = (event: TouchEvent) => {
    const start = touchStartX.current;
    const end = event.changedTouches[0]?.clientX;
    touchStartX.current = null;
    // While zoomed a swipe is the user looking around, not navigating.
    if (!hasMany || zoom || start === null || end === undefined) return;
    if (Math.abs(end - start) >= SWIPE_THRESHOLD) go(end < start ? 1 : -1);
  };

  const url = resolveAssetUrl(srcs[index] ?? null);

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="full" motionPreset="none">
      <ModalOverlay bg="rgba(0, 0, 0, 0.95)" />
      <ModalContent bg="transparent" boxShadow="none" m={0} borderRadius={0}>
        <Flex
          position="absolute"
          top={0}
          insetX={0}
          justify="space-between"
          align="center"
          px={4}
          py={3}
          zIndex={2}
          color="white"
        >
          <Text fontSize="sm" opacity={0.85}>
            {hasMany ? t('listings.imageCount', { index: index + 1, count: srcs.length }) : null}
          </Text>
          <IconButton
            aria-label={t('listings.closeImage')}
            icon={<HiXMark />}
            onClick={onClose}
            isRound
            fontSize="2xl"
            bg="blackAlpha.600"
            color="white"
            _hover={{ bg: 'blackAlpha.800' }}
          />
        </Flex>

        {/* Clicking the dark area around the image closes, like the overlay.
            Ignore the 2nd click of a double-click: the 1st one opened us. */}
        <Center
          h="100dvh"
          w="100vw"
          overflow="hidden"
          px={{ base: 0, md: 20 }}
          py={{ base: 14, md: 16 }}
          onClick={(event) => {
            if (event.detail <= 1) onClose();
          }}
          onTouchStart={onTouchStart}
          onTouchEnd={onTouchEnd}
        >
          {url ? (
            <Image
              src={url}
              alt={alt}
              maxW="100%"
              maxH="100%"
              objectFit="contain"
              userSelect="none"
              draggable={false}
              cursor={zoom ? 'zoom-out' : 'zoom-in'}
              transform={zoom ? `scale(${ZOOM_SCALE})` : undefined}
              transformOrigin={zoom ? `${zoom.x}% ${zoom.y}%` : undefined}
              transition="transform 0.2s ease"
              onClick={(event) => event.stopPropagation()}
              onDoubleClick={onDoubleClick}
            />
          ) : null}
        </Center>

        {hasMany ? (
          <>
            <IconButton
              {...navButtonProps}
              left={{ base: 2, md: 4 }}
              aria-label={t('listings.previousImage')}
              icon={<HiChevronLeft />}
              onClick={() => go(-1)}
            />
            <IconButton
              {...navButtonProps}
              right={{ base: 2, md: 4 }}
              aria-label={t('listings.nextImage')}
              icon={<HiChevronRight />}
              onClick={() => go(1)}
            />
          </>
        ) : null}
      </ModalContent>
    </Modal>
  );
}
