// Fixture: input component module for context inode tests (M40).

export interface InputProps {
  name: string;
  label: string;
  required?: boolean;
}

export type InputKind = 'text' | 'email' | 'number';

export function describeInput(props: InputProps): string {
  return `${props.name}:${props.label}`;
}
