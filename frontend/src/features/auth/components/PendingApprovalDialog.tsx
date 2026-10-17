import {
  Button,
  Link,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Stack,
  Text,
} from '@chakra-ui/react';
import { Trans, useTranslation } from 'react-i18next';
import { useSessionStore } from '@/store/sessionStore';

/**
 * Shown once after signing up without a valid registration code. Lives in
 * MainLayout rather than RegisterScreen because signing in immediately
 * redirects away from the (guest-only) register route.
 */
export function PendingApprovalDialog() {
  const { t } = useTranslation();
  const notice = useSessionStore((s) => s.pendingApprovalNotice);
  const dismiss = useSessionStore((s) => s.dismissPendingApprovalNotice);
  const contactEmail = notice?.contactEmail;

  return (
    <Modal isOpen={Boolean(notice)} onClose={dismiss} isCentered>
      <ModalOverlay />
      <ModalContent borderRadius="2xl" mx={4}>
        <ModalHeader fontSize="lg">{t('auth.pendingTitle')}</ModalHeader>
        <ModalBody>
          <Stack spacing={3} color="brand.muted">
            <Text>{t('auth.pendingBody')}</Text>
            {contactEmail ? (
              <Text>
                <Trans
                  i18nKey="auth.pendingContact"
                  values={{ email: contactEmail }}
                  components={{
                    cta: <Link href={`mailto:${contactEmail}`} color="brand.primary" />,
                  }}
                />
              </Text>
            ) : null}
          </Stack>
        </ModalBody>
        <ModalFooter>
          <Button onClick={dismiss}>{t('auth.pendingOk')}</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
