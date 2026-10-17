import {
  Button,
  FormControl,
  FormErrorMessage,
  FormHelperText,
  FormLabel,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Select,
  Stack,
  Textarea,
  useToast,
} from '@chakra-ui/react';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import {
  FEEDBACK_KINDS,
  feedbackApi,
  type FeedbackKind,
} from '@/features/feedback/api/feedback.api';

type FeedbackDialogProps = {
  isOpen: boolean;
  onClose: () => void;
};

type FeedbackFormValues = { kind: FeedbackKind; message: string };

const MAX_MESSAGE_LENGTH = 2000;

/** Report a bug or suggest an improvement to the admin, by email. */
export function FeedbackDialog({ isOpen, onClose }: FeedbackDialogProps) {
  const { t } = useTranslation();
  const toast = useToast();
  const location = useLocation();
  const sendFeedback = useMutation({ mutationFn: feedbackApi.send });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FeedbackFormValues>({ defaultValues: { kind: 'bug', message: '' } });

  const onSubmit = handleSubmit((values) =>
    sendFeedback.mutate(
      {
        kind: values.kind,
        message: values.message.trim(),
        page: `${location.pathname}${location.search}`,
      },
      {
        onSuccess: () => {
          toast({ status: 'success', title: t('feedback.sent') });
          reset();
          onClose();
        },
        onError: (err) => toast({ status: 'error', title: err.message }),
      },
    ),
  );

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent as="form" onSubmit={onSubmit} mx={4}>
        <ModalHeader>{t('feedback.title')}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Stack spacing={4}>
            <FormControl>
              <FormLabel>{t('feedback.kind')}</FormLabel>
              <Select {...register('kind')}>
                {FEEDBACK_KINDS.map((kind) => (
                  <option key={kind} value={kind}>
                    {t(`feedback.kinds.${kind}`)}
                  </option>
                ))}
              </Select>
            </FormControl>
            <FormControl isInvalid={Boolean(errors.message)}>
              <FormLabel>{t('feedback.message')}</FormLabel>
              <Textarea
                rows={6}
                placeholder={t('feedback.messagePlaceholder')}
                {...register('message', {
                  validate: (value) => value.trim().length > 0 || t('validation.required'),
                  maxLength: {
                    value: MAX_MESSAGE_LENGTH,
                    message: t('validation.maxLength', { count: MAX_MESSAGE_LENGTH }),
                  },
                })}
              />
              <FormHelperText fontSize="xs">{t('feedback.help')}</FormHelperText>
              <FormErrorMessage>{errors.message?.message}</FormErrorMessage>
            </FormControl>
          </Stack>
        </ModalBody>
        <ModalFooter gap={2}>
          <Button variant="ghost" onClick={onClose}>
            {t('feedback.cancel')}
          </Button>
          <Button type="submit" isLoading={sendFeedback.isPending}>
            {t('feedback.submit')}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
