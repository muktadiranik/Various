import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./base.page";

export class EditorPage extends BasePage {
  readonly titleInput: Locator;
  readonly descriptionInput: Locator;
  readonly bodyInput: Locator;
  readonly tagsInput: Locator;
  readonly publishButton: Locator;
  readonly validationErrors: Locator;

  constructor(page: Page) {
    super(page);

    this.titleInput = page.getByPlaceholder("Article Title");
    this.descriptionInput = page.getByPlaceholder("What's this article about?");
    this.bodyInput = page.getByPlaceholder("Write your article (in markdown)");
    this.tagsInput = page.getByPlaceholder("Enter tags");
    this.publishButton = page.getByRole("button", {
      name: /publish article/i,
    });

    /**
     * Conduit renders validation messages as:
     *
     * <ul class="error-messages">
     *   <li>title can't be blank</li>
     * </ul>
     */
    this.validationErrors = page.locator(".error-messages li");
  }

  /**
   * Fill article form securely across all browsers.
   */
  async fillArticle(title: string, description: string, body: string, tags: string[] = []): Promise<void> {
    /**
     * Clear the fields first to trigger initial state alterations
     */
    await this.titleInput.clear();
    await this.titleInput.fill(title);

    await this.descriptionInput.clear();
    await this.descriptionInput.fill(description);

    await this.bodyInput.clear();
    await this.bodyInput.fill(body);

    if (tags.length > 0) {
      for (const tag of tags) {
        await this.tagsInput.clear();
        await this.tagsInput.fill(tag);
        await this.page.keyboard.press("Enter");
      }
    }

    /**
     * Crucial for Firefox: Blur the last element to flush the UI framework's internal events
     */
    await this.bodyInput.blur();
  }

  /**
   * Added publishArticle method that automates the full creation lifecycle
   * while listening securely for the backend POST network payload interceptor.
   */
  async publishArticle(article: { title: string; description: string; body: string; tags: string[] }): Promise<void> {
    await this.fillArticle(article.title, article.description, article.body, article.tags);

    /**
     * Securely wait for backend creation persistence and user action concurrently
     */
    await Promise.all([this.page.waitForResponse((response) => response.url().includes("/articles") && response.request().method() === "POST"), this.publishButton.click()]);

    await this.waitForPageReady();
  }

  /**
   * Aggressively clears and refills fields.
   * Useful when changing existing data to empty strings to trigger UI state updates.
   */
  async clearAndFillArticle(title: string, description: string, body: string, tags: string[] = []): Promise<void> {
    const inputs = [this.titleInput, this.descriptionInput, this.bodyInput];
    for (const input of inputs) {
      await input.click();
      await this.page.keyboard.press("Control+A");
      await this.page.keyboard.press("Backspace");
    }
    await this.fillArticle(title, description, body, tags);
  }

  /**
   * Create a new article.
   */
  async createArticle(title: string, description: string, body: string, tags: string[] = []): Promise<void> {
    await this.fillArticle(title, description, body, tags);
    await Promise.all([this.page.waitForResponse((response) => response.url().includes("/articles") && response.request().method() === "POST"), this.publishButton.click()]);
    await this.waitForPageReady();
  }

  /**
   * Waits for the editor inputs to be populated with the existing article data.
   * This prevents Playwright from typing before the app loads the backend values.
   */
  async waitForExistingArticleData(): Promise<void> {
    // Wait until the title input is no longer empty
    await expect(this.titleInput).not.toHaveValue("");
    // Wait for the body input to also contain text
    await expect(this.bodyInput).not.toHaveValue("");
  }

  /**
   * Update existing article safely by waiting for data to load first.
   */
  async updateArticle(title: string, description: string, body: string, tags: string[] = []): Promise<void> {
    /**
     * Wait for the SPA to load the existing article data into the UI
     */
    await this.waitForExistingArticleData();

    await this.titleInput.click();
    await this.page.keyboard.press("Control+A");
    await this.page.keyboard.press("Backspace");
    await this.titleInput.fill(title);

    await this.descriptionInput.click();
    await this.page.keyboard.press("Control+A");
    await this.page.keyboard.press("Backspace");
    await this.descriptionInput.fill(description);

    await this.bodyInput.click();
    await this.page.keyboard.press("Control+A");
    await this.page.keyboard.press("Backspace");
    await this.bodyInput.fill(body);

    if (tags.length > 0) {
      for (const tag of tags) {
        await this.tagsInput.fill(tag);
        await this.page.keyboard.press("Enter");
      }
    }

    await this.bodyInput.blur();

    /**
     * Set up response listener explicitly
     */
    const responsePromise = this.page.waitForResponse((response) => response.url().includes("/articles/") && response.request().method() === "PUT");

    await this.publishButton.click();
    await responsePromise;
    await this.waitForPageReady();
  }

  /**
   * Fill only title.
   * Useful for negative tests.
   */
  async fillTitle(title: string): Promise<void> {
    await this.titleInput.fill(title);
  }

  /**
   * Fill only description.
   */
  async fillDescription(description: string): Promise<void> {
    await this.descriptionInput.fill(description);
  }

  /**
   * Fill only body.
   */
  async fillBody(body: string): Promise<void> {
    await this.bodyInput.fill(body);
  }

  /**
   * Click publish button.
   */
  async clickPublish(): Promise<void> {
    await this.publishButton.click();
  }

  /**
   * Verify editor page loaded.
   */
  async verifyEditorLoaded(): Promise<void> {
    await expect(this.publishButton).toBeVisible();
  }

  /**
   * Verify validation errors.
   */
  async expectValidationErrors(): Promise<void> {
    await expect(this.validationErrors.first()).toBeVisible();
  }

  /**
   * Verify specific validation message.
   */
  async verifyValidationMessage(message: string): Promise<void> {
    await expect(this.validationErrors).toContainText(message);
  }

  /**
   * Get current title value.
   */
  async getTitleValue(): Promise<string> {
    return await this.titleInput.inputValue();
  }

  /**
   * Get current description value.
   */
  async getDescriptionValue(): Promise<string> {
    return await this.descriptionInput.inputValue();
  }

  /**
   * Get current body value.
   */
  async getBodyValue(): Promise<string> {
    return await this.bodyInput.inputValue();
  }
}
