// Fixture: form component module for context inode tests (M40).
import { InputProps } from './Input';

export interface FormProps {
  title: string;
  fields: InputProps[];
  onSubmit: (values: Record<string, string>) => void;
  disabled?: boolean;
}

/**
 * Build a form model from raw field configs.
 * @complexity O(N)
 */
export function buildForm(title: string, fields: InputProps[]): FormProps {
  return {
    title,
    fields,
    onSubmit: () => undefined,
  };
}

export const DEFAULT_FORM_TITLE: string = 'untitled';
