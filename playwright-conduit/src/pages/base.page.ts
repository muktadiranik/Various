import { expect, Locator, Page, Response } from '@playwright/test';
import { TIMEOUTS } from '@constants/index';

export abstract class BasePage {
  protected readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Navigate to a relative path.
   * Example:
   * await this.goto('/login');
   */
  async goto(path: string = '/'): Promise<void> {
    await this.page.goto(path, {
      waitUntil: 'domcontentloaded',
    });

    await this.waitForPageReady();
  }

  /**
   * Wait until the page is fully loaded.
   */
  async waitForPageReady(): Promise<void> {
    await this.page.waitForLoadState('domcontentloaded');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Reload the current page.
   */
  async reload(): Promise<void> {
    await this.page.reload({
      waitUntil: 'domcontentloaded',
    });

    await this.waitForPageReady();
  }

  /**
   * Click an element.
   */
  async click(locator: Locator): Promise<void> {
    await expect(locator).toBeVisible({
      timeout: TIMEOUTS.MEDIUM,
    });

    await locator.click();
  }

  /**
   * Fill an input.
   */
  async fill(locator: Locator, value: string): Promise<void> {
    await expect(locator).toBeVisible();

    await locator.fill(value);
  }

  /**
   * Clear then fill an input.
   */
  async clearAndFill(
    locator: Locator,
    value: string
  ): Promise<void> {
    await expect(locator).toBeVisible();

    await locator.clear();

    await locator.fill(value);
  }

  /**
   * Press a keyboard key.
   */
  async press(
    locator: Locator,
    key: string
  ): Promise<void> {
    await locator.press(key);
  }

  /**
   * Wait until locator is visible.
   */
  async waitFor(locator: Locator): Promise<void> {
    await locator.waitFor({
      state: 'visible',
      timeout: TIMEOUTS.MEDIUM,
    });
  }

  /**
   * Scroll to locator.
   */
  async scrollIntoView(locator: Locator): Promise<void> {
    await locator.scrollIntoViewIfNeeded();
  }

  /**
   * Returns trimmed inner text.
   */
  async getText(locator: Locator): Promise<string> {
    await expect(locator).toBeVisible();

    return (await locator.innerText()).trim();
  }

  /**
   * Returns input value.
   */
  async getValue(locator: Locator): Promise<string> {
    await expect(locator).toBeVisible();

    return locator.inputValue();
  }

  /**
   * Returns whether locator is visible.
   */
  async isVisible(locator: Locator): Promise<boolean> {
    return locator.isVisible();
  }

  /**
   * Assert locator visible.
   */
  async expectVisible(locator: Locator): Promise<void> {
    await expect(locator).toBeVisible();
  }

  /**
   * Assert locator hidden.
   */
  async expectHidden(locator: Locator): Promise<void> {
    await expect(locator).toBeHidden();
  }

  /**
   * Assert locator enabled.
   */
  async expectEnabled(locator: Locator): Promise<void> {
    await expect(locator).toBeEnabled();
  }

  /**
   * Assert locator disabled.
   */
  async expectDisabled(locator: Locator): Promise<void> {
    await expect(locator).toBeDisabled();
  }

  /**
   * Assert locator contains text.
   */
  async expectText(
    locator: Locator,
    text: string
  ): Promise<void> {
    await expect(locator).toContainText(text);
  }

  /**
   * Assert exact text.
   */
  async expectExactText(
    locator: Locator,
    text: string
  ): Promise<void> {
    await expect(locator).toHaveText(text);
  }

  /**
   * Assert current URL.
   */
  async expectUrlContains(
    value: string
  ): Promise<void> {
    await expect(this.page).toHaveURL(
      new RegExp(value)
    );
  }

  /**
   * Assert page title.
   */
  async expectPageTitle(
    title: string | RegExp
  ): Promise<void> {
    await expect(this.page).toHaveTitle(title);
  }

  /**
   * Wait for an API response.
   */
  async waitForApiResponse(
    urlPart: string,
    status = 200
  ): Promise<Response> {
    return this.page.waitForResponse(response => {
      return (
        response.url().includes(urlPart) &&
        response.status() === status
      );
    });
  }

  /**
   * Wait for URL navigation.
   */
  async waitForUrl(url: string | RegExp): Promise<void> {
    await this.page.waitForURL(url);
  }

  /**
   * Take screenshot.
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `test-results/${name}.png`,
      fullPage: true,
    });
  }
}