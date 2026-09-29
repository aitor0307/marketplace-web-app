/** Pydantic v2 error item, as returned by app.errors' ValidationError handler. */
export type ValidationErrorItem = {
  loc: (string | number)[];
  msg: string;
  type?: string;
};

/**
 * The backend returns two error shapes: operations use `{ error }`, while
 * ResponseFactory (validation, JWT failures) uses `{ success, message }`.
 */
export type ApiErrorBody = {
  error?: string;
  success?: boolean;
  message?: string | ValidationErrorItem[];
};

export class ApiError extends Error {
  readonly status: number;
  /** Field name → first validation message, when the backend rejected the payload. */
  readonly fieldErrors: Record<string, string>;

  constructor(status: number, message: string, fieldErrors: Record<string, string> = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export type RequestOptions = {
  method?: HttpMethod;
  /** Plain objects are sent as JSON; FormData is sent as multipart. */
  body?: unknown;
  query?: Record<string, string | number | undefined | null>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  /** When false, skip the Authorization header (e.g. login). Default true. */
  auth?: boolean;
};
