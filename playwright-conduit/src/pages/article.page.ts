import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./base.page";

export class ArticlePage extends BasePage {
  readonly articleTitle: Locator;
  readonly articleBody: Locator;

  readonly editArticleButton: Locator;
  readonly deleteArticleButton: Locator;
  readonly favoriteButton: Locator;

  readonly commentInput: Locator;
  readonly postCommentButton: Locator;

  readonly articleMeta: Locator;
  readonly tagList: Locator;

  constructor(page: Page) {
    super(page);

    this.articleTitle = page.locator(".banner h1");

    this.articleBody = page.locator(".article-content p");

    this.editArticleButton = page
      .locator("a", {
        hasText: "Edit Article",
      })
      .first();

    this.deleteArticleButton = page
      .locator("button", {
        hasText: "Delete Article",
      })
      .first();

    this.favoriteButton = page.getByRole("button", {
      name: /favorite article/i,
    });

    this.commentInput = page.getByPlaceholder("Write a comment...");

    this.postCommentButton = page.getByRole("button", {
      name: /post comment/i,
    });

    this.articleMeta = page.locator(".article-meta");

    this.tagList = page.locator(".tag-list .tag-default");
  }

  /**
   * Verify article title.
   */
  async verifyTitle(title: string): Promise<void> {
    await expect(this.articleTitle).toHaveText(title);
  }

  /**
   * Verify article body.
   */
  async verifyBody(body: string): Promise<void> {
    await expect(this.articleBody).toContainText(body);
  }

  /**
   * Verify current URL contains article slug.
   */
  async verifySlug(slug: string): Promise<void> {
    await expect(this.page).toHaveURL(new RegExp(`/article/${slug}$`));
  }

  /**
   * Verify current page is an article page.
   */
  async verifyArticlePage(): Promise<void> {
    await expect(this.page).toHaveURL(/\/article\//);
  }

  /**
   * Verify Edit button.
   */
  async verifyEditButtonVisible(): Promise<void> {
    await expect(this.editArticleButton).toBeVisible();
  }

  /**
   * Verify Delete button.
   */
  async verifyDeleteButtonVisible(): Promise<void> {
    await expect(this.deleteArticleButton).toBeVisible();
  }

  /**
   * Verify article author.
   */
  async verifyAuthor(username: string): Promise<void> {
    await expect(this.articleMeta).toContainText(username);
  }

  /**
   * Verify article tag.
   */
  async verifyTag(tag: string): Promise<void> {
    await expect(this.tagList).toContainText(tag);
  }

  /**
   * Click Edit Article.
   */
  async clickEdit(): Promise<void> {
    await this.editArticleButton.click();

    await expect(this.page).toHaveURL(/\/editor\//);
  }

  /**
   * Delete current article.
   */
  async deleteArticle(): Promise<void> {
    await Promise.all([
      this.page.waitForResponse((response) => response.request().method() === "DELETE" && response.url().includes("/articles/")),
      this.deleteArticleButton.click(),
    ]);

    await expect(this.page).toHaveURL("/");
  }

  /**
   * Verify article not found.
   */
  async verifyArticleNotFound(): Promise<void> {
    /**
     * Verify returned to home page
     */
    await expect(this.page).toHaveURL(/\/$/);
  }

  /**
   * Favorite article.
   */
  async favoriteArticle(): Promise<void> {
    await this.favoriteButton.click();
  }

  /**
   * Add a comment.
   */
  async addComment(comment: string): Promise<void> {
    await this.commentInput.fill(comment);

    await this.postCommentButton.click();

    await expect(this.page.locator(".card-text").last()).toContainText(comment);
  }

  /**
   * Verify comment.
   */
  async verifyComment(comment: string): Promise<void> {
    await expect(this.page.locator(".card-text")).toContainText(comment);
  }

  /**
   * Verify article persists after refresh.
   */
  async verifyArticlePersistence(title: string, body: string): Promise<void> {
    await this.page.reload();

    await this.verifyTitle(title);

    await this.verifyBody(body);
  }

  /**
   * Verify article deleted by redirect.
   */
  async verifyArticleDeleted(): Promise<void> {
    await expect(this.page).toHaveURL("/");

    await expect(this.page.getByText("Global Feed")).toBeVisible();
  }
}
