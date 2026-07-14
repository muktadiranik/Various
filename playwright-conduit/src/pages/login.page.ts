import { expect, Locator, Page } from '@playwright/test';
import { BasePage } from './base.page';
import { ROUTES } from '@constants/index';

export class LoginPage extends BasePage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly signInButton: Locator;
  readonly signUpLink: Locator;
  readonly errorMessages: Locator;

  constructor(page: Page) {
    super(page);

    this.emailInput = page.getByPlaceholder('Email');

    this.passwordInput = page.getByPlaceholder('Password');

    this.signInButton = page.getByRole('button', {
      name: /^sign in$/i,
    });

    this.signUpLink = page.getByRole('link', {
      name: /need an account\?/i,
    });

    this.errorMessages = page.locator('.error-messages');
  }

  /**
   * Open login page.
   */
  async open(): Promise<void> {
    await this.goto(ROUTES.LOGIN);

    await this.expectVisible(this.emailInput);
  }

  /**
   * Login with valid credentials.
   */
  async login(
    email: string,
    password: string
  ): Promise<void> {
    await this.fill(this.emailInput, email);

    await this.fill(this.passwordInput, password);

    await Promise.all([
      this.page.waitForURL(/\/$/),
      this.signInButton.click(),
    ]);
  }

  /**
   * Submit invalid credentials.
   */
  async loginExpectingFailure(
    email: string,
    password: string
  ): Promise<void> {
    await this.fill(this.emailInput, email);

    await this.fill(this.passwordInput, password);

    await this.signInButton.click();
  }

  /**
   * Clear login form.
   */
  async clearForm(): Promise<void> {
    await this.emailInput.clear();
    await this.passwordInput.clear();
  }

  /**
   * Verify login succeeded.
   */
  async expectLoginSuccess(): Promise<void> {
    await expect(this.page).toHaveURL(/\/$/);

    await expect(
      this.page.getByText('Your Feed')
    ).toBeVisible();
  }

  /**
   * Verify login failed.
   */
  async expectLoginFailure(): Promise<void> {
    await expect(this.errorMessages).toBeVisible();
  }

  /**
   * Verify Sign In button is enabled.
   */
  async expectSignInEnabled(): Promise<void> {
    await expect(this.signInButton).toBeEnabled();
  }

  /**
   * Verify Sign In button is disabled.
   */
  async expectSignInDisabled(): Promise<void> {
    await expect(this.signInButton).toBeDisabled();
  }

  /**
   * Verify validation message.
   */
  async expectValidationMessage(
    message: string
  ): Promise<void> {
    await expect(this.errorMessages).toContainText(
      message
    );
  }
}