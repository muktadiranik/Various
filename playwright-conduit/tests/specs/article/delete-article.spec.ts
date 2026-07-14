import { expect, test } from '@playwright/test';

import { STORAGE } from '../../../src/constants';
import { ApiClient } from '../../../src/api/api.client';

import {
  validArticle,
} from '../../../src/fixtures/test-data';

import { HomePage } from '../../../src/pages/home.page';
import { ArticlePage } from '../../../src/pages/article.page';

test.describe('Delete Article', () => {
  test.use({
    storageState: STORAGE.AUTH,
  });

  let api: ApiClient;

  test.beforeEach(async () => {
    api = new ApiClient();

    await api.init();

    await api.login();
  });

  test.afterEach(async () => {
    await api.dispose();
  });

  test('should delete an existing article', async ({ page }) => {
    const article = validArticle();

    await api.createArticle(article);

    const homePage = new HomePage(page);
    const articlePage = new ArticlePage(page);

    await homePage.open();

    await homePage.openArticle(article.title);

    await articlePage.verifyTitle(article.title);

    await articlePage.deleteArticle();

    /**
     * User should be redirected to Home
     */
    await expect(page).toHaveURL(/\/$/);

    await homePage.waitForPageReady();

    /**
     * Verify article was deleted
     */
    await homePage.expectArticlesPresent();

    // Deleted article should no longer exist
    await homePage.expectArticleNotVisible(article.title);
  });

  test('should display not found when opening a deleted article', async ({
    page,
  }) => {
    const article = validArticle();
    const articlePage = new ArticlePage(page);
    const created = await api.createArticle(article);

    // Delete through API to simulate an already deleted article
    await api.deleteArticle(created.slug);

    await page.goto(`/article/${created.slug}`);

    await articlePage.verifyArticleNotFound();
  });
});