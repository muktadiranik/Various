import { expect, test } from "@playwright/test";

import { STORAGE } from "../../../src/constants";
import { validArticle, invalidArticle } from "../../../src/fixtures/test-data";

import { HomePage } from "../../../src/pages/home.page";
import { EditorPage } from "../../../src/pages/editor.page";
import { ArticlePage } from "../../../src/pages/article.page";

test.describe("Create Article", () => {
  test.use({
    storageState: STORAGE.AUTH,
  });

  test("should create a new article successfully", async ({ page }) => {
    const homePage = new HomePage(page);
    const editorPage = new EditorPage(page);
    const articlePage = new ArticlePage(page);

    const article = validArticle();

    await homePage.open();

    await homePage.goToNewArticle();

    await editorPage.publishArticle(article);

    /**
     * Verify navigation to article page
     */
    await articlePage.verifyArticlePage();

    /**
     * Verify article content
     */
    await articlePage.verifyTitle(article.title);
    await articlePage.verifyBody(article.body);

    /**
     * Verify available actions
     */
    await articlePage.verifyEditButtonVisible();
    await articlePage.verifyDeleteButtonVisible();

    /**
     * Verify persistence after refresh
     */
    await articlePage.verifyArticlePersistence(article.title, article.body);
  });

  test("should not create an article with empty required fields", async ({ page }) => {
    const homePage = new HomePage(page);
    const editorPage = new EditorPage(page);

    const article = invalidArticle();

    await homePage.open();

    await homePage.goToNewArticle();

    await editorPage.fillArticle(article.title, article.description, article.body, article.tags);

    await editorPage.publishButton.click();

    await editorPage.expectValidationErrors();

    // The user should still be on the editor page.
    await expect(page).toHaveURL(/\/editor/);
  });
});
