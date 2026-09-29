import type { FieldValues, Path, UseFormSetError } from 'react-hook-form';
import { ApiError } from '@/types/api';

/**
 * Routes a failed mutation onto a react-hook-form: pydantic field errors land
 * on their inputs, anything else becomes the form-level `root` error.
 */
export function applyApiError<T extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<T>,
  fallbackMessage: string,
  fields: readonly Path<T>[],
): void {
  if (error instanceof ApiError) {
    let matched = false;
    for (const [field, message] of Object.entries(error.fieldErrors)) {
      if ((fields as readonly string[]).includes(field)) {
        setError(field as Path<T>, { message });
        matched = true;
      }
    }
    if (!matched) setError('root', { message: error.message || fallbackMessage });
    return;
  }
  setError('root', { message: fallbackMessage });
}
