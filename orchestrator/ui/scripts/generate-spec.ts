import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { northstarOpenUILibrary } from "../src/library";

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, "..", "openui.spec.json");
const spec = northstarOpenUILibrary.toSpec();
writeFileSync(out, JSON.stringify(spec, null, 2) + "\n", "utf8");
mkdirSync(join(here, "..", "..", "..", ".cursor", "templates"), { recursive: true });
console.log(`wrote ${out}`);
