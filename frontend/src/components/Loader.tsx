import { Center, Spinner, type SpinnerProps } from '@chakra-ui/react';

export type LoaderProps = SpinnerProps & {
  fullScreen?: boolean;
};

export function Loader({ fullScreen = false, ...props }: LoaderProps) {
  const spinner = <Spinner color="brand.accent" thickness="3px" speed="0.65s" {...props} />;

  if (!fullScreen) {
    return spinner;
  }

  return (
    <Center minH="40vh" w="full">
      {spinner}
    </Center>
  );
}
