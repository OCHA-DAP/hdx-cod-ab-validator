import { checkVersions } from "./check_versions.ts";
import { checkDates } from "./check_dates.ts";
import type { Check } from "./types.ts";

/**
 * Ordered list of all registered validation checks.
 *
 * To add a new check:
 *   1. Create src/lib/checks/check_<name>.ts implementing the Check interface
 *   2. Import it here and add it to this array
 *   Nothing else needs to change.
 */
export const checks: Check[] = [checkVersions, checkDates];
