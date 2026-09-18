// Fixture: validation utilities for context inode tests (M40).
import { InputProps } from '../components/Input';

/** @complexity O(1) */
export function validateEmail(value: string): boolean {
  return value.includes('@');
}

/** @complexity O(N) */
export function validateForm(fields: InputProps[]): string[] {
  const errors: string[] = [];
  for (const field of fields) {
    if (field.required && !field.label) {
      errors.push(field.name);
    }
  }
  return errors;
}
