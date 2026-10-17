import {
  Button,
  HStack,
  Input,
  Menu,
  MenuButton,
  MenuItemOption,
  MenuList,
  MenuOptionGroup,
  Stack,
  Tag,
  TagCloseButton,
  TagLabel,
  Wrap,
  WrapItem,
} from '@chakra-ui/react';
import { useState, type KeyboardEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { HiChevronDown } from 'react-icons/hi2';
import { SKI_TAGS } from '@/config/constants';
import { useTagLabel } from '@/features/listings/hooks/useTagLabel';

type TagPickerProps = {
  value: string[];
  onChange: (tags: string[]) => void;
};

/** Predefined ski tags from a dropdown, plus free-text ones typed in (Enter or comma adds). */
export function TagPicker({ value, onChange }: TagPickerProps) {
  const { t } = useTranslation();
  const tagLabel = useTagLabel();
  const [draft, setDraft] = useState('');

  const presetSelected = value.filter((tag) => (SKI_TAGS as readonly string[]).includes(tag));
  const custom = value.filter((tag) => !presetSelected.includes(tag));

  const onPresetChange = (selected: string | string[]) => {
    const presets = Array.isArray(selected) ? selected : [selected];
    // Keep the dropdown's order for presets, then the custom ones.
    onChange([...SKI_TAGS.filter((tag) => presets.includes(tag)), ...custom]);
  };

  const addDraft = () => {
    const tags = draft
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean)
      .filter((tag) => !value.includes(tag));
    if (tags.length) onChange([...value, ...tags]);
    setDraft('');
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' || event.key === ',') {
      // Enter would otherwise submit the listing form.
      event.preventDefault();
      addDraft();
    }
  };

  return (
    <Stack spacing={3}>
      <HStack spacing={2} align="stretch">
        <Menu closeOnSelect={false} placement="bottom-start">
          <MenuButton as={Button} variant="outline" rightIcon={<HiChevronDown />} flexShrink={0}>
            {t('newListing.tagsPick')}
            {presetSelected.length ? ` (${presetSelected.length})` : ''}
          </MenuButton>
          <MenuList maxH="300px" overflowY="auto" zIndex={10}>
            <MenuOptionGroup type="checkbox" value={presetSelected} onChange={onPresetChange}>
              {SKI_TAGS.map((tag) => (
                <MenuItemOption key={tag} value={tag}>
                  {tagLabel(tag)}
                </MenuItemOption>
              ))}
            </MenuOptionGroup>
          </MenuList>
        </Menu>
        <Input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={onKeyDown}
          onBlur={addDraft}
          placeholder={t('newListing.tagsPlaceholder')}
        />
      </HStack>

      {value.length ? (
        <Wrap spacing={2}>
          {value.map((tag) => (
            <WrapItem key={tag}>
              <Tag size="md" borderRadius="full" bg="accent.50" color="accent.800">
                <TagLabel>{tagLabel(tag)}</TagLabel>
                <TagCloseButton
                  aria-label={t('newListing.tagsRemove', { tag: tagLabel(tag) })}
                  onClick={() => onChange(value.filter((other) => other !== tag))}
                />
              </Tag>
            </WrapItem>
          ))}
        </Wrap>
      ) : null}
    </Stack>
  );
}
