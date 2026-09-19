// Edge-case fixture: correct usage of edge-case exports (clean control).
import Widget, { identity, collect, sizeOf } from '../ui/lib';

export function run(opts: Map<string, number>): number {
  const size = sizeOf(opts);
  const values = collect('first', 1, 2, 3);
  return identity<number>(size) + values.length;
}

export const label: string = Widget({ name: 'x', label: 'y' });
