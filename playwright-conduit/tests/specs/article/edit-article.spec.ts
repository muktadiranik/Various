import { test, expect } from "@playwright/test";

import { ApiClient } from "../../../src/api/api.client";
import { ArticlePage } from "../../../src/pages/article.page";
import { EditorPage } from "../../../src/pages/editor.page";

import { generateArticle } from "../../../src/utils/random-data";

test.describe("Edit Article", () => {
  let apiClient: ApiClient;

  test.beforeEach(async () => {
    apiClient = new ApiClient();
    await apiClient.init();
    await apiClient.login();
  });

  test.afterEach(async () => {
    await apiClient.dispose();
  });

  test("should edit an existing article", async ({ page }) => {
    const articlePage = new ArticlePage(page);
    const editorPage = new EditorPage(page);

    /**
     * Create article using API as pre-condition
     */
    const originalArticle = generateArticle();
    const createdArticle = await apiClient.createArticle(originalArticle);

    /**
     * Navigate to created article
     */
    await page.goto(`/article/${createdArticle.slug}`);
    await articlePage.verifyTitle(originalArticle.title);

    /**
     * Open editor
     */
    await articlePage.clickEdit();
    await editorPage.verifyEditorLoaded();

    /**
     * Generate updated data
     */
    const updatedArticle = generateArticle();

    /**
     * Update article
     */
    await editorPage.updateArticle(updatedArticle.title, updatedArticle.description, updatedArticle.body, updatedArticle.tags);

    /**
     * Verify redirect to article page (Forces Playwright to auto-wait for the URL change)
     */
    await expect(page).toHaveURL(/\/article\/[\w-]+/, { timeout: 10000 });

    /**
     * Verify updated article content
     */
    await articlePage.verifyTitle(updatedArticle.title);
    await articlePage.verifyBody(updatedArticle.body);

    /**
     * Verify data persists after refresh
     */
    await articlePage.verifyArticlePersistence(updatedArticle.title, updatedArticle.body);
  });

  test("should not update article with invalid data", async ({ page }) => {
    const articlePage = new ArticlePage(page);
    const editorPage = new EditorPage(page);

    /**
     * Create article using API
     */
    const article = generateArticle();
    const createdArticle = await apiClient.createArticle(article);

    await page.goto(`/article/${createdArticle.slug}`);

    /**
     * Open editor
     */
    await articlePage.clickEdit();
    await editorPage.verifyEditorLoaded();

    /**
     * CRUCIAL: Wait for the old data to load completely before clearing it out
     */
    await editorPage.waitForExistingArticleData();

    /**
     * Remove required fields safely now that the fields have settled
     */
    await editorPage.clearAndFillArticle("", "", "", []);
    await editorPage.clickPublish();

    /**
     * Assert Conduit's silent fallback behavior
     */
    await expect(page).toHaveURL(new RegExp(`/article/${createdArticle.slug}`));
    await articlePage.verifyTitle(article.title);
    await articlePage.verifyBody(article.body);
  });

  test("should keep original article when submitting empty values", async ({ page }) => {
    const articlePage = new ArticlePage(page);
    const editorPage = new EditorPage(page);

    const article = generateArticle();

    const createdArticle = await apiClient.createArticle(article);

    await page.goto(`/article/${createdArticle.slug}`);

    await articlePage.clickEdit();

    await editorPage.verifyEditorLoaded();

    /**
     * Clear all fields
     */
    await editorPage.fillArticle("", "", "", []);

    await editorPage.clickPublish();

    /**
     * Back on article page
     */
    await expect(page).toHaveURL(/\/article\//);

    /**
     * Original data should still exist
     */
    await articlePage.verifyTitle(article.title);

    await articlePage.verifyBody(article.body);
  });
});
