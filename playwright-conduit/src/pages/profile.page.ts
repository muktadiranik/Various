import { expect, Locator, Page } from '@playwright/test';
import { BasePage } from './base.page';

export class ProfilePage extends BasePage {
  readonly profileName: Locator;
  readonly profileImage: Locator;

  readonly myArticlesTab: Locator;
  readonly favoritedArticlesTab: Locator;

  readonly articlePreviews: Locator;
  readonly articleTitles: Locator;

  readonly emptyArticlesMessage: Locator;

  constructor(page: Page) {
    super(page);

    this.profileName = page.locator('.user-info h4');

    this.profileImage = page.locator('.user-img');

    this.myArticlesTab = page.getByRole('link', {
      name: /my articles/i,
    });

    this.favoritedArticlesTab = page.getByRole('link', {
      name: /favorited articles/i,
    });

    this.articlePreviews = page.locator('.article-preview');

    this.articleTitles = page.locator('.article-preview h1');

    this.emptyArticlesMessage = page.getByText(
      /no articles are here/i
    );
  }

  /**
   * Verify profile username.
   */
  async verifyUsername(username: string): Promise<void> {
    await expect(this.profileName).toHaveText(username);
  }

  /**
   * Verify profile image.
   */
  async verifyProfileImage(): Promise<void> {
    await expect(this.profileImage).toBeVisible();
  }

  /**
   * Open "My Articles" tab.
   */
  async openMyArticles(): Promise<void> {
    await this.click(this.myArticlesTab);

    await this.waitForPageReady();
  }

  /**
   * Open "Favorited Articles" tab.
   */
  async openFavoritedArticles(): Promise<void> {
    await this.click(this.favoritedArticlesTab);

    await this.waitForPageReady();
  }

  /**
   * Open an article by title.
   */
  async openArticle(title: string): Promise<void> {
    const article = this.articleTitles.filter({
      hasText: title,
    });

    await expect(article).toBeVisible();

    await article.click();

    await this.waitForPageReady();
  }

  /**
   * Verify an article exists.
   */
  async verifyArticleExists(title: string): Promise<void> {
    await expect(
      this.articleTitles.filter({
        hasText: title,
      })
    ).toBeVisible();
  }

  /**
   * Verify an article does not exist.
   */
  async verifyArticleDoesNotExist(
    title: string
  ): Promise<void> {
    await expect(
      this.articleTitles.filter({
        hasText: title,
      })
    ).toHaveCount(0);
  }

  /**
   * Verify there are articles in the profile.
   */
  async verifyArticlesPresent(): Promise<void> {
    await expect(
      this.articlePreviews.first()
    ).toBeVisible();
  }

  /**
   * Verify profile has no articles.
   */
  async verifyNoArticles(): Promise<void> {
    await expect(
      this.emptyArticlesMessage
    ).toBeVisible();
  }

  /**
   * Return article count.
   */
  async getArticleCount(): Promise<number> {
    return this.articlePreviews.count();
  }

  /**
   * Return all article titles.
   */
  async getArticleTitles(): Promise<string[]> {
    return this.articleTitles.allInnerTexts();
  }

  /**
   * Verify article count.
   */
  async verifyArticleCount(
    expected: number
  ): Promise<void> {
    await expect(this.articlePreviews).toHaveCount(
      expected
    );
  }

  /**
   * Refresh profile page.
   */
  async refreshProfile(): Promise<void> {
    await this.reload();
  }
}