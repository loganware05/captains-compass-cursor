// Fixture: API client that crosses the ui boundary (M40 boundary fixtures).
import { FormProps, buildForm } from '../ui/components/Form';
import { validateForm } from '../ui/utils/validate';

export interface SubmissionResult {
  ok: boolean;
  errors: string[];
}

export function submitForm(form: FormProps): SubmissionResult {
  const errors = validateForm(form.fields);
  return { ok: errors.length === 0, errors };
}

export function remake(title: string): FormProps {
  return buildForm(title, []);
}
