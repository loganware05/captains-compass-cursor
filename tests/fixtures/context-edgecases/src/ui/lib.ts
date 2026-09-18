// Edge-case fixture: generics, default export, class, re-exports, variadic (M40 hardening).
import { InputProps } from './components/Input';

export function identity<T>(value: T): T { return value; }

export default function Widget(props: InputProps): string { return props.name; }

export function sizeOf(opts: Map<string, number>): number { return opts.size; }

export function collect(first: string, ...rest: number[]): number[] { return rest; }

export class FormStore {
  private items: string[] = [];
  add(item: string): void { this.items.push(item); }
  count(): number { return this.items.length; }
}

export { InputProps } from './components/Input';

export type ApiToken = 'placeholder-not-a-secret';
