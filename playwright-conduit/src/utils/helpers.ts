import { expect, Locator, Page } from '@playwright/test';

/**
 * Wait until the page has finished loading.
 */
export async function waitForPageLoad(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForLoadState('networkidle');
}

/**
 * Click an element after ensuring it is visible.
 */
export async function safeClick(locator: Locator): Promise<void> {
  await expect(locator).toBeVisible();
  await locator.click();
}

/**
 * Fill an input after ensuring it is visible.
 */
export async function safeFill(
  locator: Locator,
  value: string
): Promise<void> {
  await expect(locator).toBeVisible();
  await locator.fill(value);
}

/**
 * Clear an input field.
 */
export async function clearInput(locator: Locator): Promise<void> {
  await expect(locator).toBeVisible();
  await locator.clear();
}

/**
 * Assert that the current URL contains the expected path.
 */
export async function expectUrlContains(
  page: Page,
  path: string
): Promise<void> {
  await expect(page).toHaveURL(new RegExp(path));
}

/**
 * Assert that a locator contains the expected text.
 */
export async function expectText(
  locator: Locator,
  text: string
): Promise<void> {
  await expect(locator).toContainText(text);
}

/**
 * Assert an element is visible.
 */
export async function expectVisible(locator: Locator): Promise<void> {
  await expect(locator).toBeVisible();
}

/**
 * Assert an element is hidden.
 */
export async function expectHidden(locator: Locator): Promise<void> {
  await expect(locator).toBeHidden();
}

/**
 * Refresh the page and wait for it to stabilize.
 */
export async function refresh(page: Page): Promise<void> {
  await page.reload();
  await waitForPageLoad(page);
}

/**
 * Generate a URL-friendly slug.
 */
export function slugify(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-');
}

/**
 * Sleep helper.
 * Use sparingly—prefer Playwright's built-in waiting mechanisms.
 */
export async function delay(milliseconds: number): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, milliseconds));
}

/**
 * Returns a random integer between min and max (inclusive).
 */
export function randomNumber(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Returns a unique timestamp string.
 */
export function timestamp(): string {
  return Date.now().toString();
}