import { expect, test } from "@playwright/test";

import { STORAGE } from "../../../src/constants";
import { invalidUserSettings, validUserSettings } from "../../../src/fixtures/test-data";

import { HomePage } from "../../../src/pages/home.page";
import { SettingsPage } from "../../../src/pages/settings.page";

test.describe("Update User Settings", () => {
  test.use({
    storageState: STORAGE.AUTH,
  });

  test("should update user settings successfully", async ({ page }) => {
    const homePage = new HomePage(page);
    const settingsPage = new SettingsPage(page);

    const settings = validUserSettings();

    await homePage.open();

    await homePage.goToSettings();

    /**
     * Wait until the Settings page is loaded.
     */
    await settingsPage.waitForPageReady();

    /**
     * Check if the username input is visible
     */
    await expect(settingsPage.usernameInput).toBeVisible();

    // Capture current values so they can be restored
    const originalSettings = {
      image: await settingsPage.imageUrlInput.inputValue(),
      username: await settingsPage.usernameInput.inputValue(),
      bio: await settingsPage.bioTextarea.inputValue(),
      email: await settingsPage.emailInput.inputValue(),
    };

    await settingsPage.updateSettings(settings);

    /**
     * Verify URL
     */
    await expect(page).toHaveURL(/profile/);

    /**
     * Refresh to ensure persistence
     */
    await page.reload();

    /**
     * Cleanup - restore original settings
     */
    await homePage.goToSettings();

    await settingsPage.updateSettings({
      image: originalSettings.image,
      username: originalSettings.username,
      bio: originalSettings.bio,
      email: originalSettings.email,
      password: "",
    });
  });

  test("should return to settings page for invalid settings", async ({ page }) => {
    const homePage = new HomePage(page);
    const settingsPage = new SettingsPage(page);

    await homePage.open();

    await homePage.goToSettings();

    await settingsPage.submitInvalidSettings(invalidUserSettings());

    await expect(page).toHaveURL(/settings/);
  });

  test("should throw error for invalid settings", async ({ page }) => {
    const homePage = new HomePage(page);
    const settingsPage = new SettingsPage(page);

    await homePage.open();

    await homePage.goToSettings();

    const [response] = await Promise.all([
      page.waitForResponse((r) => r.url().includes("/api/user") && r.request().method() === "PUT"),
      settingsPage.submitInvalidSettings(invalidUserSettings()),
    ]);

    expect(response.ok()).toBeFalsy();
    expect(response.status()).toBe(500);
  });
});
