import { Box } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import { TopNav } from '@/components/TopNav';
import { VersionBadge } from '@/components/VersionBadge';
import { PendingApprovalDialog } from '@/features/auth';

export function MainLayout() {
  return (
    <Box minH="100dvh" bg="brand.pageBg">
      <TopNav />
      <Outlet />
      <PendingApprovalDialog />
      <VersionBadge />
    </Box>
  );
}
