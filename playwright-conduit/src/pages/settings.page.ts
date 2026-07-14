import { expect, Locator, Page } from "@playwright/test";
import { BasePage } from "./base.page";
import { ROUTES } from "@constants/index";
import { UserSettingsData } from "@utils/random-data";

export class SettingsPage extends BasePage {
  readonly imageUrlInput: Locator;
  readonly usernameInput: Locator;
  readonly bioTextarea: Locator;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;

  readonly updateSettingsButton: Locator;
  readonly logoutButton: Locator;

  readonly settingsForm: Locator;
  readonly validationErrors: Locator;

  constructor(page: Page) {
    super(page);

    this.settingsForm = page.locator("form");

    this.imageUrlInput = page.getByPlaceholder("URL of profile picture") || page.locator("img");

    this.usernameInput = page.getByPlaceholder("Username");

    this.bioTextarea = page.getByPlaceholder("Short bio about you");

    this.emailInput = page.getByPlaceholder("Email");

    this.passwordInput = page.getByPlaceholder("New Password");

    this.updateSettingsButton = page.getByRole("button", {
      name: /update settings/i,
    });

    this.logoutButton = page.getByRole("button", {
      name: /or click here to logout/i,
    });

    this.validationErrors = page.locator(".error-messages");
  }

  /**
   * Navigate to Settings page.
   */
  async open(): Promise<void> {
    await this.goto(ROUTES.SETTINGS);

    await this.expectVisible(this.settingsForm);
  }

  /**
   * Update user settings.
   */
  async updateSettings(settings: UserSettingsData): Promise<void> {
    await this.clearAndFill(this.imageUrlInput, settings.image);

    await this.clearAndFill(this.bioTextarea, settings.bio);

    await this.clearAndFill(this.emailInput, settings.email);

    // Username is optional in current data model
    if (settings.password) {
      await this.clearAndFill(this.passwordInput, settings.password);
    }

    await Promise.all([this.page.waitForResponse((response) => response.url().includes("/user") && response.request().method() === "PUT"), this.updateSettingsButton.click()]);

    await this.waitForPageReady();
  }

  /**
   * Submit invalid settings.
   */
  async submitInvalidSettings(settings: UserSettingsData): Promise<void> {
    await this.clearAndFill(this.emailInput, settings.email);

    await this.updateSettingsButton.click();
  }

  /**
   * Logout.
   */
  async logout(): Promise<void> {
    await this.click(this.logoutButton);

    await this.expectUrlContains("/login");
  }

  /**
   * Verify form values.
   */
  async verifySettings(settings: UserSettingsData): Promise<void> {
    await expect(this.imageUrlInput).toHaveValue(settings.image);

    await expect(this.bioTextarea).toHaveValue(settings.bio);

    await expect(this.emailInput).toHaveValue(settings.email);
  }

  /**
   * Verify email.
   */
  async verifyEmail(email: string): Promise<void> {
    await expect(this.emailInput).toHaveValue(email);
  }

  /**
   * Verify bio.
   */
  async verifyBio(bio: string): Promise<void> {
    await expect(this.bioTextarea).toHaveValue(bio);
  }

  /**
   * Verify image URL.
   */
  async verifyImage(image: string): Promise<void> {
    await expect(this.imageUrlInput).toHaveValue(image);
  }

  /**
   * Verify validation errors.
   */
  async expectValidationErrors(): Promise<void> {
    await expect(this.validationErrors).toBeVisible();
  }

  /**
   * Verify update button is enabled.
   */
  async expectUpdateButtonEnabled(): Promise<void> {
    await expect(this.updateSettingsButton).toBeEnabled();
  }

  /**
   * Verify update button is disabled.
   */
  async expectUpdateButtonDisabled(): Promise<void> {
    await expect(this.updateSettingsButton).toBeDisabled();
  }
}
