import { expect, test } from "@playwright/test";

import { STORAGE } from "../../../src/constants";
import { HomePage } from "../../../src/pages/home.page";

test.describe("Filter Articles by Tag", () => {
  test.use({
    storageState: STORAGE.AUTH,
  });

  test("should filter articles by selected tag", async ({ page }) => {
    const homePage = new HomePage(page);

    /**
     * Open the Home page.
     */
    await homePage.open();

    /**
     * Wait until the Popular Tags section is loaded.
     */
    await expect(homePage.popularTags.first()).toBeVisible();

    /**
     * Get the first available tag.
     */
    const selectedTag = (await homePage.popularTags.first().textContent())?.trim();

    expect(selectedTag).toBeTruthy();

    /**
     * Click the tag.
     */
    await homePage.popularTags.first().click();

    /**
     * Verify the selected tag becomes active.
     */
    await expect(page.locator(".feed-toggle .nav-link.active")).toHaveText(` ${selectedTag} `);

    /**
     * Verify articles are displayed.
     */
    await homePage.expectArticlesPresent();
  });

  test("should display articles when switching between tags", async ({ page }) => {
    const homePage = new HomePage(page);

    await homePage.open();

    await expect(homePage.popularTags.first()).toBeVisible();

    const tagCount = await homePage.popularTags.count();

    test.skip(tagCount < 2, "At least two tags are required for this test.");

    const firstTag = (await homePage.popularTags.nth(0).textContent())?.trim();

    const secondTag = (await homePage.popularTags.nth(1).textContent())?.trim();

    expect(firstTag).toBeTruthy();
    expect(secondTag).toBeTruthy();

    /**
     * Filter by first tag
     */
    await homePage.filterByTag(firstTag!);

    await expect(page.locator(".feed-toggle .nav-link.active")).toHaveText(` ${firstTag} `);

    await homePage.expectArticlesPresent();

    /**
     * Filter by second tag
     */
    await homePage.filterByTag(secondTag!);

    await expect(page.locator(".feed-toggle .nav-link.active")).toHaveText(` ${secondTag} `);

    await homePage.expectArticlesPresent();

  });
});
