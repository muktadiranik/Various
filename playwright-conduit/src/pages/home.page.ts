import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./base.page";
import { ROUTES } from "@constants/index";

export class HomePage extends BasePage {
  // Navigation
  readonly homeLink: Locator;
  readonly newArticleLink: Locator;
  readonly settingsLink: Locator;
  readonly profileLink: Locator;

  // Feed Tabs
  readonly yourFeedTab: Locator;
  readonly globalFeedTab: Locator;
  readonly tagFeedTab: Locator;

  // Articles
  readonly articlePreview: Locator;
  readonly articleTitles: Locator;

  // Tags
  readonly popularTags: Locator;

  // Empty state
  readonly noArticlesMessage: Locator;

  constructor(page: Page) {
    super(page);

    this.homeLink = page.getByRole("link", {
      name: /^home$/i,
    });

    this.newArticleLink = page.getByRole("link", {
      name: /new article/i,
    });

    this.settingsLink = page.getByRole("link", {
      name: /settings/i,
    });

    // Username changes depending on the account
    this.profileLink = page.locator('a.nav-link[href*="/profile/"]');

    this.yourFeedTab = page.getByRole("button", {
      name: /your feed/i,
    });

    this.globalFeedTab = page.getByRole("button", {
      name: /global feed/i,
    });

    this.tagFeedTab = page.locator(".feed-toggle .nav-item");

    this.articlePreview = page.locator(".article-preview");

    this.articleTitles = page.locator(".article-preview h1");

    this.popularTags = page.locator(".sidebar a.tag-pill");

    this.noArticlesMessage = page.getByText(/no articles are here/i);
  }

  /**
   * Open Home page.
   */
  async open(): Promise<void> {
    await this.goto("/");

    await this.waitForPageReady();
  }

  /**
   * Navigate to Editor.
   */
  async goToNewArticle(): Promise<void> {
    await this.click(this.newArticleLink);

    await this.expectUrlContains(ROUTES.EDITOR);
  }

  /**
   * Navigate to Settings.
   */
  async goToSettings(): Promise<void> {
    await this.click(this.settingsLink);

    await this.expectUrlContains(ROUTES.SETTINGS);
  }

  /**
   * Open logged-in user's profile.
   */
  async goToProfile(): Promise<void> {
    await this.click(this.profileLink);

    await this.expectUrlContains("/profile/");
  }

  /**
   * Open Global Feed.
   */
  async openGlobalFeed(): Promise<void> {
    await this.click(this.globalFeedTab);

    await this.waitForPageReady();
  }

  /**
   * Open Your Feed.
   */
  async openYourFeed(): Promise<void> {
    await this.click(this.yourFeedTab);

    await this.waitForPageReady();
  }

  /**
   * Filter by tag.
   */
  async filterByTag(tag: string): Promise<void> {
    await this.page
      .locator(".sidebar")
      .filter({
        has: this.page.getByText("Popular Tags"),
      })
      .locator("a.tag-pill")
      .filter({
        hasText: new RegExp(`^\\s*${tag}\\s*$`),
      })
      .click();

    await this.waitForPageReady();
  }

  /**
   * Verify selected tag feed.
   */
  async expectSelectedTag(tag: string): Promise<void> {
    await expect(this.tagFeedTab).toContainText(tag);
  }

  /**
   * Open article by title.
   */
  async openArticle(title: string): Promise<void> {
    const article = this.page.locator(".article-preview h1").filter({
      hasText: title,
    });

    await article.click();

    await this.waitForPageReady();
  }

  /**
   * Verify article exists.
   */
  async expectArticleVisible(title: string): Promise<void> {
    await expect(
      this.articleTitles.filter({
        hasText: title,
      }),
    ).toBeVisible();
  }

  /**
   * Verify article does not exist.
   */
  async expectArticleNotVisible(title: string): Promise<void> {
    await expect(
      this.articleTitles.filter({
        hasText: title,
      }),
    ).toHaveCount(0);
  }

  /**
   * Verify feed has articles.
   */
  async expectArticlesPresent(): Promise<void> {
    await expect(this.articlePreview.first()).toBeVisible();
  }

  /**
   * Verify empty feed.
   */
  async expectNoArticles(): Promise<void> {
    await expect(this.noArticlesMessage).toBeVisible();
  }

  /**
   * Verify tag exists.
   */
  async expectTagVisible(tag: string): Promise<void> {
    await expect(
      this.popularTags.filter({
        hasText: tag,
      }),
    ).toBeVisible();
  }

  /**
   * Return all article titles.
   */
  async getArticleTitles(): Promise<string[]> {
    return this.articleTitles.allInnerTexts();
  }

  /**
   * Verify every article contains a tag.
   */
  async expectEveryArticleContainsTag(tag: string): Promise<void> {
    const articles = await this.articlePreview.count();

    for (let i = 0; i < articles; i++) {
      await expect(
        this.articlePreview.nth(i).locator(".tag-list"),
        /**
         * As the data is generated randomly
         * some articles may not have tags
         * so we need to use regex
         * to check if the tag exists
         * or not
         */
      ).toContainText(new RegExp(`[a-zA-Z]`, "i"));
    }
  }
}
